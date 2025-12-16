"""
File Selector Component (PyQt6版)
ファイル選択コンポーネント
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog
from PyQt6.QtCore import Qt
from pathlib import Path
from typing import Optional, Callable
from gui_qt.styles import AppleStyle


class FileSelector(QWidget):
    """ファイル選択コンポーネント（PyQt6版）"""
    
    def __init__(self, parent=None, label_text: str = "", file_types: list = None,
                 callback: Optional[Callable] = None, save_mode: bool = False):
        """
        初期化
        
        Args:
            parent: 親ウィジェット
            label_text: ラベルテキスト
            file_types: ファイルタイプのリスト [("説明", "*.拡張子"), ...]
            callback: ファイル選択時のコールバック関数
            save_mode: Trueの場合、保存ダイアログを使用（デフォルト: False）
        """
        super().__init__(parent)
        self.callback = callback
        self.save_mode = save_mode
        
        if file_types is None:
            file_types = [("Excel files", "*.xlsx *.xlsm *.xls"), ("All files", "*.*")]
        
        self.file_types = file_types
        
        # レイアウト
        self._create_widgets(label_text)
    
    def _create_widgets(self, label_text: str):
        """ウィジェットを作成"""
        layout = QVBoxLayout(self)
        layout.setSpacing(AppleStyle.SPACING['sm'])
        layout.setContentsMargins(0, 0, 0, 0)
        
        # ラベル（空の場合は表示しない）
        if label_text:
            label = QLabel(label_text)
            label_style = AppleStyle.get_label_style('body')
            label.setFont(label_style['font'])
            label.setStyleSheet(f"color: {label_style['color'].name()};")
            layout.addWidget(label)
        
        # ファイルパス表示とボタンのフレーム
        path_layout = QHBoxLayout()
        path_layout.setSpacing(AppleStyle.SPACING['sm'])
        
        # エントリー（ファイルパス表示）
        self.entry = QLineEdit()
        self.entry.setStyleSheet(AppleStyle.get_entry_style())
        self.entry.setPlaceholderText("ファイルを選択...")
        path_layout.addWidget(self.entry)
        
        # 参照ボタン
        browse_btn = QPushButton("参照...")
        browse_btn.setStyleSheet(AppleStyle.get_button_style('secondary'))
        browse_btn.setFixedWidth(80)
        browse_btn.clicked.connect(self._browse_file)
        path_layout.addWidget(browse_btn)
        
        layout.addLayout(path_layout)
    
    def _browse_file(self):
        """ファイル選択ダイアログを表示"""
        if self.save_mode:
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "ファイルを保存",
                "",
                ";;".join([f"{desc} ({pattern})" for desc, pattern in self.file_types])
            )
        else:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "ファイルを選択",
                "",
                ";;".join([f"{desc} ({pattern})" for desc, pattern in self.file_types])
            )
        
        if file_path:
            self.entry.setText(file_path)
            if self.callback:
                self.callback(file_path)
    
    def get_file_path(self) -> Optional[str]:
        """選択されたファイルパスを取得"""
        path = self.entry.text().strip()
        return path if path else None
    
    def set_file_path(self, file_path: str):
        """ファイルパスを設定"""
        self.entry.setText(file_path)
    
    def clear(self):
        """選択をクリア"""
        self.entry.clear()

