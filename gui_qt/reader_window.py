"""
Reader Window - Excel読み上げ機能のGUI (PyQt6版)
Excelファイルの内容を音声で読み上げる機能専用のウィンドウ
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFileDialog, QSlider, QLineEdit, QMessageBox, QFrame,
    QCheckBox, QScrollArea, QWidget, QGridLayout, QSizePolicy,
    QStackedWidget
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QObject
from pathlib import Path
from typing import Optional, Dict, Any, Union
import pandas as pd

from core import ExcelReader
from gui_qt.styles import AppleStyle


# 定数
GRID_COLUMNS = 3  # 列選択グリッドの列数
DEFAULT_SHEET = "0"  # デフォルトのシート名
DEFAULT_COLUMN_DELAY = "0.5"  # デフォルトの列間待ち時間（秒）
DEFAULT_ROW_DELAY = "0.0"  # デフォルトの行間待ち時間（秒）
DEFAULT_VOLUME = 100  # デフォルトの音量（%）
DEFAULT_SPEED = 0  # デフォルトの読み上げ速度


def get_column_letter(idx: int) -> str:
    """
    列インデックスをExcel列名（A, B, C...）に変換
    
    Args:
        idx: 列インデックス（0ベース）
        
    Returns:
        Excel列名（A, B, C, ..., Z, AA, AB, ...）
    """
    result = ""
    idx += 1  # 1ベースに変換
    while idx > 0:
        idx -= 1
        result = chr(65 + (idx % 26)) + result
        idx //= 26
    return result


class ReadingWorker(QObject):
    """読み上げ処理を実行するワーカースレッド"""
    
    finished = pyqtSignal(dict)
    progress = pyqtSignal(int, int, str, object)  # current_row, total_rows, column_name, cell_value
    error = pyqtSignal(str)
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__()
        self.config = config
        self.reader: Optional[ExcelReader] = None
        self._stop_requested = False
        self._pause_requested = False
    
    def set_progress_callback(self, callback):
        """進捗コールバックを設定"""
        self.progress.connect(callback)
    
    def run(self):
        """読み上げ処理を実行"""
        try:
            # 進捗コールバックを設定
            def progress_callback(current_row, total_rows, column_name, cell_value):
                self.progress.emit(current_row, total_rows, column_name, cell_value)
            
            self.config['progress_callback'] = progress_callback
            self.reader = ExcelReader(self.config)
            
            result = self.reader.read_excel()
            self.finished.emit(result)
            
        except Exception as e:
            self.error.emit(str(e))
    
    def stop(self):
        """読み上げを停止"""
        self._stop_requested = True
        if self.reader:
            self.reader.stop()
    
    def pause(self):
        """読み上げを一時停止"""
        self._pause_requested = True
        if self.reader:
            self.reader.pause()
    
    def resume(self):
        """読み上げを再開"""
        self._pause_requested = False
        if self.reader:
            self.reader.resume()
    
    def update_settings(self, speed: Optional[int] = None, volume: Optional[float] = None,
                        column_delay: Optional[float] = None, row_delay: Optional[float] = None):
        """読み上げ中に設定を更新"""
        if self.reader:
            self.reader.update_settings(speed, volume, column_delay, row_delay)


class ReaderWindow(QDialog):
    """Excel読み上げウィンドウ（PyQt6版）"""
    
    def __init__(self, parent=None, on_home_click=None):
        """
        初期化
        
        Args:
            parent: 親ウィンドウ（Noneの場合は独立ウィンドウ）
            on_home_click: ホームに戻るボタンのコールバック
        """
        super().__init__(parent)
        
        # ウィンドウフラグを設定（移動可能、閉じるボタンあり）
        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.WindowTitleHint |
            Qt.WindowType.WindowSystemMenuHint |
            Qt.WindowType.WindowMinimizeButtonHint |
            Qt.WindowType.WindowMaximizeButtonHint |
            Qt.WindowType.WindowCloseButtonHint
        )
        
        self.setWindowTitle("Excel 読み上げ機能")
        self.resize(700, 800)
        self.setMinimumSize(650, 600)  # 最小サイズを設定
        
        self.on_home_click = on_home_click
        
        # 変数
        self.worker: Optional[ReadingWorker] = None
        self.worker_thread: Optional[QThread] = None
        self.current_row = 0
        self.total_rows = 0
        self.columns = []  # Excelファイルの列リスト
        self.column_checkboxes = []  # 列選択チェックボックス
        
        # UI作成
        self._create_widgets()
        
        # ウィンドウを中央に配置
        self._center_window()
    
    def _center_window(self):
        """ウィンドウを画面中央に配置（画面外に出ないようにする）"""
        from PyQt6.QtWidgets import QApplication
        
        # 画面のジオメトリを取得
        screen = QApplication.primaryScreen().geometry()
        screen_width = screen.width()
        screen_height = screen.height()
        
        # ウィンドウのサイズを取得
        window_width = self.width()
        window_height = self.height()
        
        # ウィンドウのサイズが画面サイズを超えている場合は調整
        if window_width > screen_width:
            window_width = screen_width - 20  # マージンを確保
            self.resize(window_width, window_height)
        if window_height > screen_height:
            window_height = screen_height - 20  # マージンを確保
            self.resize(window_width, window_height)
        
        # 親ウィンドウがある場合でも、画面内に確実に収まるようにする
        # 画面の中央に配置
        x = screen.x() + (screen_width - window_width) // 2
        y = screen.y() + (screen_height - window_height) // 2
        
        # 画面外に出ないように調整
        x = max(screen.x(), min(x, screen.x() + screen_width - window_width))
        y = max(screen.y(), min(y, screen.y() + screen_height - window_height))
        
        self.move(x, y)
    
    def _create_widgets(self):
        """ウィジェットを作成"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(AppleStyle.SPACING['md'])
        main_layout.setContentsMargins(
            AppleStyle.SPACING['md'],
            AppleStyle.SPACING['md'],
            AppleStyle.SPACING['md'],
            AppleStyle.SPACING['md']
        )
        
        # タイトル
        title_label = QLabel("Excel 読み上げ機能")
        title_style = AppleStyle.get_label_style('title')
        title_label.setFont(title_style['font'])
        title_label.setStyleSheet(f"color: {title_style['color'].name()};")
        main_layout.addWidget(title_label)
        
        # サブタイトル
        subtitle_label = QLabel("Excelファイルの内容を音声で読み上げます")
        subtitle_style = AppleStyle.get_label_style('caption')
        subtitle_label.setFont(subtitle_style['font'])
        subtitle_label.setStyleSheet(f"color: {subtitle_style['color'].name()};")
        main_layout.addWidget(subtitle_label)
        
        # セクション間のスペーシングを追加
        main_layout.addSpacing(AppleStyle.SPACING['md'])
        
        # 画面遷移用のStackedWidget
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setMinimumHeight(400)
        self.stacked_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        main_layout.addWidget(self.stacked_widget, stretch=1)
        
        # ページ1: ファイル設定と列選択
        page1 = self._create_page1()
        self.stacked_widget.addWidget(page1)
        
        # ページ2: 読み上げ設定と進捗表示
        page2 = self._create_page2()
        self.stacked_widget.addWidget(page2)
        
        # 初期ページを設定
        self.stacked_widget.setCurrentIndex(0)
        
        # ナビゲーションセクション
        nav_section = self._create_navigation_section()
        nav_section.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Minimum
        )
        main_layout.addWidget(nav_section)
        
        # ボタンセクション
        button_section = self._create_button_section()
        button_section.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Minimum
        )
        main_layout.addWidget(button_section)
    
    def _create_page1(self) -> QWidget:
        """ページ1（ファイル設定と列選択）を作成"""
        page = QWidget()
        page.setStyleSheet(f"background-color: {AppleStyle.COLORS['background'].name()};")
        page.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        layout = QVBoxLayout(page)
        layout.setSpacing(AppleStyle.SPACING['md'])
        layout.setContentsMargins(
            AppleStyle.SPACING['md'],
            AppleStyle.SPACING['md'],
            AppleStyle.SPACING['md'],
            AppleStyle.SPACING['md']
        )
        
        # ファイル設定セクション
        file_section = self._create_file_section()
        file_section.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Minimum
        )
        layout.addWidget(file_section)
        
        # 列選択セクション（伸縮可能）
        self.column_section = self._create_column_section()
        self.column_section.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        layout.addWidget(self.column_section, stretch=1)
        self.column_section.hide()  # 初期状態では非表示
        
        return page
    
    def _create_page2(self) -> QWidget:
        """ページ2（読み上げ設定と進捗表示）を作成"""
        page = QWidget()
        page.setStyleSheet(f"background-color: {AppleStyle.COLORS['background'].name()};")
        page.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        layout = QVBoxLayout(page)
        layout.setSpacing(AppleStyle.SPACING['md'])
        layout.setContentsMargins(
            AppleStyle.SPACING['md'],
            AppleStyle.SPACING['md'],
            AppleStyle.SPACING['md'],
            AppleStyle.SPACING['md']
        )
        
        # 読み上げ設定セクション
        reading_section = self._create_reading_settings_section()
        reading_section.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Minimum
        )
        layout.addWidget(reading_section)
        
        # 進捗表示セクション
        progress_section = self._create_progress_section()
        progress_section.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Minimum
        )
        layout.addWidget(progress_section)
        
        # 残りのスペースを埋める
        layout.addStretch()
        
        return page
    
    def _create_navigation_section(self) -> QFrame:
        """ナビゲーションセクションを作成"""
        section = QFrame()
        section.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Minimum
        )
        layout = QHBoxLayout(section)
        layout.setSpacing(AppleStyle.SPACING['sm'])
        
        # 前へボタン
        self.prev_btn = QPushButton("← 前へ")
        self.prev_btn.setStyleSheet(AppleStyle.get_button_style('secondary'))
        self.prev_btn.setEnabled(False)  # 最初のページでは無効
        self.prev_btn.clicked.connect(self._go_to_previous_page)
        layout.addWidget(self.prev_btn)
        
        layout.addStretch()
        
        # ページインジケーター
        self.page_indicator = QLabel("1 / 2")
        indicator_style = AppleStyle.get_label_style('body')
        self.page_indicator.setFont(indicator_style['font'])
        self.page_indicator.setStyleSheet(f"color: {indicator_style['color'].name()};")
        layout.addWidget(self.page_indicator)
        
        layout.addStretch()
        
        # 次へボタン
        self.next_btn = QPushButton("次へ →")
        self.next_btn.setStyleSheet(AppleStyle.get_button_style('secondary'))
        self.next_btn.clicked.connect(self._go_to_next_page)
        layout.addWidget(self.next_btn)
        
        return section
    
    def _go_to_previous_page(self):
        """前のページに移動"""
        current_index = self.stacked_widget.currentIndex()
        if current_index > 0:
            self.stacked_widget.setCurrentIndex(current_index - 1)
            self._update_navigation_buttons()
    
    def _go_to_next_page(self):
        """次のページに移動"""
        current_index = self.stacked_widget.currentIndex()
        if current_index < self.stacked_widget.count() - 1:
            # ページ2に移動する前に、ファイルが選択されているか確認
            if current_index == 0:
                file_path = self.file_path_edit.text().strip()
                if not file_path:
                    QMessageBox.warning(
                        self,
                        "警告",
                        "Excelファイルを選択してください。"
                    )
                    return
            self.stacked_widget.setCurrentIndex(current_index + 1)
            self._update_navigation_buttons()
    
    def _update_navigation_buttons(self):
        """ナビゲーションボタンの状態を更新"""
        current_index = self.stacked_widget.currentIndex()
        total_pages = self.stacked_widget.count()
        
        # 前へボタン
        self.prev_btn.setEnabled(current_index > 0)
        
        # 次へボタン
        self.next_btn.setEnabled(current_index < total_pages - 1)
        
        # ページインジケーター
        self.page_indicator.setText(f"{current_index + 1} / {total_pages}")
    
    def _create_section_title(self, text: str, layout: QVBoxLayout) -> QLabel:
        """
        セクションタイトルを作成してレイアウトに追加
        
        Args:
            text: タイトルテキスト
            layout: 追加先のレイアウト
            
        Returns:
            作成されたQLabel
        """
        title = QLabel(text)
        title_style = AppleStyle.get_label_style('heading')
        title.setFont(title_style['font'])
        title.setStyleSheet(f"""
            color: {title_style['color'].name()};
            font-weight: bold;
            margin-bottom: {AppleStyle.SPACING['sm']}px;
        """)
        layout.addWidget(title)
        return title
    
    def _create_file_section(self) -> QFrame:
        """ファイル設定セクションを作成"""
        section = QFrame()
        section.setStyleSheet(AppleStyle.get_frame_style('card'))
        section.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Minimum
        )
        layout = QVBoxLayout(section)
        layout.setSpacing(AppleStyle.SPACING['md'])
        layout.setContentsMargins(
            AppleStyle.SPACING['md'],
            AppleStyle.SPACING['md'],
            AppleStyle.SPACING['md'],
            AppleStyle.SPACING['md']
        )
        
        # セクションタイトル
        self._create_section_title("📁 ファイル設定", layout)
        
        # ファイル選択
        file_label = QLabel("Excelファイル:")
        file_label_style = AppleStyle.get_label_style('body_bold')
        file_label.setFont(file_label_style['font'])
        file_label.setStyleSheet(f"""
            color: {file_label_style['color'].name()};
            margin-top: {AppleStyle.SPACING['xs']}px;
            margin-bottom: {AppleStyle.SPACING['xs']}px;
        """)
        layout.addWidget(file_label)
        
        file_layout = QHBoxLayout()
        file_layout.setSpacing(AppleStyle.SPACING['sm'])
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setStyleSheet(AppleStyle.get_entry_style())
        self.file_path_edit.setPlaceholderText("読み上げるExcelファイルを選択...")
        self.file_path_edit.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed
        )
        file_layout.addWidget(self.file_path_edit, stretch=1)
        
        browse_btn = QPushButton("参照...")
        browse_btn.setStyleSheet(AppleStyle.get_button_style('secondary'))
        browse_btn.setMinimumWidth(100)
        browse_btn.setMaximumWidth(120)
        browse_btn.setMinimumHeight(36)
        browse_btn.setSizePolicy(
            QSizePolicy.Policy.Minimum,
            QSizePolicy.Policy.Fixed
        )
        browse_btn.clicked.connect(self._browse_file)
        file_layout.addWidget(browse_btn)
        
        layout.addLayout(file_layout)
        
        # シート選択（スペーシングを追加）
        layout.addSpacing(AppleStyle.SPACING['sm'])
        
        sheet_label = QLabel("シート名またはインデックス:")
        sheet_style = AppleStyle.get_label_style('body_bold')
        sheet_label.setFont(sheet_style['font'])
        sheet_label.setStyleSheet(f"""
            color: {sheet_style['color'].name()};
            margin-top: {AppleStyle.SPACING['sm']}px;
            margin-bottom: {AppleStyle.SPACING['xs']}px;
        """)
        layout.addWidget(sheet_label)
        
        self.sheet_edit = QLineEdit(DEFAULT_SHEET)
        self.sheet_edit.setStyleSheet(AppleStyle.get_entry_style())
        layout.addWidget(self.sheet_edit)
        
        sheet_hint = QLabel("（例: 0 または Sheet1）")
        hint_style = AppleStyle.get_label_style('caption')
        sheet_hint.setFont(hint_style['font'])
        sheet_hint.setStyleSheet(f"""
            color: {hint_style['color'].name()};
            margin-top: {AppleStyle.SPACING['xs']}px;
        """)
        layout.addWidget(sheet_hint)
        
        return section
    
    def _create_column_section(self) -> QFrame:
        """列選択セクションを作成"""
        section = QFrame()
        section.setStyleSheet(AppleStyle.get_frame_style('card'))
        section.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        layout = QVBoxLayout(section)
        layout.setSpacing(AppleStyle.SPACING['sm'])
        layout.setContentsMargins(
            AppleStyle.SPACING['md'],
            AppleStyle.SPACING['md'],
            AppleStyle.SPACING['md'],
            AppleStyle.SPACING['md']
        )
        
        # セクションタイトル
        self._create_section_title("📋 読み上げる列を選択", layout)
        
        desc = QLabel("読み上げる列にチェックを入れてください（すべて選択がデフォルト）")
        desc_style = AppleStyle.get_label_style('caption')
        desc.setFont(desc_style['font'])
        desc.setStyleSheet(f"""
            color: {desc_style['color'].name()};
            margin-bottom: {AppleStyle.SPACING['sm']}px;
        """)
        layout.addWidget(desc)
        
        # すべて選択/すべて解除ボタン
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        select_all_btn = QPushButton("すべて選択")
        select_all_btn.setStyleSheet(AppleStyle.get_button_style('secondary'))
        select_all_btn.clicked.connect(self._select_all_columns)
        button_layout.addWidget(select_all_btn)
        
        deselect_all_btn = QPushButton("すべて解除")
        deselect_all_btn.setStyleSheet(AppleStyle.get_button_style('secondary'))
        deselect_all_btn.clicked.connect(self._deselect_all_columns)
        button_layout.addWidget(deselect_all_btn)
        
        layout.addLayout(button_layout)
        
        # スクロール可能な列選択エリア
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setStyleSheet(f"""
            QScrollArea {{
                border: 1px solid {AppleStyle.COLORS['border'].name()};
                border-radius: {AppleStyle.BORDER_RADIUS['sm']}px;
                background-color: {AppleStyle.COLORS['surface'].name()};
            }}
        """)
        scroll_area.setMinimumHeight(150)
        scroll_area.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        
        self.columns_widget = QWidget()
        self.columns_widget.setStyleSheet(f"""
            background-color: {AppleStyle.COLORS['surface'].name()};
        """)
        self.columns_layout = QGridLayout(self.columns_widget)
        self.columns_layout.setSpacing(AppleStyle.SPACING['sm'])
        self.columns_layout.setContentsMargins(
            AppleStyle.SPACING['sm'],
            AppleStyle.SPACING['sm'],
            AppleStyle.SPACING['sm'],
            AppleStyle.SPACING['sm']
        )
        
        # プレースホルダーラベル（列が読み込まれていない場合）
        self.column_placeholder = QLabel("Excelファイルを選択すると、読み上げ可能な列がここに表示されます")
        placeholder_style = AppleStyle.get_label_style('caption')
        self.column_placeholder.setFont(placeholder_style['font'])
        self.column_placeholder.setStyleSheet(f"""
            color: {AppleStyle.COLORS['text_secondary'].name()};
            padding: {AppleStyle.SPACING['lg']}px;
        """)
        self.column_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.columns_layout.addWidget(self.column_placeholder, 0, 0, 1, 3)
        
        scroll_area.setWidget(self.columns_widget)
        layout.addWidget(scroll_area, stretch=1)
        
        return section
    
    def _create_column_checkboxes(self):
        """列選択チェックボックスを作成"""
        checkbox_style = AppleStyle.get_label_style('body')
        
        for col_idx, col_name in enumerate(self.columns):
            col_letter = get_column_letter(col_idx)
            checkbox = QCheckBox(f"{col_name} (列{col_letter})")
            checkbox.setFont(checkbox_style['font'])
            checkbox.setStyleSheet(f"""
                QCheckBox {{
                    color: {checkbox_style['color'].name()};
                    padding: 4px;
                }}
                QCheckBox::indicator {{
                    width: 20px;
                    height: 20px;
                }}
                QCheckBox:hover {{
                    background-color: rgba(0, 122, 255, 0.1);
                }}
            """)
            checkbox.setChecked(True)  # デフォルトで全選択
            self.column_checkboxes.append(checkbox)
            
            # グリッドレイアウトに配置（行、列）
            row = col_idx // GRID_COLUMNS
            col = col_idx % GRID_COLUMNS
            self.columns_layout.addWidget(checkbox, row, col)
    
    def _select_all_columns(self):
        """すべての列を選択"""
        for checkbox in self.column_checkboxes:
            checkbox.setChecked(True)
    
    def _deselect_all_columns(self):
        """すべての列を解除"""
        for checkbox in self.column_checkboxes:
            checkbox.setChecked(False)
    
    def _get_sheet_name(self) -> Union[int, str]:
        """
        シート名またはインデックスを取得
        
        Returns:
            シート名（文字列）またはインデックス（整数）
        """
        sheet_value = self.sheet_edit.text().strip()
        try:
            return int(sheet_value)
        except ValueError:
            return sheet_value if sheet_value else 0
    
    def _extract_column_names(self, df: pd.DataFrame) -> list[str]:
        """
        DataFrameから列名を抽出
        
        Args:
            df: pandas DataFrame
            
        Returns:
            列名のリスト
        """
        columns = []
        for col_idx, col_name in enumerate(df.columns):
            col_str = str(col_name)
            # 列名が空またはNaNの場合は列番号を使用
            if not col_str or col_str == 'nan' or col_str.strip() == '':
                col_str = f"列{get_column_letter(col_idx)}"
            columns.append(col_str)
        return columns
    
    def _clear_column_checkboxes(self):
        """既存の列選択チェックボックスをクリア"""
        for checkbox in self.column_checkboxes:
            checkbox.setParent(None)
            checkbox.deleteLater()
        self.column_checkboxes.clear()
    
    def _load_columns(self, file_path: str):
        """Excelファイルから列を読み込む"""
        try:
            # シート名を取得
            sheet_name = self._get_sheet_name()
            
            # Excelファイルを読み込む（1行目をヘッダーとして扱う）
            df = pd.read_excel(file_path, sheet_name=sheet_name, header=0, nrows=0)
            
            # 列名を抽出
            self.columns = self._extract_column_names(df)
            
            # 既存のチェックボックスをクリア
            self._clear_column_checkboxes()
            
            # プレースホルダーラベルを非表示
            if hasattr(self, 'column_placeholder'):
                self.column_placeholder.hide()
            
            # 列選択チェックボックスを作成
            self._create_column_checkboxes()
            
            # 列選択セクションを表示
            self.column_section.show()
            
        except Exception as e:
            QMessageBox.warning(
                self,
                "エラー",
                f"列の読み込みに失敗しました:\n{str(e)}"
            )
    
    def _create_reading_settings_section(self) -> QFrame:
        """読み上げ設定セクションを作成"""
        section = QFrame()
        section.setStyleSheet(AppleStyle.get_frame_style('card'))
        section.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Minimum
        )
        layout = QVBoxLayout(section)
        layout.setSpacing(AppleStyle.SPACING['sm'])
        layout.setContentsMargins(
            AppleStyle.SPACING['md'],
            AppleStyle.SPACING['md'],
            AppleStyle.SPACING['md'],
            AppleStyle.SPACING['md']
        )
        
        # セクションタイトル
        self._create_section_title("⚙️ 読み上げ設定", layout)
        
        # 読み上げ速度
        speed_label = QLabel("読み上げ速度:")
        speed_style = AppleStyle.get_label_style('body_bold')
        speed_label.setFont(speed_style['font'])
        speed_label.setStyleSheet(f"""
            color: {speed_style['color'].name()};
            margin-top: {AppleStyle.SPACING['xs']}px;
            margin-bottom: {AppleStyle.SPACING['xs']}px;
        """)
        layout.addWidget(speed_label)
        
        speed_layout = QHBoxLayout()
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setMinimum(-10)
        self.speed_slider.setMaximum(10)
        self.speed_slider.setValue(DEFAULT_SPEED)
        speed_layout.addWidget(self.speed_slider)
        
        self.speed_label = QLabel("0")
        self.speed_label.setMinimumWidth(40)
        self.speed_slider.valueChanged.connect(lambda v: self.speed_label.setText(str(v)))
        speed_layout.addWidget(self.speed_label)
        
        layout.addLayout(speed_layout)
        
        # 音量
        volume_label = QLabel("音量:")
        volume_label.setFont(speed_style['font'])
        volume_label.setStyleSheet(f"color: {speed_style['color'].name()};")
        layout.addWidget(volume_label)
        
        volume_layout = QHBoxLayout()
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(DEFAULT_VOLUME)
        volume_layout.addWidget(self.volume_slider)
        
        self.volume_label = QLabel(f"{DEFAULT_VOLUME}%")
        self.volume_label.setMinimumWidth(50)
        self.volume_slider.valueChanged.connect(self._on_volume_changed)
        volume_layout.addWidget(self.volume_label)
        
        layout.addLayout(volume_layout)
        
        # 列間の待ち時間
        column_delay_label = QLabel("列間の待ち時間（秒）:")
        column_delay_label.setFont(speed_style['font'])
        column_delay_label.setStyleSheet(f"""
            color: {speed_style['color'].name()};
            margin-top: {AppleStyle.SPACING['sm']}px;
            margin-bottom: {AppleStyle.SPACING['xs']}px;
        """)
        layout.addWidget(column_delay_label)
        
        self.column_delay_edit = QLineEdit(DEFAULT_COLUMN_DELAY)
        self.column_delay_edit.setStyleSheet(AppleStyle.get_entry_style())
        self.column_delay_edit.editingFinished.connect(self._on_column_delay_changed)
        layout.addWidget(self.column_delay_edit)
        
        # 行間の待ち時間
        row_delay_label = QLabel("行間の待ち時間（秒）:")
        row_delay_label.setFont(speed_style['font'])
        row_delay_label.setStyleSheet(f"""
            color: {speed_style['color'].name()};
            margin-top: {AppleStyle.SPACING['sm']}px;
            margin-bottom: {AppleStyle.SPACING['xs']}px;
        """)
        layout.addWidget(row_delay_label)
        
        self.row_delay_edit = QLineEdit(DEFAULT_ROW_DELAY)
        self.row_delay_edit.setStyleSheet(AppleStyle.get_entry_style())
        self.row_delay_edit.editingFinished.connect(self._on_row_delay_changed)
        layout.addWidget(self.row_delay_edit)
        
        return section
    
    def _create_progress_section(self) -> QFrame:
        """進捗表示セクションを作成"""
        section = QFrame()
        section.setStyleSheet(AppleStyle.get_frame_style('card'))
        section.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Minimum
        )
        layout = QVBoxLayout(section)
        layout.setSpacing(AppleStyle.SPACING['sm'])
        layout.setContentsMargins(
            AppleStyle.SPACING['md'],
            AppleStyle.SPACING['md'],
            AppleStyle.SPACING['md'],
            AppleStyle.SPACING['md']
        )
        
        self._create_section_title("📊 進捗情報", layout)
        
        self.progress_info_label = QLabel("読み上げ待機中...")
        progress_style = AppleStyle.get_label_style('body')
        self.progress_info_label.setFont(progress_style['font'])
        self.progress_info_label.setStyleSheet(f"color: {progress_style['color'].name()};")
        layout.addWidget(self.progress_info_label)
        
        return section
    
    def _create_button_section(self) -> QFrame:
        """ボタンセクションを作成"""
        section = QFrame()
        layout = QHBoxLayout(section)
        layout.setSpacing(AppleStyle.SPACING['sm'])
        
        # ホームボタン
        if self.on_home_click:
            home_btn = QPushButton("🏠 ホーム")
            home_btn.setStyleSheet(AppleStyle.get_button_style('secondary'))
            home_btn.clicked.connect(self.on_home_click)
            layout.addWidget(home_btn)
        
        layout.addStretch()
        
        # 実行ボタン
        self.execute_btn = QPushButton("▶ 読み上げを開始")
        self.execute_btn.setStyleSheet(AppleStyle.get_button_style('primary'))
        self.execute_btn.setFont(AppleStyle.FONTS['body_bold'])
        self.execute_btn.clicked.connect(self._execute_reading)
        layout.addWidget(self.execute_btn)
        
        # 一時停止ボタン
        self.pause_btn = QPushButton("⏸ 一時停止")
        self.pause_btn.setStyleSheet(AppleStyle.get_button_style('secondary'))
        self.pause_btn.setEnabled(False)
        self.pause_btn.clicked.connect(self._pause_reading)
        layout.addWidget(self.pause_btn)
        
        # 停止ボタン
        self.stop_btn = QPushButton("⏹ 停止")
        self.stop_btn.setStyleSheet(AppleStyle.get_button_style('secondary'))
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self._stop_reading)
        layout.addWidget(self.stop_btn)
        
        return section
    
    def _browse_file(self):
        """ファイル選択ダイアログを表示"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "読み上げるExcelファイルを選択",
            "",
            "Excel Files (*.xlsx *.xlsm *.xls);;All Files (*)"
        )
        if file_path:
            self.file_path_edit.setText(file_path)
            # ファイル選択後に列を読み込む
            self._load_columns(file_path)
            # 列が読み込まれたら列選択セクションを表示
            if hasattr(self, 'column_section') and self.column_section:
                self.column_section.show()
    
    def _validate_inputs(self) -> tuple[bool, Optional[str]]:
        """入力の検証"""
        file_path = self.file_path_edit.text().strip()
        
        if not file_path:
            return False, "Excelファイルを選択してください"
        if not Path(file_path).exists():
            return False, "ファイルが見つかりません"
        
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
        
        self.progress_info_label.setText(info_text)
    
    def _execute_reading(self):
        """読み上げを実行"""
        # バリデーション
        is_valid, error_message = self._validate_inputs()
        if not is_valid:
            QMessageBox.critical(self, "入力エラー", error_message)
            return
        
        # UIを無効化
        self.execute_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)
        self.stop_btn.setEnabled(True)
        
        # 設定を作成
        sheet_name = self._get_sheet_name()
        
        # 選択された列のインデックスを取得
        selected_column_indices = []
        if self.column_checkboxes:
            for idx, checkbox in enumerate(self.column_checkboxes):
                if checkbox.isChecked():
                    selected_column_indices.append(idx)
            
            # 列が選択されていない場合はすべて選択
            if not selected_column_indices:
                selected_column_indices = list(range(len(self.column_checkboxes)))
        else:
            # 列が読み込まれていない場合は、すべての列を選択（後でExcelファイルから取得）
            selected_column_indices = None
        
        config = {
            'file_path': self.file_path_edit.text().strip(),
            'sheet_name': sheet_name,
            'speed': self.speed_slider.value(),
            'column_delay': float(self.column_delay_edit.text() or DEFAULT_COLUMN_DELAY),
            'row_delay': float(self.row_delay_edit.text() or DEFAULT_ROW_DELAY),
            'volume': self.volume_slider.value() / 100.0,
            'selected_columns': selected_column_indices,  # 選択された列のインデックス
        }
        
        # ワーカースレッドを作成
        self.worker = ReadingWorker(config)
        self.worker.set_progress_callback(self._progress_callback)
        self.worker_thread = QThread()
        
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.started.connect(self.worker.run)
        self.worker.finished.connect(self._on_reading_finished)
        self.worker.error.connect(self._on_reading_error)
        self.worker.progress.connect(self._progress_callback)
        
        self.worker_thread.start()
    
    def _pause_reading(self):
        """読み上げを一時停止"""
        if self.worker:
            if self.worker._pause_requested:
                self.worker.resume()
                self.pause_btn.setText("⏸ 一時停止")
            else:
                self.worker.pause()
                self.pause_btn.setText("▶ 再開")
    
    def _stop_reading(self):
        """読み上げを停止"""
        if self.worker:
            self.worker.stop()
        self._reset_ui()
        if self.worker_thread:
            self.worker_thread.quit()
            self.worker_thread.wait()
    
    def _on_speed_changed(self, value: int):
        """読み上げ速度が変更されたときの処理"""
        self.speed_label.setText(str(value))
        # 読み上げ中の場合、設定を更新
        if self.worker and self.worker.reader:
            self.worker.update_settings(speed=value)
    
    def _on_volume_changed(self, value: int):
        """音量が変更されたときの処理"""
        self.volume_label.setText(f"{value}%")
        # 読み上げ中の場合、設定を更新
        if self.worker and self.worker.reader:
            self.worker.update_settings(volume=value / 100.0)
    
    def _on_column_delay_changed(self):
        """列間の待ち時間が変更されたときの処理"""
        try:
            delay = float(self.column_delay_edit.text() or DEFAULT_COLUMN_DELAY)
            # 読み上げ中の場合、設定を更新
            if self.worker and self.worker.reader:
                self.worker.update_settings(column_delay=delay)
        except ValueError:
            pass
    
    def _on_row_delay_changed(self):
        """行間の待ち時間が変更されたときの処理"""
        try:
            delay = float(self.row_delay_edit.text() or DEFAULT_ROW_DELAY)
            # 読み上げ中の場合、設定を更新
            if self.worker and self.worker.reader:
                self.worker.update_settings(row_delay=delay)
        except ValueError:
            pass
    
    def _reset_ui(self):
        """UIをリセット"""
        self.execute_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.pause_btn.setText("⏸ 一時停止")
        self.stop_btn.setEnabled(False)
        self.progress_info_label.setText("読み上げ待機中...")
    
    def _on_reading_finished(self, result: Dict[str, Any]):
        """読み上げ完了時の処理"""
        self._reset_ui()
        
        if self.worker_thread:
            self.worker_thread.quit()
            self.worker_thread.wait()
        
        if result['success']:
            QMessageBox.information(
                self,
                "成功",
                f"読み上げが完了しました！\n\n読み上げた行数: {result['rows_read']}行"
            )
        else:
            QMessageBox.critical(self, "エラー", result['message'])
    
    def _on_reading_error(self, error_message: str):
        """読み上げエラー時の処理"""
        self._reset_ui()
        
        if self.worker_thread:
            self.worker_thread.quit()
            self.worker_thread.wait()
        
        QMessageBox.critical(self, "エラー", f"処理中にエラーが発生しました:\n{error_message}")
    
    def closeEvent(self, event):
        """ウィンドウを閉じるときの処理"""
        if self.worker and self.worker.reader and self.worker.reader.is_reading():
            reply = QMessageBox.question(
                self,
                "確認",
                "読み上げ中です。停止してウィンドウを閉じますか？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self._stop_reading()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

