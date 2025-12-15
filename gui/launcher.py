"""
Launcher Window - 機能選択画面
複数のExcelツール機能を選択するためのランチャー
"""

import tkinter as tk
from typing import Callable, Optional
from gui.styles import AppleStyle


class LauncherWindow(tk.Toplevel):
    """機能選択ランチャーウィンドウ"""
    
    def __init__(self, parent=None):
        """
        初期化
        
        Args:
            parent: 親ウィンドウ（Noneの場合は独立ウィンドウ）
        """
        if parent is None:
            # 親がない場合は一時的なルートウィンドウを作成
            temp_root = tk.Tk()
            temp_root.withdraw()
            super().__init__(temp_root)
            self._temp_root = temp_root
        else:
            super().__init__(parent)
            self._temp_root = None
        
        self.title("Excel Tool Suite")
        self.geometry("800x600")
        self.configure(bg=AppleStyle.COLORS['background'])
        
        # ウィンドウを中央に配置
        self._center_window()
        
        # 選択された機能
        self.selected_feature: Optional[str] = None
        
        # UI作成
        self._create_widgets()
        
        # イベントハンドラ（メニューバーが設定される場合は上書きされる）
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _center_window(self):
        """ウィンドウを画面中央に配置"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def _create_widgets(self):
        """ウィジェットを作成"""
        # メインコンテナ
        main_container = tk.Frame(
            self,
            **AppleStyle.get_frame_style('background')
        )
        main_container.pack(fill='both', expand=True, padx=AppleStyle.SPACING['xl'], 
                           pady=AppleStyle.SPACING['xl'])
        
        # タイトル
        title_label = tk.Label(
            main_container,
            text="Excel Tool Suite",
            **AppleStyle.get_label_style('title')
        )
        title_label.pack(pady=(0, AppleStyle.SPACING['sm']))
        
        # サブタイトル
        subtitle_label = tk.Label(
            main_container,
            text="使用する機能を選択してください",
            **AppleStyle.get_label_style('caption')
        )
        subtitle_label.pack(pady=(0, AppleStyle.SPACING['xl']))
        
        # タイル表示セクション
        tiles_container = tk.Frame(
            main_container,
            **AppleStyle.get_frame_style('background')
        )
        tiles_container.pack(fill='both', expand=True, pady=(0, AppleStyle.SPACING['lg']))
        
        # タイルをグリッドレイアウトで配置
        # 機能1: VLOOKUP風機能
        self._create_feature_tile(
            tiles_container,
            "VLOOKUP風機能",
            "2つのExcelファイルを比較してデータをコピー",
            "📊",
            lambda: self._select_feature('vlookup'),
            row=0,
            col=0
        )
        
        # 機能2: キーワード検索機能
        self._create_feature_tile(
            tiles_container,
            "キーワード検索",
            "Excelファイルからキーワードを検索",
            "🔍",
            lambda: self._select_feature('search'),
            row=0,
            col=1
        )
        
        # 機能3: ファイル統合機能
        self._create_feature_tile(
            tiles_container,
            "ファイル統合",
            "分割されたExcelファイルを統合して1つに",
            "📋",
            lambda: self._select_feature('merge'),
            row=1,
            col=0
        )
        
        # 機能4: 読み上げ機能
        self._create_feature_tile(
            tiles_container,
            "読み上げ機能",
            "Excelファイルの内容を音声で読み上げ",
            "🔊",
            lambda: self._select_feature('reader'),
            row=1,
            col=1
        )
    
    def _create_feature_tile(self, parent, title: str, subtitle: str, 
                            icon: str, command: Callable, row: int, col: int):
        """機能タイルを作成"""
        # タイルフレーム（カード形式）
        frame_style = AppleStyle.get_frame_style('surface')
        tile_frame = tk.Frame(
            parent,
            bg=frame_style['bg'],
            relief='flat',
            borderwidth=1,
            highlightbackground=AppleStyle.COLORS['border'],
            highlightthickness=1
        )
        tile_frame.grid(
            row=row,
            column=col,
            padx=AppleStyle.SPACING['md'],
            pady=AppleStyle.SPACING['md'],
            sticky='nsew'
        )
        
        # グリッドの重みを設定
        parent.grid_columnconfigure(col, weight=1)
        parent.grid_rowconfigure(row, weight=1)
        
        # タイル全体をクリック可能にする
        tile_frame.bind('<Button-1>', lambda e: command())
        tile_frame.bind('<Enter>', lambda e: self._on_tile_enter(tile_frame))
        tile_frame.bind('<Leave>', lambda e: self._on_tile_leave(tile_frame))
        
        # タイルコンテンツ
        content_frame = tk.Frame(
            tile_frame,
            bg=AppleStyle.COLORS['surface']
        )
        content_frame.pack(fill='both', expand=True, padx=AppleStyle.SPACING['lg'], 
                          pady=AppleStyle.SPACING['lg'])
        
        # アイコンとタイトルを横並びに配置
        header_frame = tk.Frame(
            content_frame,
            bg=AppleStyle.COLORS['surface']
        )
        header_frame.pack(fill='x', pady=(0, AppleStyle.SPACING['md']))
        
        # アイコン（左側、小さめに）
        icon_label = tk.Label(
            header_frame,
            text=icon,
            font=('Segoe UI', 32),
            bg=AppleStyle.COLORS['surface'],
            fg=AppleStyle.COLORS['primary']
        )
        icon_label.pack(side='left', padx=(0, AppleStyle.SPACING['md']))
        icon_label.bind('<Button-1>', lambda e: command())
        
        # タイトル（右側、大きく）
        title_label = tk.Label(
            header_frame,
            text=title,
            font=AppleStyle.FONTS['heading'],
            bg=AppleStyle.COLORS['surface'],
            fg=AppleStyle.COLORS['text_primary'],
            anchor='w',
            justify='left'
        )
        title_label.pack(side='left', fill='x', expand=True)
        title_label.bind('<Button-1>', lambda e: command())
        
        # サブタイトル（説明文）
        subtitle_label = tk.Label(
            content_frame,
            text=subtitle,
            font=AppleStyle.FONTS['body'],
            bg=AppleStyle.COLORS['surface'],
            fg=AppleStyle.COLORS['text_primary'],
            wraplength=250,
            justify='left',
            anchor='w'
        )
        subtitle_label.pack(fill='x', pady=(0, AppleStyle.SPACING['sm']))
        subtitle_label.bind('<Button-1>', lambda e: command())
        
        # 詳細説明（小さめのテキストで追加情報）
        detail_text = self._get_feature_detail(title)
        detail_label = None
        if detail_text:
            detail_label = tk.Label(
                content_frame,
                text=detail_text,
                font=AppleStyle.FONTS['caption'],
                bg=AppleStyle.COLORS['surface'],
                fg=AppleStyle.COLORS['text_secondary'],
                wraplength=250,
                justify='left',
                anchor='w'
            )
            detail_label.pack(fill='x')
            detail_label.bind('<Button-1>', lambda e: command())
        
        # カーソルをポインターに変更
        widgets_to_bind = [tile_frame, content_frame, header_frame, icon_label, title_label, subtitle_label]
        if detail_label:
            widgets_to_bind.append(detail_label)
        for widget in widgets_to_bind:
            widget.config(cursor='hand2')
    
    def _get_feature_detail(self, title: str) -> str:
        """機能の詳細説明を取得"""
        details = {
            "VLOOKUP風機能": "複数のキーワード列でマッチングし、指定列のデータをコピーします",
            "キーワード検索": "指定フォルダ内のExcelファイルからキーワードを検索して結果を出力します",
            "ファイル統合": "フォルダ内のExcelファイルまたは複数のExcelファイルを統合して1つのファイルにします",
            "読み上げ機能": "Excelファイルの内容を音声で読み上げます（音声エンジンが必要です）"
        }
        return details.get(title, "")
    
    def _on_tile_enter(self, tile_frame):
        """タイルにマウスが入ったとき"""
        # タイルの背景色を少し明るく
        tile_frame.config(bg=AppleStyle.COLORS['background'])
        # すべての子ウィジェットの背景色を更新
        self._update_widget_bg(tile_frame, AppleStyle.COLORS['background'])
    
    def _on_tile_leave(self, tile_frame):
        """タイルからマウスが出たとき"""
        # タイルの背景色を元に戻す
        tile_frame.config(bg=AppleStyle.COLORS['surface'])
        # すべての子ウィジェットの背景色を更新
        self._update_widget_bg(tile_frame, AppleStyle.COLORS['surface'])
    
    def _update_widget_bg(self, parent, bg_color):
        """ウィジェットとその子要素の背景色を更新"""
        for widget in parent.winfo_children():
            if isinstance(widget, (tk.Frame, tk.Label)):
                widget.config(bg=bg_color)
                # 再帰的に子要素も更新
                self._update_widget_bg(widget, bg_color)
    
    def _select_feature(self, feature: str):
        """機能を選択"""
        # #region agent log
        import json
        with open(r'c:\Users\ayama\Python\ExcelTool\.cursor\debug.log', 'a', encoding='utf-8') as f:
            f.write(json.dumps({"sessionId":"debug-session","runId":"post-fix","hypothesisId":"A,B","location":"gui/launcher.py:261","message":"_select_feature entry","data":{"feature":feature,"has_temp_root":self._temp_root is not None},"timestamp":int(__import__('time').time()*1000)})+'\n')
        # #endregion
        self.selected_feature = feature
        # wait_window()を終了させるためにdestroy()を呼ぶ
        # #region agent log
        with open(r'c:\Users\ayama\Python\ExcelTool\.cursor\debug.log', 'a', encoding='utf-8') as f:
            f.write(json.dumps({"sessionId":"debug-session","runId":"post-fix","hypothesisId":"A,B","location":"gui/launcher.py:265","message":"calling destroy to end wait_window","data":{},"timestamp":int(__import__('time').time()*1000)})+'\n')
        # #endregion
        self.destroy()
        # #region agent log
        with open(r'c:\Users\ayama\Python\ExcelTool\.cursor\debug.log', 'a', encoding='utf-8') as f:
            f.write(json.dumps({"sessionId":"debug-session","runId":"post-fix","hypothesisId":"A,B","location":"gui/launcher.py:267","message":"_select_feature exit (after destroy)","data":{},"timestamp":int(__import__('time').time()*1000)})+'\n')
        # #endregion
    
    def _on_closing(self):
        """ウィンドウを閉じるときの処理"""
        self.selected_feature = None
        # wait_window()を終了させるためにdestroy()を呼ぶ
        self.destroy()

