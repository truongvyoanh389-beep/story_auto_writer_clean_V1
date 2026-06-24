from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QGroupBox,
    QFileDialog,
    QSpinBox,
    QComboBox,
    QFormLayout,
)
from PyQt6.QtCore import Qt
from app.core.prompt_value_mapper import PromptValueMapper

class InputPage(QWidget):
    def __init__(self):
        super().__init__()

        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)

        title = QLabel("Đầu vào")
        title.setStyleSheet("font-size: 24px; font-weight: 700;")
        layout.addWidget(title)

        info = QLabel(
            "Nhập tiêu đề + transcript thủ công, hoặc import file .txt. "
            "Nếu import .txt: title = tên file, transcript = nội dung file."
        )
        info.setWordWrap(True)
        layout.addWidget(info)

        settings_box = QGroupBox("Cài đặt truyện")
        settings_form = QFormLayout(settings_box)
        settings_form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        settings_form.setFormAlignment(Qt.AlignmentFlag.AlignTop)
        settings_form.setHorizontalSpacing(18)
        settings_form.setVerticalSpacing(12)
        settings_form.setSpacing(10)

        self.target_words_spin = QSpinBox()
        self.target_words_spin.setRange(3000, 50000)
        self.target_words_spin.setSingleStep(500)
        self.target_words_spin.setValue(10000)
        self.target_words_spin.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)

        self.pov_combo = QComboBox()
        self.pov_combo.addItems([
            "Ngôi thứ nhất - Tôi / của tôi",
            "Ngôi thứ hai - Bạn / của bạn",
            "Ngôi thứ ba giới hạn",
            "Ngôi thứ ba toàn tri",
        ])

        self.audience_combo = QComboBox()
        self.audience_combo.addItems([
            "Người Mỹ từ 45 tuổi trở lên",
            "Phụ nữ Mỹ từ 45 tuổi trở lên",
            "Đàn ông Mỹ từ 45 tuổi trở lên",
            "Người Mỹ cao tuổi từ 60 tuổi trở lên",
            "Khán giả Mỹ trưởng thành nói chung",
        ])

        self.tone_combo = QComboBox()
        self.tone_combo.addItems([
            "Cảm xúc chân thực",
            "Cảm xúc chậm, thấm sâu",
            "Căng thẳng, kịch tính nhưng đời thường",
            "Lặng, đau, nhiều suy ngẫm",
            "Tối ưu giữ chân người nghe audio",
        ])

        self.revenge_combo = QComboBox()
        self.revenge_combo.addItems([
            "Trung bình - sự thật được phơi bày",
            "Nhẹ - đặt ranh giới cảm xúc",
            "Cao - phơi bày công khai",
            "Hậu quả pháp lý / tài chính nhưng thực tế",
            "Đảo ngược danh tiếng trong gia đình",
        ])

        self.ending_combo = QComboBox()
        self.ending_combo.addItems([
            "Kết thúc có bài học đạo đức",
            "Công lý được thực thi",
            "Kết thúc bằng ranh giới lặng lẽ",
            "Hoà giải buồn vui lẫn lộn",
            "Không liên lạc, giữ lòng tự trọng",
        ])

        self.niche_combo = QComboBox()
        self.niche_combo.setEditable(True)
        self.niche_combo.addItems([
            "Family Betrayal",
            "Inheritance",
            "Military Female",
            "Judge Stories",
            "Rich Woman Hidden Identity",
            "Courtroom Revenge",
            "Workplace Betrayal",
            "Medical / Hospital Drama",
            "Veteran Hidden Identity",
            "Small Town Secret",
        ])
        

        settings_form.addRow("Số chữ mục tiêu", self.target_words_spin)
        settings_form.addRow("Ngôi kể", self.pov_combo)
        settings_form.addRow("Tệp khán giả", self.audience_combo)
        settings_form.addRow("Tone", self.tone_combo)
        settings_form.addRow("Mức revenge", self.revenge_combo)
        settings_form.addRow("Kiểu kết", self.ending_combo)
        settings_form.addRow("Ngách:", self.niche_combo)

        layout.addWidget(settings_box)

        box = QGroupBox("Title + Transcript")
        box_layout = QVBoxLayout(box)

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Tiêu đề viral hoặc tiêu đề gốc")

        self.transcript_input = QTextEdit()
        self.transcript_input.setPlaceholderText("Dán transcript vào đây...")
        self.transcript_input.setMinimumHeight(330)

        box_layout.addWidget(QLabel("Title"))
        box_layout.addWidget(self.title_input)
        box_layout.addWidget(QLabel("Transcript"))
        box_layout.addWidget(self.transcript_input)

        layout.addWidget(box, 1)

        btn_row = QHBoxLayout()

        self.import_txt_btn = QPushButton("Import file .txt")
        self.import_txt_btn.setObjectName("PrimaryButton")
        self.import_txt_btn.clicked.connect(self.import_txt_file)

        self.clear_btn = QPushButton("Xoá input")
        self.clear_btn.clicked.connect(self.clear)

        btn_row.addWidget(self.import_txt_btn)
        btn_row.addWidget(self.clear_btn)
        btn_row.addStretch()

        layout.addLayout(btn_row)

        self.status_label = QLabel("Chưa có input.")
        self.status_label.setStyleSheet("color: #94a3b8;")
        layout.addWidget(self.status_label)

    def import_txt_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Chọn file transcript .txt",
            "",
            "Text Files (*.txt)",
        )

        if not file_path:
            return

        path = Path(file_path)

        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            content = path.read_text(encoding="utf-8-sig")
        except Exception:
            content = path.read_text(errors="ignore")

        self.title_input.setText(path.stem.strip())
        self.transcript_input.setPlainText(content.strip())

        self.status_label.setText(
            f"Đã import: {path.name} | Title = tên file | Transcript = nội dung file"
        )

    def get_data(self) -> dict:
        return {
            "title": self.title_input.text().strip(),
            "transcript": self.transcript_input.toPlainText().strip(),
            "target_words": self.target_words_spin.value(),
            "narration_pov": self.pov_combo.currentText(),
            "target_audience": self.audience_combo.currentText(),
            "tone": self.tone_combo.currentText(),
            "revenge_intensity": self.revenge_combo.currentText(),
            "ending_type": self.ending_combo.currentText(),
            "niche": self.niche_combo.currentText().strip(),
        }

    def set_data(self, data: dict):
            self.title_input.setText(data.get("title", ""))
            self.transcript_input.setPlainText(data.get("transcript", ""))

            self.target_words_spin.setValue(int(data.get("target_words", 10000) or 10000))

            self._set_combo_text(
                self.pov_combo,
                PromptValueMapper.pov_to_vi(
                    data.get("narration_pov", "Ngôi thứ nhất - Tôi / của tôi")
                ),
            )

            self._set_combo_text(
                self.audience_combo,
                PromptValueMapper.audience_to_vi(
                    data.get("target_audience", "Người Mỹ từ 45 tuổi trở lên")
                ),
            )

            self._set_combo_text(
                self.tone_combo,
                PromptValueMapper.tone_to_vi(
                    data.get("tone", "Cảm xúc chân thực")
                ),
            )

            self._set_combo_text(
                self.revenge_combo,
                PromptValueMapper.revenge_to_vi(
                    data.get("revenge_intensity", "Trung bình - sự thật được phơi bày")
                ),
            )

            self._set_combo_text(
                self.ending_combo,
                PromptValueMapper.ending_to_vi(
                    data.get("ending_type", "Kết thúc có bài học đạo đức")
                ),
            )

            self._set_combo_text(
            self.niche_combo,
            data.get("niche", "Family Betrayal"),
        )

    def validate(self) -> tuple[bool, str]:
        title = self.title_input.text().strip()
        transcript = self.transcript_input.toPlainText().strip()

        if not title:
            return False, "Bạn cần nhập title hoặc import file .txt."

        if not transcript:
            return False, "Bạn cần nhập transcript hoặc import file .txt."

        if self.target_words_spin.value() < 3000:
            return False, "Số chữ mục tiêu quá thấp."

        return True, ""

    def clear(self):
        self.title_input.clear()
        self.transcript_input.clear()
        self.target_words_spin.setValue(10000)
        self.pov_combo.setCurrentIndex(0)
        self.audience_combo.setCurrentIndex(0)
        self.tone_combo.setCurrentIndex(0)
        self.revenge_combo.setCurrentIndex(0)
        self.ending_combo.setCurrentIndex(0)
        self.niche_combo.setCurrentIndex(0)
        self.status_label.setText("Đã xoá input.")

    @staticmethod
    def _set_combo_text(combo: QComboBox, text: str):
        index = combo.findText(text)

        if index >= 0:
            combo.setCurrentIndex(index)
        elif combo.isEditable():
            combo.setEditText(text)
        else:
            combo.setCurrentIndex(0)
