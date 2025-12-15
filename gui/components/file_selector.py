"""
File Selector Component
ファイル選択コンポーネント
"""

import tkinter as tk
from tkinter import filedialog, ttk
from pathlib import Path
from typing import Optional, Callable
from gui.styles import AppleStyle


class FileSelector(tk.Frame):
    """ファイル選択コンポーネント"""
    
    def __init__(self, parent, label_text: str, file_types: list = None, 
                 callback: Optional[Callable] = None, save_mode: bool = False, **kwargs):
        """
        初期化
        
        Args:
            parent: 親ウィジェット
            label_text: ラベルテキスト
            file_types: ファイルタイプのリスト [("説明", "*.拡張子"), ...]
            callback: ファイル選択時のコールバック関数
            save_mode: Trueの場合、保存ダイアログを使用（デフォルト: False）
        """
        super().__init__(parent, **AppleStyle.get_frame_style('surface'))
        self.callback = callback
        self.save_mode = save_mode
        
        if file_types is None:
            file_types = [("Excel files", "*.xlsx *.xlsm *.xls"), ("All files", "*.*")]
        
        self.file_types = file_types
        self.selected_file = tk.StringVar()
        
        # レイアウト
        self._create_widgets(label_text)
    
    def _create_widgets(self, label_text: str):
        """ウィジェットを作成"""
        # ラベル（空の場合は表示しない）
        if label_text:
            label = tk.Label(
                self,
                text=label_text,
                **AppleStyle.get_label_style('body')
            )
            label.pack(anchor='w', pady=(0, AppleStyle.SPACING['sm']))
        
        # ファイルパス表示とボタンのフレーム
        path_frame = tk.Frame(self, **AppleStyle.get_frame_style('surface'))
        path_frame.pack(fill='x')
        
        # エントリー（ファイルパス表示）
        self.entry = tk.Entry(
            path_frame,
            textvariable=self.selected_file,
            **AppleStyle.get_entry_style()
        )
        self.entry.pack(side='left', fill='x', expand=True, padx=(0, AppleStyle.SPACING['sm']))
        
        # 参照ボタン
        browse_btn = tk.Button(
            path_frame,
            text="参照...",
            command=self._browse_file,
            width=10,
            **AppleStyle.get_button_style('secondary')
        )
        browse_btn.pack(side='right')
    
    def _browse_file(self):
        """ファイル選択ダイアログを表示"""
        if self.save_mode:
            file_path = filedialog.asksaveasfilename(
                title="ファイルを保存",
                filetypes=self.file_types,
                defaultextension=".xlsx"
            )
        else:
            file_path = filedialog.askopenfilename(
                title="ファイルを選択",
                filetypes=self.file_types
            )
        
        if file_path:
            self.selected_file.set(file_path)
            if self.callback:
                self.callback(file_path)
    
    def get_file_path(self) -> Optional[str]:
        """選択されたファイルパスを取得"""
        path = self.selected_file.get().strip()
        return path if path else None
    
    def set_file_path(self, file_path: str):
        """ファイルパスを設定"""
        self.selected_file.set(file_path)
    
    def clear(self):
        """選択をクリア"""
        self.selected_file.set("")

