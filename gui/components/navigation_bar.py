"""
Navigation Bar Component
ナビゲーションバーコンポーネント
機能ウィンドウに表示するナビゲーションバー
"""

import tkinter as tk
from typing import Callable, Optional
from gui.styles import AppleStyle


class NavigationBar(tk.Frame):
    """ナビゲーションバーコンポーネント"""
    
    def __init__(self, parent, on_home_click: Optional[Callable] = None, **kwargs):
        """
        初期化
        
        Args:
            parent: 親ウィジェット
            on_home_click: ホームボタンクリック時のコールバック関数
        """
        super().__init__(parent, **AppleStyle.get_frame_style('surface'))
        self.on_home_click = on_home_click
        
        self._create_widgets()
    
    def _create_widgets(self):
        """ウィジェットを作成"""
        # ナビゲーションバーのコンテナ
        nav_container = tk.Frame(self, **AppleStyle.get_frame_style('surface'))
        nav_container.pack(fill='x', padx=AppleStyle.SPACING['md'], pady=AppleStyle.SPACING['sm'])
        
        # 左側: ホームボタン
        home_btn = tk.Button(
            nav_container,
            text="🏠 ホームに戻る",
            command=self._on_home_click,
            **AppleStyle.get_button_style('secondary'),
            padx=AppleStyle.SPACING['lg'],
            pady=AppleStyle.SPACING['md']
        )
        home_btn.pack(side='left')
    
    def _on_home_click(self):
        """ホームボタンがクリックされたとき"""
        if self.on_home_click:
            self.on_home_click()

