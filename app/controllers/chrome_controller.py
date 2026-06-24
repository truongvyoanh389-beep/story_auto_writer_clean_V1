import asyncio
import inspect
import threading
import time
from concurrent.futures import Future

from playwright.async_api import async_playwright


class PlaywrightAsyncBridge:
    def __init__(self):
        self.loop = None
        self.thread = None
        self.playwright = None
        self._ready = threading.Event()

    def start(self):
        if self.thread and self.thread.is_alive():
            return

        self._ready.clear()
        self.thread = threading.Thread(
            target=self._run_loop,
            name="playwright-async-bridge",
            daemon=True,
        )
        self.thread.start()
        self._ready.wait()

    def _run_loop(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self._ready.set()
        self.loop.run_forever()

    def run(self, func):
        self.start()

        async def runner():
            result = func()
            if inspect.isawaitable(result):
                result = await result
            return result

        future: Future = asyncio.run_coroutine_threadsafe(runner(), self.loop)
        return future.result()

    def stop(self):
        if not self.loop:
            return

        try:
            if self.playwright:
                self.run(lambda: self.playwright.stop())
        finally:
            try:
                self.loop.call_soon_threadsafe(self.loop.stop)
            finally:
                self.loop = None
                self.thread = None
                self.playwright = None
                self._ready.clear()

    def reset(self):
        try:
            self.stop()
        except Exception:
            if self.loop:
                try:
                    self.loop.call_soon_threadsafe(self.loop.stop)
                except Exception:
                    pass
            self.loop = None
            self.thread = None
            self.playwright = None
            self._ready.clear()


class PlaywrightProxy:
    def __init__(self, bridge: PlaywrightAsyncBridge, target):
        object.__setattr__(self, "_bridge", bridge)
        object.__setattr__(self, "_target", target)

    def __getattr__(self, name):
        bridge = object.__getattribute__(self, "_bridge")
        target = object.__getattribute__(self, "_target")
        attr = bridge.run(lambda: getattr(target, name))

        if callable(attr):
            def method(*args, **kwargs):
                unwrapped_args = [unwrap_playwright_proxy(arg) for arg in args]
                unwrapped_kwargs = {
                    key: unwrap_playwright_proxy(value)
                    for key, value in kwargs.items()
                }
                result = bridge.run(lambda: attr(*unwrapped_args, **unwrapped_kwargs))
                return wrap_playwright_value(bridge, result)

            return method

        return wrap_playwright_value(bridge, attr)

    def __bool__(self):
        return True


def unwrap_playwright_proxy(value):
    if isinstance(value, PlaywrightProxy):
        return object.__getattribute__(value, "_target")
    return value


def wrap_playwright_value(bridge, value):
    if isinstance(value, list):
        return [wrap_playwright_value(bridge, item) for item in value]

    if isinstance(value, tuple):
        return tuple(wrap_playwright_value(bridge, item) for item in value)

    if value is None or isinstance(value, (str, int, float, bool, dict)):
        return value

    module_name = type(value).__module__
    if module_name.startswith("playwright."):
        return PlaywrightProxy(bridge, value)

    return value


class ChromeController:
    def __init__(self, port: int = 9222):
        self.port = port
        self.bridge = PlaywrightAsyncBridge()
        self.browser = None
        self.context = None
        self.page = None

    def connect(self):
        endpoint = f"http://127.0.0.1:{self.port}"

        self._ensure_playwright()
        browser = self._connect_over_cdp(endpoint)
        self.browser = wrap_playwright_value(self.bridge, browser)

        if not self.browser.contexts:
            raise RuntimeError("Không tìm thấy Chrome context. Hãy mở Chrome bằng remote debugging.")

        self.context = self.browser.contexts[0]
        self.page = self._best_page()

        return self.page

    def _ensure_playwright(self):
        last_error = None

        for _ in range(2):
            try:
                self.bridge.start()
                if not self.bridge.playwright:
                    self.bridge.playwright = self.bridge.run(lambda: async_playwright().start())
                return
            except Exception as exc:
                last_error = exc
                self.bridge.reset()
                time.sleep(1)

        raise RuntimeError(
            "Khong khoi dong duoc Playwright driver. Hay cai lai runtime bang lenh:\n"
            "env_name\\Scripts\\python.exe -m pip install -r requirements.txt\n"
            "env_name\\Scripts\\python.exe -m playwright install chromium\n"
            f"Loi goc: {last_error}"
        ) from last_error

    def _connect_over_cdp(self, endpoint: str):
        last_error = None

        for attempt in range(3):
            try:
                return self.bridge.run(
                    lambda: self.bridge.playwright.chromium.connect_over_cdp(endpoint)
                )
            except Exception as exc:
                last_error = exc
                if attempt < 2:
                    time.sleep(1)

        raise RuntimeError(
            f"Khong ket noi duoc Chrome remote debugging tai {endpoint}. "
            "Hay mo Chrome bang profile/port trong tab Profile roi thu lai. "
            f"Loi goc: {last_error}"
        ) from last_error

    def _best_page(self):
        pages = self.context.pages

        for page in pages:
            try:
                if "gemini.google.com" in page.url:
                    return page
            except Exception:
                pass

        if pages:
            return pages[-1]

        return self.context.new_page()

    def open_url(self, url: str):
        if not self.page:
            self.connect()

        for page in self.context.pages:
            try:
                if "gemini.google.com" in page.url:
                    self.page = page
                    self.page.bring_to_front()
                    self.page.goto(url, wait_until="domcontentloaded")
                    return self.page
            except Exception:
                pass

        self.page = self.context.new_page()
        self.page.goto(url, wait_until="domcontentloaded")

        return self.page

    def close(self):
        self.bridge.stop()
