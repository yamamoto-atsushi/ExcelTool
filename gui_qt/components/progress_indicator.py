"""
Progress Indicator Component (PyQt6版)
進捗表示コンポーネント
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore import Qt
from gui_qt.styles import AppleStyle


class ProgressIndicator(QWidget):
    """進捗表示コンポーネント（PyQt6版）"""
    
    def __init__(self, parent=None):
        """
        初期化
        
        Args:
            parent: 親ウィジェット
        """
        super().__init__(parent)
        self._create_widgets()
        self.hide()
    
    def _create_widgets(self):
        """ウィジェットを作成"""
        layout = QVBoxLayout(self)
        layout.setSpacing(AppleStyle.SPACING['md'])
        layout.setContentsMargins(0, 0, 0, 0)
        
        # プログレスバー
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)  # 不定プログレスバー
        self.progress.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid {AppleStyle.COLORS['border'].name()};
                border-radius: {AppleStyle.BORDER_RADIUS['sm']}px;
                background-color: {AppleStyle.COLORS['surface'].name()};
                height: 8px;
            }}
            QProgressBar::chunk {{
                background-color: {AppleStyle.COLORS['primary'].name()};
                border-radius: {AppleStyle.BORDER_RADIUS['sm']}px;
            }}
        """)
        layout.addWidget(self.progress)
        
        # ステータスラベル
        self.status_label = QLabel("処理中...")
        label_style = AppleStyle.get_label_style('body')
        self.status_label.setFont(label_style['font'])
        self.status_label.setStyleSheet(f"color: {label_style['color'].name()};")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
    
    def show(self, message: str = "処理中..."):
        """進捗表示を表示"""
        self.status_label.setText(message)
        self.setVisible(True)
    
    def hide(self):
        """進捗表示を非表示"""
        self.setVisible(False)
    
    def update_message(self, message: str):
        """メッセージを更新"""
        self.status_label.setText(message)

