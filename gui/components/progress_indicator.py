"""
Progress Indicator Component
進捗表示コンポーネント
"""

import tkinter as tk
from tkinter import ttk
from gui.styles import AppleStyle


class ProgressIndicator(tk.Frame):
    """進捗表示コンポーネント"""
    
    def __init__(self, parent, **kwargs):
        """
        初期化
        
        Args:
            parent: 親ウィジェット
        """
        super().__init__(parent, **AppleStyle.get_frame_style('surface'))
        self._create_widgets()
        self.hide()
    
    def _create_widgets(self):
        """ウィジェットを作成"""
        # プログレスバー
        self.progress = ttk.Progressbar(
            self,
            mode='indeterminate',
            length=300
        )
        self.progress.pack(pady=AppleStyle.SPACING['md'])
        
        # ステータスラベル
        self.status_label = tk.Label(
            self,
            text="処理中...",
            **AppleStyle.get_label_style('body')
        )
        self.status_label.pack(pady=(0, AppleStyle.SPACING['md']))
    
    def show(self, message: str = "処理中..."):
        """進捗表示を表示"""
        self.status_label.config(text=message)
        self.pack(fill='x', pady=AppleStyle.SPACING['md'])
        self.progress.start(10)
    
    def hide(self):
        """進捗表示を非表示"""
        self.progress.stop()
        self.pack_forget()
    
    def update_message(self, message: str):
        """メッセージを更新"""
        self.status_label.config(text=message)

