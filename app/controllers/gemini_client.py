import time
import pyperclip
from pathlib import Path


class GeminiClient:
    GEMINI_URL = "https://gemini.google.com/app"

    INPUT_SELECTORS = [
        'rich-textarea div[contenteditable="true"]',
        'rich-textarea [contenteditable="true"]',
        'div.ql-editor[contenteditable="true"]',
        'div[contenteditable="true"][role="textbox"]',
        'div[aria-label*="Enter a prompt"][contenteditable="true"]',
        'div[aria-label*="Nhập câu lệnh"][contenteditable="true"]',
        'div[aria-label*="prompt"][contenteditable="true"]',
        'div[contenteditable="true"]',
        'textarea[aria-label*="Enter"]',
        'textarea[aria-label*="prompt"]',
        "textarea",
        "rich-textarea",
    ]

    SEND_SELECTORS = [
        'button[aria-label*="Send"]',
        'button[aria-label*="send"]',
        'button[aria-label*="Gửi"]',
        'button:has(mat-icon[fonticon="send"])',
        'button:has(mat-icon[data-mat-icon-name="send"])',
        'button:has(mat-icon)',
    ]

    STOP_SELECTORS = [
        'button[aria-label*="Stop"]',
        'button[aria-label*="stop"]',
        'button[aria-label*="Dừng"]',
        'button[aria-label*="Cancel"]',
        'button[aria-label*="cancel"]',
        'button:has(mat-icon[fonticon="stop"])',
        'button:has(mat-icon[data-mat-icon-name="stop"])',
    ]

    RESPONSE_SELECTORS = [
        "message-content",
        "message-content div",
        'div[class*="model-response"]',
        'div[class*="response"]',
        "div.markdown",
    ]

    def __init__(self, chrome_controller, log_func=None):
        self.chrome = chrome_controller
        self.log_func = log_func

    @property
    def page(self):
        return self.chrome.page

    def log(self, message: str):
        if self.log_func:
            self.log_func(message)

    def open(self):
        self.chrome.open_url(self.GEMINI_URL)
        self.page.bring_to_front()
        self.page.wait_for_load_state("domcontentloaded", timeout=30000)
        time.sleep(5)

        # Đóng popup nếu có
        try:
            self.page.keyboard.press("Escape")
        except Exception:
            pass

    def send_prompt(self, prompt: str, wait_seconds: int = 300, expect_json: bool = False) -> str:
        if not self.page or "gemini.google.com" not in self.page.url:
            self.open()
        else:
            self.page.bring_to_front()
            time.sleep(1)

        input_box = self._find_input_box()

        if input_box is None:
            self._save_debug_files("gemini_input_not_found")
            raise RuntimeError("Không tìm thấy ô nhập Gemini.")

        before_response_count = self._response_count()

        self._paste(input_box, prompt)
        self._send()

        self.log("Đã gửi prompt. Đang chờ Gemini bắt đầu chạy...")
        generation_started = self._wait_generation_start(timeout_seconds=20)

        if not generation_started and self._response_count() <= before_response_count:
            self.log("Gemini chưa bắt đầu chạy sau khi bấm Send. Đang thử gửi lại...")
            self._send(use_keyboard_fallback=True)
            generation_started = self._wait_generation_start(timeout_seconds=20)

        if not generation_started and self._response_count() <= before_response_count:
            self._save_debug_files("gemini_prompt_not_sent")
            raise RuntimeError(
                "Prompt đã được dán vào Gemini nhưng chưa gửi được. "
                "Hãy kiểm tra nút Send có bị disable, Gemini có popup/login/captcha, "
                "hoặc prompt có quá dài không."
            )

        self.log("Đang chờ Gemini chạy xong...")
        self._wait_generation_finish(timeout_seconds=wait_seconds)

        self.log("Gemini đã dừng. Đang chờ response ổn định...")
        self._wait_response_stable(timeout_seconds=30, min_stable_seconds=4)

        response = self.read_last_response(
            before_count=before_response_count,
            expect_json=expect_json,
        )

        if not response:
            self._save_debug_files("gemini_response_not_found")
            raise RuntimeError("Không đọc được phản hồi Gemini.")

        return response

    # ------------------------------------------------------------------
    # Input
    # ------------------------------------------------------------------

    def _find_input_box(self):
        self.log("Đang tìm ô nhập Gemini...")

        # Cách 1: selector thường
        for selector in self.INPUT_SELECTORS:
            try:
                locator = self.page.locator(selector)
                count = locator.count()

                if count <= 0:
                    continue

                for i in range(count - 1, -1, -1):
                    item = locator.nth(i)

                    try:
                        if item.is_visible(timeout=1500):
                            item.click(timeout=5000)
                            self.log(f"Tìm thấy ô nhập bằng selector: {selector}")
                            return item
                    except Exception:
                        continue

            except Exception:
                continue

        # Cách 2: JS tìm tất cả contenteditable / textarea đang visible
        try:
            handle = self.page.evaluate_handle(
                """
                () => {
                    const candidates = [
                        ...document.querySelectorAll('[contenteditable="true"]'),
                        ...document.querySelectorAll('textarea'),
                        ...document.querySelectorAll('rich-textarea')
                    ];

                    function isVisible(el) {
                        const rect = el.getBoundingClientRect();
                        const style = window.getComputedStyle(el);
                        return rect.width > 20 &&
                               rect.height > 10 &&
                               style.visibility !== 'hidden' &&
                               style.display !== 'none' &&
                               style.opacity !== '0';
                    }

                    const visible = candidates.filter(isVisible);
                    return visible.length ? visible[visible.length - 1] : null;
                }
                """
            )

            element = handle.as_element()

            if element:
                element.click(timeout=5000)
                self.log("Tìm thấy ô nhập bằng JS fallback.")
                return element

        except Exception as e:
            self.log(f"JS fallback tìm input lỗi: {e}")

        # Cách 3: click vào vùng rich-textarea nếu có
        try:
            rich = self.page.locator("rich-textarea").last
            if rich.is_visible(timeout=2000):
                rich.click(timeout=5000)
                self.log("Click được rich-textarea fallback.")
                return rich
        except Exception:
            pass

        return None

    def _paste(self, input_box, prompt: str):
        try:
            input_box.click(timeout=8000)
            time.sleep(0.5)

            self.page.keyboard.press("Control+A")
            time.sleep(0.1)
            self.page.keyboard.press("Backspace")
            time.sleep(0.2)

            pyperclip.copy(prompt)
            self.page.keyboard.press("Control+V")
            time.sleep(1)
            self._dispatch_input_events()

        except Exception as e:
            self._save_debug_files("gemini_paste_failed")
            raise RuntimeError(f"Không dán được prompt vào Gemini: {e}")

    def _dispatch_input_events(self):
        try:
            self.page.evaluate(
                """
                () => {
                    const elements = [
                        document.activeElement,
                        ...document.querySelectorAll('rich-textarea [contenteditable="true"]'),
                        ...document.querySelectorAll('[contenteditable="true"]'),
                        ...document.querySelectorAll('textarea')
                    ].filter(Boolean);

                    for (const el of elements) {
                        el.dispatchEvent(new InputEvent('input', {
                            bubbles: true,
                            cancelable: true,
                            inputType: 'insertText',
                            data: ''
                        }));
                        el.dispatchEvent(new Event('change', { bubbles: true }));
                    }
                }
                """
            )
        except Exception as e:
            self.log(f"Không dispatch được input event: {e}")

    def _button_is_clickable(self, btn) -> bool:
        try:
            if not btn.is_visible(timeout=1000):
                return False
            if not btn.is_enabled(timeout=1000):
                return False

            disabled_state = btn.evaluate(
                """
                el => {
                    const disabled = el.disabled ||
                        el.getAttribute('aria-disabled') === 'true' ||
                        el.classList.contains('disabled');
                    if (disabled) {
                        return true;
                    }

                    const icon = el.querySelector('mat-icon');
                    const text = [
                        el.getAttribute('aria-label'),
                        el.getAttribute('title'),
                        el.innerText,
                        icon && icon.innerText,
                        icon && icon.getAttribute('fonticon'),
                        icon && icon.getAttribute('data-mat-icon-name')
                    ].filter(Boolean).join(' ').toLowerCase();

                    const looksLikeSend =
                        text.includes('send') ||
                        text.includes('gửi') ||
                        text.includes('gui') ||
                        text.includes('arrow_upward');

                    return !looksLikeSend;
                }
                """
            )
            return not disabled_state
        except Exception:
            return False

    def _send(self, use_keyboard_fallback: bool = False):
        self._dispatch_input_events()
        time.sleep(0.5)

        for selector in self.SEND_SELECTORS:
            try:
                locator = self.page.locator(selector)
                count = locator.count()

                if count <= 0:
                    continue

                for i in range(count - 1, -1, -1):
                    btn = locator.nth(i)

                    try:
                        if self._button_is_clickable(btn):
                            btn.click(timeout=5000)
                            self.log(f"Đã bấm Send bằng selector: {selector}")
                            time.sleep(1)
                            return
                    except Exception:
                        continue

            except Exception:
                continue

        try:
            if use_keyboard_fallback:
                self.page.keyboard.press("Control+Enter")
                time.sleep(1)

            self.page.keyboard.press("Enter")
            self.log("Không tìm thấy nút Send, đã fallback Enter.")
            time.sleep(1)
            return
        except Exception as e:
            self._save_debug_files("gemini_send_failed")
            raise RuntimeError(f"Không bấm được nút gửi Gemini: {e}")

    # ------------------------------------------------------------------
    # Wait
    # ------------------------------------------------------------------

    def _wait_generation_start(self, timeout_seconds: int = 20):
        start = time.time()

        while time.time() - start < timeout_seconds:
            if self._is_generating():
                return True
            time.sleep(0.5)

        return False

    def _wait_generation_finish(self, timeout_seconds: int = 300):
        start = time.time()
        ever_seen_stop = False

        while time.time() - start < timeout_seconds:
            generating = self._is_generating()

            if generating:
                ever_seen_stop = True
                time.sleep(1)
                continue

            if ever_seen_stop:
                return True

            time.sleep(1)

            if time.time() - start > 8:
                return False

        raise TimeoutError(f"Gemini vẫn đang chạy quá {timeout_seconds} giây.")

    def _wait_response_stable(self, timeout_seconds: int = 30, min_stable_seconds: int = 4):
        start = time.time()
        last_text = ""
        stable_since = None

        while time.time() - start < timeout_seconds:
            current_text = self._get_last_response_text()

            if current_text and current_text == last_text:
                if stable_since is None:
                    stable_since = time.time()

                if time.time() - stable_since >= min_stable_seconds:
                    return True
            else:
                stable_since = None
                last_text = current_text

            time.sleep(1)

        return False

    def _is_generating(self) -> bool:
        for selector in self.STOP_SELECTORS:
            try:
                locator = self.page.locator(selector)

                if locator.count() <= 0:
                    continue

                for i in range(locator.count()):
                    item = locator.nth(i)
                    try:
                        if item.is_visible(timeout=500):
                            return True
                    except Exception:
                        continue

            except Exception:
                continue

        return False

    # ------------------------------------------------------------------
    # Read response
    # ------------------------------------------------------------------

    def read_last_response(self, before_count: int | None = None, expect_json: bool = False) -> str:
        candidates = []

        for selector in self.RESPONSE_SELECTORS:
            try:
                locator = self.page.locator(selector)
                count = locator.count()

                if count <= 0:
                    continue

                # Ưu tiên đọc từ cuối lên
                for i in range(count - 1, -1, -1):
                    try:
                        text = locator.nth(i).inner_text(timeout=3000).strip()
                    except Exception:
                        continue

                    if not text:
                        continue

                    # Bỏ qua text quá ngắn / nút UI
                    if len(text) < 30:
                        continue

                    candidates.append(text)

            except Exception:
                continue

        if not candidates:
            return ""

        # Với step JSON: ưu tiên response có JSON object
        if expect_json:
            for text in candidates:
                if "{" in text and "}" in text and len(text) > 50:
                    return text

            return candidates[0]

        # Với step prose: không ưu tiên JSON cũ.
        # Lấy candidate đầu tiên từ cuối DOM, nhưng tránh outline JSON.
        for text in candidates:
            if self._looks_like_outline_json(text):
                continue

            return text

        # Nếu tất cả đều là outline JSON thì trả candidate đầu để worker báo lỗi rõ
        return candidates[0]


    def _looks_like_outline_json(self, text: str) -> bool:
        t = (text or "").strip()

        if not t.startswith("{"):
            return False

        markers = [
            '"outline_title"',
            '"total_chapters"',
            '"overall_arc"',
            '"chapters"',
            '"chapter_function"',
            '"continuity_plan"',
            '"realism_guardrails"',
        ]

        hit = sum(1 for marker in markers if marker in t)

        return hit >= 3

    def _response_count(self) -> int:
        max_count = 0

        for selector in self.RESPONSE_SELECTORS:
            try:
                count = self.page.locator(selector).count()
                max_count = max(max_count, count)
            except Exception:
                pass

        return max_count

    def _get_last_response_text(self) -> str:
        try:
            return self.read_last_response()
        except Exception:
            return ""

    # ------------------------------------------------------------------
    # Debug
    # ------------------------------------------------------------------

    def _save_debug_files(self, name: str):
        try:
            png_path = Path(f"{name}.png")
            html_path = Path(f"{name}.html")

            self.page.screenshot(path=str(png_path), full_page=True)

            html = self.page.content()
            html_path.write_text(html, encoding="utf-8")

            self.log(f"Đã lưu debug: {png_path}, {html_path}")

        except Exception as e:
            self.log(f"Không lưu được debug Gemini: {e}")

    def open_new_chat(self):
        """
        Mở chat Gemini mới để tránh bị kẹt context cũ.
        """

        try:
            page = self.chrome_controller.page
        except Exception:
            page = getattr(self, "page", None)

        if page is None:
            self.open()
            return

        try:
            page.goto("https://gemini.google.com/app", wait_until="domcontentloaded")
            page.wait_for_timeout(3000)
        except Exception:
            self.open()
