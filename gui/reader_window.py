"""
Reader Window - Excel読み上げ機能のGUI
Excelファイルの内容を音声で読み上げる機能専用のウィンドウ
"""

import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
import threading

import pandas as pd
from core import ExcelReader
from gui.styles import AppleStyle
from gui.components import FileSelector, ProgressIndicator


class ReaderWindow(tk.Toplevel):
    """Excel読み上げウィンドウ"""
    
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
        
        self.title("Excel 読み上げ機能")
        self.geometry("700x750")
        self.configure(bg=AppleStyle.COLORS['background'])
        
        # ウィンドウを中央に配置
        self._center_window()
        
        # 変数
        self.reader: Optional[ExcelReader] = None
        self.reading_thread: Optional[threading.Thread] = None
        self.current_row = 0
        self.total_rows = 0
        
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
            text="Excel 読み上げ機能",
            **AppleStyle.get_label_style('title')
        )
        title_label.pack(pady=(0, AppleStyle.SPACING['lg']))
        
        # サブタイトル
        subtitle_label = tk.Label(
            main_container,
            text="Excelファイルの内容を音声で読み上げます",
            **AppleStyle.get_label_style('caption')
        )
        subtitle_label.pack(pady=(0, AppleStyle.SPACING['xl']))
        
        # 設定セクション
        settings_section = tk.Frame(
            main_container,
            **AppleStyle.get_frame_style('card')
        )
        settings_section.pack(fill='x', pady=(0, AppleStyle.SPACING['lg']), 
                             padx=AppleStyle.SPACING['md'], ipady=AppleStyle.SPACING['md'])
        
        section_title = tk.Label(
            settings_section,
            text="ファイル設定",
            **AppleStyle.get_label_style('heading')
        )
        section_title.pack(anchor='w', pady=(AppleStyle.SPACING['md'], AppleStyle.SPACING['lg']),
                          padx=AppleStyle.SPACING['md'])
        
        # ファイル選択
        self.file_selector = FileSelector(
            settings_section,
            "読み上げるExcelファイル",
            callback=self._on_file_selected
        )
        self.file_selector.pack(fill='x', padx=AppleStyle.SPACING['md'], 
                                pady=(0, AppleStyle.SPACING['md']))
        
        # シート選択
        sheet_frame = tk.Frame(settings_section, **AppleStyle.get_frame_style('surface'))
        sheet_frame.pack(fill='x', padx=AppleStyle.SPACING['md'], 
                        pady=(0, AppleStyle.SPACING['md']))
        
        tk.Label(
            sheet_frame,
            text="シート名またはインデックス:",
            **AppleStyle.get_label_style('body_bold')
        ).pack(anchor='w', pady=(0, AppleStyle.SPACING['xs']))
        
        self.sheet_var = tk.StringVar(value="0")
        sheet_entry = tk.Entry(
            sheet_frame,
            textvariable=self.sheet_var,
            **AppleStyle.get_entry_style()
        )
        sheet_entry.pack(fill='x')
        
        tk.Label(
            sheet_frame,
            text="（例: 0 または Sheet1）",
            **AppleStyle.get_label_style('caption')
        ).pack(anchor='w', pady=(AppleStyle.SPACING['xs'], 0))
        
        # 読み上げ設定セクション
        reading_settings_section = tk.Frame(
            main_container,
            **AppleStyle.get_frame_style('card')
        )
        reading_settings_section.pack(fill='x', pady=(0, AppleStyle.SPACING['lg']), 
                                     padx=AppleStyle.SPACING['md'], ipady=AppleStyle.SPACING['md'])
        
        reading_title = tk.Label(
            reading_settings_section,
            text="読み上げ設定",
            **AppleStyle.get_label_style('heading')
        )
        reading_title.pack(anchor='w', pady=(AppleStyle.SPACING['md'], AppleStyle.SPACING['lg']),
                          padx=AppleStyle.SPACING['md'])
        
        # 読み上げ速度
        speed_frame = tk.Frame(reading_settings_section, **AppleStyle.get_frame_style('surface'))
        speed_frame.pack(fill='x', padx=AppleStyle.SPACING['md'], 
                        pady=(0, AppleStyle.SPACING['md']))
        
        tk.Label(
            speed_frame,
            text="読み上げ速度:",
            **AppleStyle.get_label_style('body_bold')
        ).pack(anchor='w', pady=(0, AppleStyle.SPACING['xs']))
        
        speed_control_frame = tk.Frame(speed_frame, **AppleStyle.get_frame_style('surface'))
        speed_control_frame.pack(fill='x')
        
        self.speed_var = tk.IntVar(value=0)
        speed_scale = tk.Scale(
            speed_control_frame,
            from_=-10,
            to=10,
            orient=tk.HORIZONTAL,
            variable=self.speed_var,
            **AppleStyle.get_entry_style()
        )
        speed_scale.pack(side='left', fill='x', expand=True, padx=(0, AppleStyle.SPACING['sm']))
        
        speed_label = tk.Label(
            speed_control_frame,
            textvariable=tk.StringVar(value="0"),
            width=4,
            **AppleStyle.get_label_style('body')
        )
        speed_label.pack(side='right')
        
        # 速度ラベルの更新
        def update_speed_label(*args):
            speed_label.config(text=str(self.speed_var.get()))
        self.speed_var.trace('w', update_speed_label)
        
        # 音量
        volume_frame = tk.Frame(reading_settings_section, **AppleStyle.get_frame_style('surface'))
        volume_frame.pack(fill='x', padx=AppleStyle.SPACING['md'], 
                         pady=(0, AppleStyle.SPACING['md']))
        
        tk.Label(
            volume_frame,
            text="音量:",
            **AppleStyle.get_label_style('body_bold')
        ).pack(anchor='w', pady=(0, AppleStyle.SPACING['xs']))
        
        volume_control_frame = tk.Frame(volume_frame, **AppleStyle.get_frame_style('surface'))
        volume_control_frame.pack(fill='x')
        
        self.volume_var = tk.DoubleVar(value=1.0)
        volume_scale = tk.Scale(
            volume_control_frame,
            from_=0.0,
            to=1.0,
            resolution=0.1,
            orient=tk.HORIZONTAL,
            variable=self.volume_var,
            **AppleStyle.get_entry_style()
        )
        volume_scale.pack(side='left', fill='x', expand=True, padx=(0, AppleStyle.SPACING['sm']))
        
        volume_label = tk.Label(
            volume_control_frame,
            textvariable=tk.StringVar(value="100%"),
            width=5,
            **AppleStyle.get_label_style('body')
        )
        volume_label.pack(side='right')
        
        # 音量ラベルの更新
        def update_volume_label(*args):
            volume_label.config(text=f"{int(self.volume_var.get() * 100)}%")
        self.volume_var.trace('w', update_volume_label)
        
        # 列間の待ち時間
        column_delay_frame = tk.Frame(reading_settings_section, **AppleStyle.get_frame_style('surface'))
        column_delay_frame.pack(fill='x', padx=AppleStyle.SPACING['md'], 
                               pady=(0, AppleStyle.SPACING['md']))
        
        tk.Label(
            column_delay_frame,
            text="列間の待ち時間（秒）:",
            **AppleStyle.get_label_style('body_bold')
        ).pack(anchor='w', pady=(0, AppleStyle.SPACING['xs']))
        
        self.column_delay_var = tk.DoubleVar(value=0.5)
        column_delay_entry = tk.Entry(
            column_delay_frame,
            textvariable=self.column_delay_var,
            **AppleStyle.get_entry_style()
        )
        column_delay_entry.pack(fill='x')
        
        # 行間の待ち時間
        row_delay_frame = tk.Frame(reading_settings_section, **AppleStyle.get_frame_style('surface'))
        row_delay_frame.pack(fill='x', padx=AppleStyle.SPACING['md'], 
                            pady=(0, AppleStyle.SPACING['md']))
        
        tk.Label(
            row_delay_frame,
            text="行間の待ち時間（秒）:",
            **AppleStyle.get_label_style('body_bold')
        ).pack(anchor='w', pady=(0, AppleStyle.SPACING['xs']))
        
        self.row_delay_var = tk.DoubleVar(value=0.0)
        row_delay_entry = tk.Entry(
            row_delay_frame,
            textvariable=self.row_delay_var,
            **AppleStyle.get_entry_style()
        )
        row_delay_entry.pack(fill='x')
        
        # 進捗表示セクション
        progress_section = tk.Frame(
            main_container,
            **AppleStyle.get_frame_style('card')
        )
        progress_section.pack(fill='x', pady=(0, AppleStyle.SPACING['lg']), 
                             padx=AppleStyle.SPACING['md'], ipady=AppleStyle.SPACING['md'])
        
        progress_title = tk.Label(
            progress_section,
            text="進捗情報",
            **AppleStyle.get_label_style('heading')
        )
        progress_title.pack(anchor='w', pady=(AppleStyle.SPACING['md'], AppleStyle.SPACING['lg']),
                           padx=AppleStyle.SPACING['md'])
        
        # 進捗情報表示
        self.progress_info_label = tk.Label(
            progress_section,
            text="読み上げ待機中...",
            **AppleStyle.get_label_style('body')
        )
        self.progress_info_label.pack(anchor='w', padx=AppleStyle.SPACING['md'], 
                                      pady=(0, AppleStyle.SPACING['md']))
        
        # コントロールボタンセクション
        button_section = tk.Frame(
            main_container,
            **AppleStyle.get_frame_style('background')
        )
        button_section.pack(fill='x', pady=(0, AppleStyle.SPACING['lg']))
        
        # ボタンフレーム
        button_frame = tk.Frame(button_section, **AppleStyle.get_frame_style('background'))
        button_frame.pack()
        
        # 実行ボタン
        self.execute_btn = tk.Button(
            button_frame,
            text="▶ 読み上げを開始",
            command=self._execute_reading,
            **AppleStyle.get_button_style('primary'),
            font=('Segoe UI', 14, 'bold'),
            padx=AppleStyle.SPACING['xl'],
            pady=AppleStyle.SPACING['md']
        )
        self.execute_btn.pack(side='left', padx=AppleStyle.SPACING['sm'])
        
        # 一時停止ボタン
        self.pause_btn = tk.Button(
            button_frame,
            text="⏸ 一時停止",
            command=self._pause_reading,
            **AppleStyle.get_button_style('secondary'),
            state='disabled'
        )
        self.pause_btn.pack(side='left', padx=AppleStyle.SPACING['sm'])
        
        # 停止ボタン
        self.stop_btn = tk.Button(
            button_frame,
            text="⏹ 停止",
            command=self._stop_reading,
            **AppleStyle.get_button_style('secondary'),
            state='disabled'
        )
        self.stop_btn.pack(side='left', padx=AppleStyle.SPACING['sm'])
        
        # 進捗表示
        self.progress = ProgressIndicator(main_container)
    
    def _on_file_selected(self, file_path: str):
        """ファイルが選択されたときの処理"""
        # ファイル情報を表示するなど
        pass
    
    def _validate_inputs(self) -> Tuple[bool, Optional[str]]:
        """入力の検証"""
        file_path = self.file_selector.get_file_path()
        
        if not file_path:
            return False, "Excelファイルを選択してください"
        if not Path(file_path).exists():
            return False, "ファイルが見つかりません"
        
        try:
            sheet_value = self.sheet_var.get().strip()
            if sheet_value:
                # 数値に変換できるか確認
                try:
                    int(sheet_value)
                except ValueError:
                    # 文字列の場合はそのまま（シート名）
                    pass
        except Exception:
            return False, "シート名が無効です"
        
        return True, None
    
    def _progress_callback(self, current_row: int, total_rows: int, column_name: str, cell_value: Any):
        """進捗コールバック"""
        self.current_row = current_row
        self.total_rows = total_rows
        cell_str = str(cell_value) if not pd.isna(cell_value) else ""
        if len(cell_str) > 30:
            cell_str = cell_str[:30] + "..."
        
        info_text = f"行 {current_row}/{total_rows} | 列: {column_name}"
        if cell_str:
            info_text += f" | 内容: {cell_str}"
        
        self.after(0, lambda: self.progress_info_label.config(text=info_text))
    
    def _execute_reading(self):
        """読み上げを実行"""
        # バリデーション
        is_valid, error_message = self._validate_inputs()
        if not is_valid:
            messagebox.showerror("入力エラー", error_message)
            return
        
        # UIを無効化
        self.execute_btn.config(state='disabled')
        self.pause_btn.config(state='normal')
        self.stop_btn.config(state='normal')
        self.progress.show("読み上げを開始しています...")
        
        # 別スレッドで処理を実行
        self.reading_thread = threading.Thread(target=self._process_in_thread)
        self.reading_thread.daemon = True
        self.reading_thread.start()
    
    def _process_in_thread(self):
        """別スレッドで処理を実行"""
        try:
            import pandas as pd
            
            # 設定を作成
            sheet_value = self.sheet_var.get().strip()
            try:
                sheet_name = int(sheet_value)
            except ValueError:
                sheet_name = sheet_value if sheet_value else 0
            
            config = {
                'file_path': self.file_selector.get_file_path(),
                'sheet_name': sheet_name,
                'speed': self.speed_var.get(),
                'column_delay': self.column_delay_var.get(),
                'row_delay': self.row_delay_var.get(),
                'volume': self.volume_var.get(),
                'progress_callback': self._progress_callback
            }
            
            # 読み上げツールを作成
            self.reader = ExcelReader(config)
            
            self.after(0, lambda: self.progress.update_message("ファイルを読み込んでいます..."))
            result = self.reader.read_excel()
            
            # 結果を表示
            self.after(0, lambda: self._show_result(result))
            
        except Exception as e:
            self.after(0, lambda: self._show_error(str(e)))
    
    def _pause_reading(self):
        """読み上げを一時停止"""
        if self.reader:
            if self.reader.is_paused():
                self.reader.resume()
                self.pause_btn.config(text="⏸ 一時停止")
            else:
                self.reader.pause()
                self.pause_btn.config(text="▶ 再開")
    
    def _stop_reading(self):
        """読み上げを停止"""
        if self.reader:
            self.reader.stop()
        self._reset_ui()
    
    def _reset_ui(self):
        """UIをリセット"""
        self.execute_btn.config(state='normal')
        self.pause_btn.config(state='disabled', text="⏸ 一時停止")
        self.stop_btn.config(state='disabled')
        self.progress.hide()
        self.progress_info_label.config(text="読み上げ待機中...")
    
    def _show_result(self, result: Dict[str, Any]):
        """結果を表示"""
        self._reset_ui()
        
        if result['success']:
            message = (
                f"読み上げが完了しました！\n\n"
                f"読み上げた行数: {result['rows_read']}行"
            )
            messagebox.showinfo("成功", message)
        else:
            messagebox.showerror("エラー", result['message'])
    
    def _show_error(self, error_message: str):
        """エラーを表示"""
        self._reset_ui()
        messagebox.showerror("エラー", f"処理中にエラーが発生しました:\n{error_message}")
    
    def _on_closing(self):
        """ウィンドウを閉じるときの処理"""
        if self.reader and self.reader.is_reading():
            if messagebox.askokcancel("確認", "読み上げ中です。停止してウィンドウを閉じますか？"):
                self.reader.stop()
                self.destroy()
        else:
            self.destroy()

