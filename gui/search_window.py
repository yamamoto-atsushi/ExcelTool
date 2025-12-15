"""
Search Window - キーワード検索機能のGUI
Excelファイルキーワード検索機能専用のウィンドウ
"""

import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
import threading

from gui.styles import AppleStyle
from gui.components import ProgressIndicator


class SearchWindow(tk.Toplevel):
    """キーワード検索ウィンドウ"""
    
    def __init__(self, parent=None):
        """
        初期化
        
        Args:
            parent: 親ウィンドウ（Noneの場合は独立ウィンドウ）
        """
        if parent is None:
            super().__init__()
        else:
            super().__init__(parent)
        
        self.title("Excel キーワード検索")
        self.geometry("700x600")
        self.configure(bg=AppleStyle.COLORS['background'])
        
        # ウィンドウを中央に配置
        self._center_window()
        
        # UI作成
        self._create_widgets()
        
        # イベントハンドラ
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
            text="Excel キーワード検索",
            **AppleStyle.get_label_style('title')
        )
        title_label.pack(pady=(0, AppleStyle.SPACING['lg']))
        
        # サブタイトル
        subtitle_label = tk.Label(
            main_container,
            text="指定フォルダ内のExcelファイルからキーワードを検索します",
            **AppleStyle.get_label_style('caption')
        )
        subtitle_label.pack(pady=(0, AppleStyle.SPACING['xl']))
        
        # 設定セクション
        settings_section = tk.Frame(
            main_container,
            **AppleStyle.get_frame_style('surface')
        )
        settings_section.pack(fill='x', pady=(0, AppleStyle.SPACING['lg']), 
                             padx=AppleStyle.SPACING['md'], ipady=AppleStyle.SPACING['md'])
        
        # 検索パス
        path_frame = tk.Frame(settings_section, **AppleStyle.get_frame_style('surface'))
        path_frame.pack(fill='x', padx=AppleStyle.SPACING['md'], 
                       pady=(AppleStyle.SPACING['md'], AppleStyle.SPACING['sm']))
        
        tk.Label(
            path_frame,
            text="検索フォルダ:",
            **AppleStyle.get_label_style('body_bold')
        ).pack(anchor='w', pady=(0, AppleStyle.SPACING['xs']))
        
        path_input_frame = tk.Frame(path_frame, **AppleStyle.get_frame_style('surface'))
        path_input_frame.pack(fill='x')
        
        self.search_path_var = tk.StringVar()
        path_entry = tk.Entry(
            path_input_frame,
            textvariable=self.search_path_var,
            **AppleStyle.get_entry_style()
        )
        path_entry.pack(side='left', fill='x', expand=True, 
                       padx=(0, AppleStyle.SPACING['sm']))
        
        tk.Button(
            path_input_frame,
            text="参照...",
            command=self._browse_folder,
            **AppleStyle.get_button_style('secondary')
        ).pack(side='right')
        
        # キーワード
        keywords_frame = tk.Frame(settings_section, **AppleStyle.get_frame_style('surface'))
        keywords_frame.pack(fill='x', padx=AppleStyle.SPACING['md'], 
                           pady=(AppleStyle.SPACING['md'], AppleStyle.SPACING['sm']))
        
        tk.Label(
            keywords_frame,
            text="検索キーワード（1行に1つ）:",
            **AppleStyle.get_label_style('body_bold')
        ).pack(anchor='w', pady=(0, AppleStyle.SPACING['xs']))
        
        self.keywords_text = tk.Text(
            keywords_frame,
            height=6,
            wrap=tk.WORD,
            **AppleStyle.get_entry_style()
        )
        self.keywords_text.pack(fill='both', expand=True)
        
        # 出力ファイル
        output_frame = tk.Frame(settings_section, **AppleStyle.get_frame_style('surface'))
        output_frame.pack(fill='x', padx=AppleStyle.SPACING['md'], 
                        pady=(AppleStyle.SPACING['md'], AppleStyle.SPACING['md']))
        
        tk.Label(
            output_frame,
            text="出力ファイル:",
            **AppleStyle.get_label_style('body_bold')
        ).pack(anchor='w', pady=(0, AppleStyle.SPACING['xs']))
        
        output_input_frame = tk.Frame(output_frame, **AppleStyle.get_frame_style('surface'))
        output_input_frame.pack(fill='x')
        
        self.output_path_var = tk.StringVar()
        output_entry = tk.Entry(
            output_input_frame,
            textvariable=self.output_path_var,
            **AppleStyle.get_entry_style()
        )
        output_entry.pack(side='left', fill='x', expand=True, 
                         padx=(0, AppleStyle.SPACING['sm']))
        
        tk.Button(
            output_input_frame,
            text="参照...",
            command=self._browse_output_file,
            **AppleStyle.get_button_style('secondary')
        ).pack(side='right')
        
        # 実行ボタン
        button_section = tk.Frame(
            main_container,
            **AppleStyle.get_frame_style('background')
        )
        button_section.pack(fill='x', pady=(AppleStyle.SPACING['lg'], 0))
        
        button_style = AppleStyle.get_button_style('primary')
        button_style['font'] = ('Segoe UI', 16, 'bold')
        self.execute_btn = tk.Button(
            button_section,
            text="▶ 検索を開始",
            command=self._execute_search,
            **button_style,
            padx=AppleStyle.SPACING['xxl'],
            pady=AppleStyle.SPACING['lg']
        )
        self.execute_btn.pack()
        
        # 進捗表示
        self.progress = ProgressIndicator(main_container)
    
    def _browse_folder(self):
        """フォルダ選択ダイアログを表示"""
        folder_path = filedialog.askdirectory(title="検索フォルダを選択")
        if folder_path:
            self.search_path_var.set(folder_path)
    
    def _browse_output_file(self):
        """出力ファイル選択ダイアログを表示"""
        file_path = filedialog.asksaveasfilename(
            title="出力ファイルを保存",
            filetypes=[("Excel files", "*.xlsx"), ("CSV files", "*.csv"), ("All files", "*.*")],
            defaultextension=".xlsx"
        )
        if file_path:
            self.output_path_var.set(file_path)
    
    def _validate_inputs(self) -> Tuple[bool, Optional[str]]:
        """入力の検証"""
        search_path = self.search_path_var.get().strip()
        keywords_text = self.keywords_text.get("1.0", tk.END).strip()
        output_path = self.output_path_var.get().strip()
        
        if not search_path:
            return False, "検索フォルダを指定してください"
        if not Path(search_path).exists():
            return False, "検索フォルダが見つかりません"
        if not keywords_text:
            return False, "検索キーワードを入力してください"
        if not output_path:
            return False, "出力ファイルを指定してください"
        
        return True, None
    
    def _execute_search(self):
        """検索を実行"""
        # バリデーション
        is_valid, error_message = self._validate_inputs()
        if not is_valid:
            messagebox.showerror("入力エラー", error_message)
            return
        
        # UIを無効化
        self.execute_btn.config(state='disabled')
        self.progress.show("検索を開始しています...")
        
        # 別スレッドで処理を実行
        thread = threading.Thread(target=self._process_in_thread)
        thread.daemon = True
        thread.start()
    
    def _process_in_thread(self):
        """別スレッドで処理を実行"""
        try:
            # ExcelSearchToolをインポート
            import sys
            from pathlib import Path
            project_root = Path(__file__).parent.parent
            sys.path.insert(0, str(project_root))
            
            from excel_search import ExcelSearchTool
            
            # 設定を作成
            keywords = [k.strip() for k in self.keywords_text.get("1.0", tk.END).strip().split('\n') if k.strip()]
            
            config = {
                'search_path': self.search_path_var.get().strip(),
                'keywords': keywords,
                'output_file': self.output_path_var.get().strip(),
                'recursive': True,
                'max_workers': 4,
                'case_sensitive': False,
            }
            
            # ツール実行
            tool = ExcelSearchTool(config)
            
            self.after(0, lambda: self.progress.update_message("ファイルを検索しています..."))
            tool.execute()
            
            # 結果を表示
            self.after(0, lambda: self._show_result())
            
        except Exception as e:
            self.after(0, lambda: self._show_error(str(e)))
    
    def _show_result(self):
        """結果を表示"""
        self.progress.hide()
        self.execute_btn.config(state='normal')
        messagebox.showinfo("成功", f"検索が完了しました。\n結果を保存しました: {self.output_path_var.get()}")
    
    def _show_error(self, error_message: str):
        """エラーを表示"""
        self.progress.hide()
        self.execute_btn.config(state='normal')
        messagebox.showerror("エラー", f"処理中にエラーが発生しました:\n{error_message}")
    
    def _on_closing(self):
        """ウィンドウを閉じるときの処理"""
        self.destroy()

