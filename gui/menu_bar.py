"""
Menu Bar - メニューバーコンポーネント
各機能にアクセスするためのメニューバー
"""

import tkinter as tk
from typing import Callable, Optional
from .styles import AppleStyle


class MenuBar:
    """メニューバークラス"""
    
    def __init__(self, parent, on_feature_select: Optional[Callable] = None):
        """
        初期化
        
        Args:
            parent: 親ウィンドウ（TkまたはToplevel）
            on_feature_select: 機能選択時のコールバック関数 (feature_name: str) -> None
        """
        self.parent = parent
        self.on_feature_select = on_feature_select
        self.menubar = tk.Menu(parent)
        
        # Toplevelの場合は親ウィンドウにメニューを設定
        if isinstance(parent, tk.Toplevel):
            # Toplevelの場合は親のルートウィンドウにメニューを設定
            root = parent.nametowidget(parent.winfo_parent()) if parent.winfo_parent() else parent
            while not isinstance(root, tk.Tk):
                root = root.nametowidget(root.winfo_parent()) if root.winfo_parent() else root
            root.config(menu=self.menubar)
        else:
            parent.config(menu=self.menubar)
        
        self._create_menus()
    
    def _create_menus(self):
        """メニューを作成"""
        # ファイルメニュー
        file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="ファイル", menu=file_menu)
        file_menu.add_command(label="終了", command=self._exit_app)
        
        # 機能メニュー
        feature_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="機能", menu=feature_menu)
        
        feature_menu.add_command(
            label="VLOOKUP風機能",
            command=lambda: self._select_feature('vlookup'),
            accelerator="Ctrl+V"
        )
        feature_menu.add_command(
            label="キーワード検索",
            command=lambda: self._select_feature('search'),
            accelerator="Ctrl+S"
        )
        feature_menu.add_command(
            label="ファイル統合",
            command=lambda: self._select_feature('merge'),
            accelerator="Ctrl+M"
        )
        feature_menu.add_command(
            label="読み上げ機能",
            command=lambda: self._select_feature('reader'),
            accelerator="Ctrl+R"
        )
        
        feature_menu.add_separator()
        feature_menu.add_command(
            label="機能選択画面を表示",
            command=lambda: self._select_feature('launcher'),
            accelerator="Ctrl+L"
        )
        
        # ヘルプメニュー
        help_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="ヘルプ", menu=help_menu)
        help_menu.add_command(label="使い方", command=self._show_help)
        help_menu.add_command(label="バージョン情報", command=self._show_about)
        
        # キーバインド
        self.parent.bind('<Control-v>', lambda e: self._select_feature('vlookup'))
        self.parent.bind('<Control-s>', lambda e: self._select_feature('search'))
        self.parent.bind('<Control-m>', lambda e: self._select_feature('merge'))
        self.parent.bind('<Control-r>', lambda e: self._select_feature('reader'))
        self.parent.bind('<Control-l>', lambda e: self._select_feature('launcher'))
    
    def _select_feature(self, feature: str):
        """機能を選択"""
        if self.on_feature_select:
            self.on_feature_select(feature)
    
    def _exit_app(self):
        """アプリケーションを終了"""
        self.parent.quit()
        self.parent.destroy()
    
    def _show_help(self):
        """ヘルプを表示"""
        import tkinter.messagebox as messagebox
        help_text = """Excel Tool Suite - 使い方

【VLOOKUP風機能】
2つのExcelファイルを比較して、キーワード列でマッチングし、
指定列のデータをコピーします。

【キーワード検索】
指定フォルダ内のExcelファイルからキーワードを検索し、
結果をExcelまたはCSV形式で出力します。

【ファイル統合】
分割されたExcelファイルを統合して1つのファイルにします。
フォルダまたは複数のファイルを指定できます。

【読み上げ機能】
Excelファイルの内容を音声で読み上げます。
（コマンドライン版のみ対応）

ショートカットキー:
- Ctrl+V: VLOOKUP風機能
- Ctrl+S: キーワード検索
- Ctrl+M: ファイル統合
- Ctrl+R: 読み上げ機能
- Ctrl+L: 機能選択画面
"""
        messagebox.showinfo("使い方", help_text)
    
    def _show_about(self):
        """バージョン情報を表示"""
        import tkinter.messagebox as messagebox
        about_text = """Excel Tool Suite
Version 1.0.1

Excel操作のための便利ツール集
- VLOOKUP風機能
- キーワード検索機能
- ファイル統合機能
- 読み上げ機能

Apple UI/UXに準拠した親しみやすいGUIを提供
"""
        messagebox.showinfo("バージョン情報", about_text)

