"""
VLOOKUP Window - VLOOKUP風機能のGUI
VLOOKUP風機能専用のウィンドウ
"""

import tkinter as tk
from tkinter import messagebox, ttk
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
import threading

from core import ExcelVLookupProcessor
from utils import ConfigManager
from gui.styles import AppleStyle
from gui.components import FileSelector, ColumnMapper, ProgressIndicator


class VLookupWindow(tk.Toplevel):
    """メインウィンドウクラス"""
    
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
        
        self.title("Excel VLOOKUP Tool")
        self.geometry("900x700")
        self.configure(bg=AppleStyle.COLORS['background'])
        
        # ウィンドウを中央に配置
        self._center_window()
        
        # 変数
        self.source_columns = []
        self.target_columns = []
        
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
            text="Excel VLOOKUP Tool",
            **AppleStyle.get_label_style('title')
        )
        title_label.pack(pady=(0, AppleStyle.SPACING['lg']))
        
        # サブタイトル
        subtitle_label = tk.Label(
            main_container,
            text="2つのExcelファイルを比較してデータをコピーします",
            **AppleStyle.get_label_style('caption')
        )
        subtitle_label.pack(pady=(0, AppleStyle.SPACING['xl']))
        
        # スクロール可能なコンテンツエリア
        canvas = tk.Canvas(
            main_container,
            bg=AppleStyle.COLORS['background'],
            highlightthickness=0
        )
        scrollbar = ttk.Scrollbar(
            main_container,
            orient="vertical",
            command=canvas.yview
        )
        scrollable_frame = tk.Frame(
            canvas,
            **AppleStyle.get_frame_style('background')
        )
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # コンテンツフレーム
        content_frame = tk.Frame(
            scrollable_frame,
            **AppleStyle.get_frame_style('background')
        )
        content_frame.pack(fill='both', expand=True, padx=AppleStyle.SPACING['md'])
        
        # ファイル選択セクション
        file_section = tk.Frame(
            content_frame,
            **AppleStyle.get_frame_style('surface')
        )
        file_section.pack(fill='x', pady=(0, AppleStyle.SPACING['lg']), 
                         padx=AppleStyle.SPACING['md'], ipady=AppleStyle.SPACING['md'])
        
        # セクションタイトルと説明
        title_frame = tk.Frame(file_section, **AppleStyle.get_frame_style('surface'))
        title_frame.pack(fill='x', padx=AppleStyle.SPACING['md'], 
                        pady=(AppleStyle.SPACING['md'], AppleStyle.SPACING['sm']))
        
        section_title = tk.Label(
            title_frame,
            text="ステップ1: ファイルを選択",
            **AppleStyle.get_label_style('heading')
        )
        section_title.pack(anchor='w')
        
        section_desc = tk.Label(
            title_frame,
            text="処理に使用するExcelファイルを選択してください",
            **AppleStyle.get_label_style('caption')
        )
        section_desc.pack(anchor='w', pady=(AppleStyle.SPACING['xs'], 0))
        
        # ソースファイル選択
        source_frame = tk.Frame(file_section, **AppleStyle.get_frame_style('surface'))
        source_frame.pack(fill='x', padx=AppleStyle.SPACING['md'], 
                         pady=(AppleStyle.SPACING['md'], AppleStyle.SPACING['sm']))
        
        source_label_frame = tk.Frame(source_frame, **AppleStyle.get_frame_style('surface'))
        source_label_frame.pack(fill='x', pady=(0, AppleStyle.SPACING['xs']))
        
        tk.Label(
            source_label_frame,
            text="① ソースファイル（参照元）",
            **AppleStyle.get_label_style('body_bold')
        ).pack(side='left')
        
        tk.Label(
            source_label_frame,
            text="データをコピーする元のファイル",
            **AppleStyle.get_label_style('caption')
        ).pack(side='left', padx=(AppleStyle.SPACING['sm'], 0))
        
        self.source_selector = FileSelector(
            source_frame,
            "",
            callback=self._on_source_file_selected
        )
        self.source_selector.pack(fill='x')
        
        # ターゲットファイル選択
        target_frame = tk.Frame(file_section, **AppleStyle.get_frame_style('surface'))
        target_frame.pack(fill='x', padx=AppleStyle.SPACING['md'], 
                         pady=(AppleStyle.SPACING['md'], AppleStyle.SPACING['sm']))
        
        target_label_frame = tk.Frame(target_frame, **AppleStyle.get_frame_style('surface'))
        target_label_frame.pack(fill='x', pady=(0, AppleStyle.SPACING['xs']))
        
        tk.Label(
            target_label_frame,
            text="② ターゲットファイル（更新対象）",
            **AppleStyle.get_label_style('body_bold')
        ).pack(side='left')
        
        tk.Label(
            target_label_frame,
            text="データを更新する対象のファイル",
            **AppleStyle.get_label_style('caption')
        ).pack(side='left', padx=(AppleStyle.SPACING['sm'], 0))
        
        self.target_selector = FileSelector(
            target_frame,
            "",
            callback=self._on_target_file_selected
        )
        self.target_selector.pack(fill='x')
        
        # 出力ファイル選択
        output_frame = tk.Frame(file_section, **AppleStyle.get_frame_style('surface'))
        output_frame.pack(fill='x', padx=AppleStyle.SPACING['md'], 
                         pady=(AppleStyle.SPACING['md'], AppleStyle.SPACING['md']))
        
        output_label_frame = tk.Frame(output_frame, **AppleStyle.get_frame_style('surface'))
        output_label_frame.pack(fill='x', pady=(0, AppleStyle.SPACING['xs']))
        
        tk.Label(
            output_label_frame,
            text="③ 出力ファイル",
            **AppleStyle.get_label_style('body_bold')
        ).pack(side='left')
        
        tk.Label(
            output_label_frame,
            text="処理結果を保存するファイル",
            **AppleStyle.get_label_style('caption')
        ).pack(side='left', padx=(AppleStyle.SPACING['sm'], 0))
        
        self.output_selector = FileSelector(
            output_frame,
            "",
            file_types=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            save_mode=True
        )
        self.output_selector.pack(fill='x')
        
        # マッピングセクション
        mapping_section = tk.Frame(
            content_frame,
            **AppleStyle.get_frame_style('surface')
        )
        mapping_section.pack(fill='both', expand=True, pady=(0, AppleStyle.SPACING['lg']),
                            padx=AppleStyle.SPACING['md'], ipady=AppleStyle.SPACING['md'])
        
        # セクションタイトルと説明
        mapping_title_frame = tk.Frame(mapping_section, **AppleStyle.get_frame_style('surface'))
        mapping_title_frame.pack(fill='x', padx=AppleStyle.SPACING['md'], 
                               pady=(AppleStyle.SPACING['md'], AppleStyle.SPACING['sm']))
        
        mapping_section_title = tk.Label(
            mapping_title_frame,
            text="ステップ2: 列のマッピングを設定",
            **AppleStyle.get_label_style('heading')
        )
        mapping_section_title.pack(anchor='w')
        
        mapping_section_desc = tk.Label(
            mapping_title_frame,
            text="どの列でマッチングし、どの列をコピーするか設定してください",
            **AppleStyle.get_label_style('caption')
        )
        mapping_section_desc.pack(anchor='w', pady=(AppleStyle.SPACING['xs'], 0))
        
        # マッチング列セクション
        match_frame = tk.Frame(mapping_section, **AppleStyle.get_frame_style('surface'))
        match_frame.pack(fill='x', padx=AppleStyle.SPACING['md'], 
                        pady=(AppleStyle.SPACING['md'], AppleStyle.SPACING['lg']))
        
        match_label_frame = tk.Frame(match_frame, **AppleStyle.get_frame_style('surface'))
        match_label_frame.pack(fill='x', pady=(0, AppleStyle.SPACING['sm']))
        
        tk.Label(
            match_label_frame,
            text="マッチング列",
            **AppleStyle.get_label_style('body_bold')
        ).pack(side='left')
        
        tk.Label(
            match_label_frame,
            text="（2つのファイルで一致させる列）",
            **AppleStyle.get_label_style('caption')
        ).pack(side='left', padx=(AppleStyle.SPACING['sm'], 0))
        
        self.match_mapper = ColumnMapper(
            match_frame,
            "",
            source_columns=[],
            target_columns=[],
            callback=self._on_mapping_changed
        )
        self.match_mapper.pack(fill='x')
        
        # コピー列セクション
        copy_frame = tk.Frame(mapping_section, **AppleStyle.get_frame_style('surface'))
        copy_frame.pack(fill='x', padx=AppleStyle.SPACING['md'], 
                       pady=(0, AppleStyle.SPACING['md']))
        
        copy_label_frame = tk.Frame(copy_frame, **AppleStyle.get_frame_style('surface'))
        copy_label_frame.pack(fill='x', pady=(0, AppleStyle.SPACING['sm']))
        
        tk.Label(
            copy_label_frame,
            text="コピー列",
            **AppleStyle.get_label_style('body_bold')
        ).pack(side='left')
        
        tk.Label(
            copy_label_frame,
            text="（ソースからターゲットにコピーする列）",
            **AppleStyle.get_label_style('caption')
        ).pack(side='left', padx=(AppleStyle.SPACING['sm'], 0))
        
        self.copy_mapper = ColumnMapper(
            copy_frame,
            "",
            source_columns=[],
            target_columns=[],
            callback=self._on_mapping_changed
        )
        self.copy_mapper.pack(fill='x')
        
        # 実行ボタンセクション
        button_section = tk.Frame(
            content_frame,
            **AppleStyle.get_frame_style('background')
        )
        button_section.pack(fill='x', pady=(AppleStyle.SPACING['lg'], AppleStyle.SPACING['lg']))
        
        # 実行ボタン
        button_style = AppleStyle.get_button_style('primary')
        button_style['font'] = ('Segoe UI', 16, 'bold')  # フォントを上書き
        self.execute_btn = tk.Button(
            button_section,
            text="▶ 処理を実行",
            command=self._execute_processing,
            **button_style,
            padx=AppleStyle.SPACING['xxl'],
            pady=AppleStyle.SPACING['lg']
        )
        self.execute_btn.pack()
        
        # 進捗表示
        self.progress = ProgressIndicator(content_frame)
        
        # 結果表示ラベル
        self.result_label = tk.Label(
            content_frame,
            text="",
            **AppleStyle.get_label_style('body')
        )
    
    def _on_source_file_selected(self, file_path: str):
        """ソースファイルが選択されたときの処理"""
        try:
            import pandas as pd
            df = pd.read_excel(file_path, sheet_name=0)
            self.source_columns = list(df.columns)
            self.match_mapper.set_source_columns(self.source_columns)
            self.copy_mapper.set_source_columns(self.source_columns)
        except Exception as e:
            messagebox.showerror("エラー", f"ファイルの読み込みに失敗しました:\n{str(e)}")
    
    def _on_target_file_selected(self, file_path: str):
        """ターゲットファイルが選択されたときの処理"""
        try:
            import pandas as pd
            df = pd.read_excel(file_path, sheet_name=0)
            self.target_columns = list(df.columns)
            # ターゲット列をマッピングに反映
            self.match_mapper.set_target_columns(self.target_columns)
            self.copy_mapper.set_target_columns(self.target_columns)
        except Exception as e:
            messagebox.showerror("エラー", f"ファイルの読み込みに失敗しました:\n{str(e)}")
    
    def _on_mapping_changed(self):
        """マッピングが変更されたときの処理"""
        # 必要に応じてバリデーションなど
        pass
    
    def _validate_inputs(self) -> Tuple[bool, Optional[str]]:
        """入力の検証"""
        source_file = self.source_selector.get_file_path()
        target_file = self.target_selector.get_file_path()
        output_file = self.output_selector.get_file_path()
        
        if not source_file:
            return False, "ソースファイルを選択してください"
        if not target_file:
            return False, "ターゲットファイルを選択してください"
        if not output_file:
            return False, "出力ファイルを指定してください"
        
        if not Path(source_file).exists():
            return False, "ソースファイルが見つかりません"
        if not Path(target_file).exists():
            return False, "ターゲットファイルが見つかりません"
        
        match_mappings = self.match_mapper.get_mappings()
        copy_mappings = self.copy_mapper.get_mappings()
        
        if not match_mappings:
            return False, "マッチング列を少なくとも1つ設定してください"
        if not copy_mappings:
            return False, "コピー列を少なくとも1つ設定してください"
        
        return True, None
    
    def _execute_processing(self):
        """処理を実行"""
        # バリデーション
        is_valid, error_message = self._validate_inputs()
        if not is_valid:
            messagebox.showerror("入力エラー", error_message)
            return
        
        # UIを無効化
        self.execute_btn.config(state='disabled')
        self.progress.show("処理を開始しています...")
        
        # 別スレッドで処理を実行
        thread = threading.Thread(target=self._process_in_thread)
        thread.daemon = True
        thread.start()
    
    def _process_in_thread(self):
        """別スレッドで処理を実行"""
        try:
            # 設定を作成
            config = {
                'source_file': self.source_selector.get_file_path(),
                'target_file': self.target_selector.get_file_path(),
                'output_file': self.output_selector.get_file_path(),
                'source_sheet': 0,
                'target_sheet': 0,
                'match_columns': self.match_mapper.get_mappings(),
                'copy_columns': self.copy_mapper.get_mappings(),
            }
            
            # プロセッサーを作成して実行
            processor = ExcelVLookupProcessor(config)
            
            self.after(0, lambda: self.progress.update_message("ファイルを読み込んでいます..."))
            result = processor.execute()
            
            # 結果を表示
            self.after(0, lambda: self._show_result(result))
            
        except Exception as e:
            self.after(0, lambda: self._show_error(str(e)))
    
    def _show_result(self, result: Dict[str, Any]):
        """結果を表示"""
        self.progress.hide()
        self.execute_btn.config(state='normal')
        
        if result['success']:
            message = (
                f"処理が完了しました！\n\n"
                f"マッチした行数: {result['matched_count']}\n"
                f"ソースファイル行数: {result['source_rows']}\n"
                f"ターゲットファイル行数: {result['target_rows']}\n"
                f"出力ファイル: {result['output_file']}"
            )
            messagebox.showinfo("成功", message)
        else:
            messagebox.showerror("エラー", result['message'])
    
    def _show_error(self, error_message: str):
        """エラーを表示"""
        self.progress.hide()
        self.execute_btn.config(state='normal')
        messagebox.showerror("エラー", f"処理中にエラーが発生しました:\n{error_message}")
    
    def _on_closing(self):
        """ウィンドウを閉じるときの処理"""
        self.destroy()

