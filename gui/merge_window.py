"""
Merge Window - Excelファイル統合機能のGUI
分割されたExcelファイルを統合する機能専用のウィンドウ
"""

import tkinter as tk
from tkinter import messagebox, ttk, filedialog, Radiobutton
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
import threading

from gui.styles import AppleStyle
from gui.components import ProgressIndicator


class MergeWindow(tk.Toplevel):
    """Excelファイル統合ウィンドウ"""
    
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
        
        self.title("Excel ファイル統合")
        self.geometry("700x650")
        self.configure(bg=AppleStyle.COLORS['background'])
        
        # ウィンドウを中央に配置
        self._center_window()
        
        # 変数
        self.input_path_var = tk.StringVar()
        self.output_path_var = tk.StringVar()
        self.input_type_var = tk.StringVar(value='folder')  # 'file' or 'folder'
        self.sheet_name_var = tk.StringVar(value='0')
        self.recursive_var = tk.BooleanVar(value=False)
        self.include_header_var = tk.BooleanVar(value=True)
        
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
            text="Excel ファイル統合",
            **AppleStyle.get_label_style('title')
        )
        title_label.pack(pady=(0, AppleStyle.SPACING['lg']))
        
        # サブタイトル
        subtitle_label = tk.Label(
            main_container,
            text="分割されたExcelファイルを統合して1つのファイルにします",
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
        
        # 入力タイプ選択
        input_type_frame = tk.Frame(settings_section, **AppleStyle.get_frame_style('surface'))
        input_type_frame.pack(fill='x', padx=AppleStyle.SPACING['md'], 
                             pady=(AppleStyle.SPACING['md'], AppleStyle.SPACING['sm']))
        
        tk.Label(
            input_type_frame,
            text="入力タイプ:",
            **AppleStyle.get_label_style('body_bold', bg_color=AppleStyle.COLORS['surface'])
        ).pack(anchor='w', pady=(0, AppleStyle.SPACING['xs']))
        
        type_select_frame = tk.Frame(input_type_frame, **AppleStyle.get_frame_style('surface'))
        type_select_frame.pack(fill='x')
        
        label_style = AppleStyle.get_label_style('body', bg_color=AppleStyle.COLORS['surface'])
        Radiobutton(
            type_select_frame,
            text="フォルダを指定",
            variable=self.input_type_var,
            value='folder',
            command=self._on_input_type_changed,
            font=label_style.get('font'),
            fg=label_style.get('fg'),
            bg=label_style.get('bg')
        ).pack(side='left', padx=(0, AppleStyle.SPACING['md']))
        
        Radiobutton(
            type_select_frame,
            text="ファイルを指定（複数選択可）",
            variable=self.input_type_var,
            value='file',
            command=self._on_input_type_changed,
            font=label_style.get('font'),
            fg=label_style.get('fg'),
            bg=label_style.get('bg')
        ).pack(side='left')
        
        # 入力パス
        input_path_frame = tk.Frame(settings_section, **AppleStyle.get_frame_style('surface'))
        input_path_frame.pack(fill='x', padx=AppleStyle.SPACING['md'], 
                            pady=(AppleStyle.SPACING['md'], AppleStyle.SPACING['sm']))
        
        tk.Label(
            input_path_frame,
            text="入力パス:",
            **AppleStyle.get_label_style('body_bold', bg_color=AppleStyle.COLORS['surface'])
        ).pack(anchor='w', pady=(0, AppleStyle.SPACING['xs']))
        
        tk.Label(
            input_path_frame,
            text="統合するExcelファイルを含むフォルダ、または統合するExcelファイルを選択してください",
            **AppleStyle.get_label_style('caption', bg_color=AppleStyle.COLORS['surface'])
        ).pack(anchor='w', pady=(0, AppleStyle.SPACING['xs']))
        
        input_path_input_frame = tk.Frame(input_path_frame, **AppleStyle.get_frame_style('surface'))
        input_path_input_frame.pack(fill='x')
        
        self.input_path_entry = tk.Entry(
            input_path_input_frame,
            textvariable=self.input_path_var,
            **AppleStyle.get_entry_style()
        )
        self.input_path_entry.pack(side='left', fill='x', expand=True, 
                                   padx=(0, AppleStyle.SPACING['sm']))
        
        self.browse_btn = tk.Button(
            input_path_input_frame,
            text="参照...",
            command=self._browse_input_path,
            **AppleStyle.get_button_style('secondary')
        )
        self.browse_btn.pack(side='right')
        
        # シート名
        sheet_frame = tk.Frame(settings_section, **AppleStyle.get_frame_style('surface'))
        sheet_frame.pack(fill='x', padx=AppleStyle.SPACING['md'], 
                        pady=(AppleStyle.SPACING['md'], AppleStyle.SPACING['sm']))
        
        tk.Label(
            sheet_frame,
            text="シート名（番号または名前）:",
            **AppleStyle.get_label_style('body_bold', bg_color=AppleStyle.COLORS['surface'])
        ).pack(anchor='w', pady=(0, AppleStyle.SPACING['xs']))
        
        tk.Label(
            sheet_frame,
            text="統合するシートを指定します（デフォルト: 0 = 最初のシート）",
            **AppleStyle.get_label_style('caption', bg_color=AppleStyle.COLORS['surface'])
        ).pack(anchor='w', pady=(0, AppleStyle.SPACING['xs']))
        
        sheet_entry = tk.Entry(
            sheet_frame,
            textvariable=self.sheet_name_var,
            **AppleStyle.get_entry_style()
        )
        sheet_entry.pack(fill='x')
        
        # オプション
        options_frame = tk.Frame(settings_section, **AppleStyle.get_frame_style('surface'))
        options_frame.pack(fill='x', padx=AppleStyle.SPACING['md'], 
                          pady=(AppleStyle.SPACING['md'], AppleStyle.SPACING['sm']))
        
        tk.Label(
            options_frame,
            text="オプション:",
            **AppleStyle.get_label_style('body_bold', bg_color=AppleStyle.COLORS['surface'])
        ).pack(anchor='w', pady=(0, AppleStyle.SPACING['xs']))
        
        label_style = AppleStyle.get_label_style('body', bg_color=AppleStyle.COLORS['surface'])
        recursive_check = tk.Checkbutton(
            options_frame,
            text="サブフォルダも検索する",
            variable=self.recursive_var,
            font=label_style.get('font'),
            fg=label_style.get('fg'),
            bg=label_style.get('bg')
        )
        recursive_check.pack(anchor='w')
        
        header_check = tk.Checkbutton(
            options_frame,
            text="すべてのファイルでヘッダーを含める（最初のファイルのみでない）",
            variable=self.include_header_var,
            font=label_style.get('font'),
            fg=label_style.get('fg'),
            bg=label_style.get('bg')
        )
        header_check.pack(anchor='w')
        
        # 出力ファイル
        output_frame = tk.Frame(settings_section, **AppleStyle.get_frame_style('surface'))
        output_frame.pack(fill='x', padx=AppleStyle.SPACING['md'], 
                        pady=(AppleStyle.SPACING['md'], AppleStyle.SPACING['md']))
        
        tk.Label(
            output_frame,
            text="出力ファイル:",
            **AppleStyle.get_label_style('body_bold', bg_color=AppleStyle.COLORS['surface'])
        ).pack(anchor='w', pady=(0, AppleStyle.SPACING['xs']))
        
        output_input_frame = tk.Frame(output_frame, **AppleStyle.get_frame_style('surface'))
        output_input_frame.pack(fill='x')
        
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
            text="▶ 統合を実行",
            command=self._execute_merge,
            **button_style,
            padx=AppleStyle.SPACING['xxl'],
            pady=AppleStyle.SPACING['lg']
        )
        self.execute_btn.pack()
        
        # 進捗表示
        self.progress = ProgressIndicator(main_container)
    
    def _on_input_type_changed(self):
        """入力タイプが変更されたときの処理"""
        # 入力パスをクリア
        self.input_path_var.set("")
    
    def _browse_input_path(self):
        """入力パス選択ダイアログを表示"""
        input_type = self.input_type_var.get()
        
        if input_type == 'folder':
            # フォルダ選択
            folder_path = filedialog.askdirectory(title="統合するExcelファイルを含むフォルダを選択")
            if folder_path:
                self.input_path_var.set(folder_path)
        else:
            # ファイル選択（複数選択可）
            file_paths = filedialog.askopenfilenames(
                title="統合するExcelファイルを選択",
                filetypes=[("Excel files", "*.xlsx *.xlsm *.xls"), ("All files", "*.*")]
            )
            if file_paths:
                # 複数ファイルのパスをセミコロンで区切って保存
                self.input_path_var.set(';'.join(file_paths))
    
    def _browse_output_file(self):
        """出力ファイル選択ダイアログを表示"""
        file_path = filedialog.asksaveasfilename(
            title="統合結果を保存",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            defaultextension=".xlsx"
        )
        if file_path:
            self.output_path_var.set(file_path)
    
    def _validate_inputs(self) -> Tuple[bool, Optional[str]]:
        """入力の検証"""
        input_path = self.input_path_var.get().strip()
        output_path = self.output_path_var.get().strip()
        
        if not input_path:
            return False, "入力パスを指定してください"
        
        input_type = self.input_type_var.get()
        if input_type == 'folder':
            if not Path(input_path).exists():
                return False, "入力フォルダが見つかりません"
            if not Path(input_path).is_dir():
                return False, "入力パスはフォルダである必要があります"
        else:
            # ファイルが指定されている場合、セミコロンで区切られた複数パスをチェック
            file_paths = [p.strip() for p in input_path.split(';') if p.strip()]
            if not file_paths:
                return False, "入力ファイルを指定してください"
            for file_path in file_paths:
                if not Path(file_path).exists():
                    return False, f"入力ファイルが見つかりません: {file_path}"
                if not Path(file_path).is_file():
                    return False, f"入力パスはファイルである必要があります: {file_path}"
        
        if not output_path:
            return False, "出力ファイルを指定してください"
        
        # 出力ファイルのディレクトリが存在するかチェック
        output_dir = Path(output_path).parent
        if output_dir and not output_dir.exists():
            return False, "出力ファイルのディレクトリが見つかりません"
        
        return True, None
    
    def _execute_merge(self):
        """統合を実行"""
        # バリデーション
        is_valid, error_message = self._validate_inputs()
        if not is_valid:
            messagebox.showerror("入力エラー", error_message)
            return
        
        # UIを無効化
        self.execute_btn.config(state='disabled')
        self.progress.show("統合を開始しています...")
        
        # 別スレッドで処理を実行
        thread = threading.Thread(target=self._process_in_thread)
        thread.daemon = True
        thread.start()
    
    def _process_in_thread(self):
        """別スレッドで処理を実行"""
        try:
            # ExcelMergerをインポート
            import sys
            from pathlib import Path
            project_root = Path(__file__).parent.parent
            sys.path.insert(0, str(project_root))
            
            from core.excel_merger import ExcelMerger
            
            # 設定を作成
            input_path = self.input_path_var.get().strip()
            input_type = self.input_type_var.get()
            
            # シート名の処理
            sheet_name = self.sheet_name_var.get().strip()
            try:
                # 数値に変換できる場合は数値として使用
                sheet_name = int(sheet_name)
            except ValueError:
                # 数値でない場合は文字列として使用
                pass
            
            config = {}
            
            # ファイルが複数選択されている場合は、ファイルリストを使用
            if input_type == 'file':
                file_paths = [p.strip() for p in input_path.split(';') if p.strip()]
                if file_paths:
                    config['input_files'] = file_paths
                else:
                    raise ValueError("入力ファイルが指定されていません")
            else:
                # フォルダが指定されている場合
                config['input_path'] = input_path
            
            config.update({
                'output_file': self.output_path_var.get().strip(),
                'sheet_name': sheet_name,
                'recursive': self.recursive_var.get(),
                'include_header': self.include_header_var.get(),
            })
            
            # ツール実行
            merger = ExcelMerger(config)
            
            self.after(0, lambda: self.progress.update_message("Excelファイルを読み込んでいます..."))
            result = merger.merge()
            
            # 結果を表示
            self.after(0, lambda: self._show_result(result))
            
        except Exception as e:
            self.after(0, lambda: self._show_error(str(e)))
    
    def _show_result(self, result: Dict[str, Any]):
        """結果を表示"""
        self.progress.hide()
        self.execute_btn.config(state='normal')
        
        if result['success']:
            messagebox.showinfo(
                "成功", 
                f"統合が完了しました。\n\n"
                f"処理ファイル数: {result['files_processed']}個\n"
                f"総行数: {result['total_rows']}行\n"
                f"出力ファイル: {result['output_file']}"
            )
        else:
            messagebox.showerror("エラー", f"統合処理中にエラーが発生しました:\n{result['message']}")
    
    def _show_error(self, error_message: str):
        """エラーを表示"""
        self.progress.hide()
        self.execute_btn.config(state='normal')
        messagebox.showerror("エラー", f"処理中にエラーが発生しました:\n{error_message}")
    
    def _on_closing(self):
        """ウィンドウを閉じるときの処理"""
        self.destroy()

