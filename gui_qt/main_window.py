"""
VLOOKUP Window - VLOOKUP風機能のGUI (PyQt6版)
VLOOKUP風機能専用のウィンドウ
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QMessageBox, QFrame, QStackedWidget, QWidget
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QObject
from pathlib import Path
from typing import Optional, Dict, Any, Callable
import pandas as pd

from core import ExcelVLookupProcessor
from gui_qt.styles import AppleStyle
from gui_qt.components import FileSelector, ColumnMapper, ProgressIndicator


class VLookupWorker(QObject):
    """VLOOKUP処理を実行するワーカースレッド"""
    
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, config: dict):
        super().__init__()
        self.config = config
    
    def run(self):
        """VLOOKUP処理を実行"""
        try:
            processor = ExcelVLookupProcessor(self.config)
            result = processor.execute()
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class VLookupWindow(QDialog):
    """VLOOKUP風機能ウィンドウ（PyQt6版）"""
    
    def __init__(self, parent=None, on_home_click: Optional[Callable] = None):
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
        
        self.setWindowTitle("Excel VLOOKUP Tool")
        self.resize(900, 800)
        self.setMinimumSize(800, 600)
        
        self.on_home_click = on_home_click
        self.source_columns = []
        self.target_columns = []
        self.worker: Optional[VLookupWorker] = None
        self.worker_thread: Optional[QThread] = None
        
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
        main_layout.setSpacing(AppleStyle.SPACING['xl'])
        main_layout.setContentsMargins(
            AppleStyle.SPACING['xl'],
            AppleStyle.SPACING['xl'],
            AppleStyle.SPACING['xl'],
            AppleStyle.SPACING['xl']
        )
        
        # タイトル
        title_label = QLabel("Excel VLOOKUP Tool")
        title_style = AppleStyle.get_label_style('title')
        title_label.setFont(title_style['font'])
        title_label.setStyleSheet(f"color: {title_style['color'].name()};")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # サブタイトル
        subtitle_label = QLabel("2つのExcelファイルを比較してデータをコピーします")
        subtitle_style = AppleStyle.get_label_style('caption')
        subtitle_label.setFont(subtitle_style['font'])
        subtitle_label.setStyleSheet(f"color: {subtitle_style['color'].name()};")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(subtitle_label)
        
        # 画面遷移用のStackedWidget
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setMinimumHeight(400)
        main_layout.addWidget(self.stacked_widget, stretch=1)
        
        # ページ1: ファイル選択
        self.page1 = self._create_page1()
        self.stacked_widget.addWidget(self.page1)
        
        # ページ2: 列マッピング（内部でサブページを持つ）
        self.page2 = self._create_page2()
        self.stacked_widget.addWidget(self.page2)
        
        # 初期ページを設定
        self.stacked_widget.setCurrentIndex(0)
        
        # ナビゲーションボタン
        nav_section = self._create_navigation_section()
        main_layout.addWidget(nav_section)
        
        # 進捗表示
        self.progress = ProgressIndicator(self)
        main_layout.addWidget(self.progress)
    
    def _create_page1(self) -> QWidget:
        """ページ1（ファイル選択）を作成"""
        page = QWidget()
        page.setStyleSheet(f"background-color: {AppleStyle.COLORS['background'].name()};")
        layout = QVBoxLayout(page)
        layout.setSpacing(AppleStyle.SPACING['lg'])
        layout.setContentsMargins(
            AppleStyle.SPACING['md'],
            AppleStyle.SPACING['md'],
            AppleStyle.SPACING['md'],
            AppleStyle.SPACING['md']
        )
        
        # ファイル選択セクション
        file_section = self._create_file_section()
        layout.addWidget(file_section)
        
        layout.addStretch()
        
        return page
    
    def _create_page2(self) -> QWidget:
        """ページ2（列マッピング）を作成"""
        page = QWidget()
        page.setStyleSheet(f"background-color: {AppleStyle.COLORS['background'].name()};")
        layout = QVBoxLayout(page)
        layout.setSpacing(AppleStyle.SPACING['lg'])
        layout.setContentsMargins(
            AppleStyle.SPACING['md'],
            AppleStyle.SPACING['md'],
            AppleStyle.SPACING['md'],
            AppleStyle.SPACING['md']
        )
        
        # ページ2内のサブページ用StackedWidget
        self.page2_stacked = QStackedWidget()
        self.page2_stacked.setMinimumHeight(400)
        layout.addWidget(self.page2_stacked, stretch=1)
        
        # ページ2-1: マッチング列
        self.page2_1 = self._create_page2_1()
        self.page2_stacked.addWidget(self.page2_1)
        
        # ページ2-2: コピー列
        self.page2_2 = self._create_page2_2()
        self.page2_stacked.addWidget(self.page2_2)
        
        # 初期サブページを設定
        self.page2_stacked.setCurrentIndex(0)
        
        # ページ2内のナビゲーション
        page2_nav = self._create_page2_navigation()
        layout.addWidget(page2_nav)
        
        return page
    
    def _create_navigation_section(self) -> QFrame:
        """ナビゲーションセクションを作成"""
        section = QFrame()
        layout = QHBoxLayout(section)
        layout.setSpacing(AppleStyle.SPACING['md'])
        
        # 戻るボタン
        self.back_btn = QPushButton("← 戻る")
        self.back_btn.setStyleSheet(AppleStyle.get_button_style('secondary'))
        self.back_btn.setEnabled(False)
        self.back_btn.clicked.connect(self._go_to_page1)
        layout.addWidget(self.back_btn)
        
        layout.addStretch()
        
        # 次へボタン
        self.next_btn = QPushButton("次へ →")
        self.next_btn.setStyleSheet(AppleStyle.get_button_style('primary'))
        self.next_btn.clicked.connect(self._go_to_page2)
        layout.addWidget(self.next_btn)
        
        # 実行ボタン（ページ2でのみ表示）
        self.execute_btn = QPushButton("▶ 処理を実行")
        self.execute_btn.setStyleSheet(AppleStyle.get_button_style('primary'))
        self.execute_btn.setFont(AppleStyle.FONTS['body_bold'])
        self.execute_btn.clicked.connect(self._execute_processing)
        self.execute_btn.hide()
        layout.addWidget(self.execute_btn)
        
        return section
    
    def _go_to_page1(self):
        """ページ1に遷移"""
        self.stacked_widget.setCurrentIndex(0)
        self.back_btn.setEnabled(False)
        self.next_btn.show()
        self.execute_btn.hide()
    
    def _go_to_page2(self):
        """ページ2に遷移"""
        # バリデーション（ファイルが選択されているか）
        source_file = self.source_selector.get_file_path()
        target_file = self.target_selector.get_file_path()
        output_file = self.output_selector.get_file_path()
        
        if not source_file or not target_file or not output_file:
            QMessageBox.warning(
                self,
                "入力エラー",
                "すべてのファイルを選択してください。"
            )
            return
        
        # 列がまだ設定されていない場合のみ設定
        if not self.source_columns and source_file:
            try:
                df = pd.read_excel(source_file, sheet_name=0)
                self.source_columns = list(df.columns)
                self.match_mapper.set_source_columns(self.source_columns)
                self.copy_mapper.set_source_columns(self.source_columns)
            except Exception as e:
                QMessageBox.critical(self, "エラー", f"ソースファイルの読み込みに失敗しました:\n{str(e)}")
                return
        
        if not self.target_columns and target_file:
            try:
                df = pd.read_excel(target_file, sheet_name=0)
                self.target_columns = list(df.columns)
                self.match_mapper.set_target_columns(self.target_columns)
                self.copy_mapper.set_target_columns(self.target_columns)
            except Exception as e:
                QMessageBox.critical(self, "エラー", f"ターゲットファイルの読み込みに失敗しました:\n{str(e)}")
                return
        
        self.stacked_widget.setCurrentIndex(1)
        self.back_btn.setEnabled(True)
        self.next_btn.hide()
        self.execute_btn.show()
        
        # ページ2の初期サブページをマッチング列に設定
        self.page2_stacked.setCurrentIndex(0)
        self.to_match_btn.setEnabled(False)
        self.to_copy_btn.setEnabled(True)
    
    def _create_file_section(self) -> QFrame:
        """ファイル選択セクションを作成"""
        section = QFrame()
        section.setStyleSheet(AppleStyle.get_frame_style('card'))
        layout = QVBoxLayout(section)
        layout.setSpacing(AppleStyle.SPACING['md'])
        layout.setContentsMargins(
            AppleStyle.SPACING['md'],
            AppleStyle.SPACING['md'],
            AppleStyle.SPACING['md'],
            AppleStyle.SPACING['md']
        )
        
        # セクションタイトル
        title = QLabel("ステップ1: ファイルを選択")
        title_style = AppleStyle.get_label_style('heading')
        title.setFont(title_style['font'])
        title.setStyleSheet(f"color: {title_style['color'].name()};")
        layout.addWidget(title)
        
        desc = QLabel("処理に使用するExcelファイルを選択してください")
        desc_style = AppleStyle.get_label_style('caption')
        desc.setFont(desc_style['font'])
        desc.setStyleSheet(f"color: {desc_style['color'].name()};")
        layout.addWidget(desc)
        
        # ソースファイル
        source_label = QLabel("① ソースファイル（参照元）")
        label_style = AppleStyle.get_label_style('body_bold')
        source_label.setFont(label_style['font'])
        source_label.setStyleSheet(f"color: {label_style['color'].name()};")
        layout.addWidget(source_label)
        
        source_desc = QLabel("データをコピーする元のファイル")
        source_desc.setFont(desc_style['font'])
        source_desc.setStyleSheet(f"color: {desc_style['color'].name()};")
        layout.addWidget(source_desc)
        
        self.source_selector = FileSelector(
            section,
            "",
            callback=self._on_source_file_selected
        )
        layout.addWidget(self.source_selector)
        
        # ターゲットファイル
        target_label = QLabel("② ターゲットファイル（更新対象）")
        target_label.setFont(label_style['font'])
        target_label.setStyleSheet(f"color: {label_style['color'].name()};")
        layout.addWidget(target_label)
        
        target_desc = QLabel("データを更新する対象のファイル")
        target_desc.setFont(desc_style['font'])
        target_desc.setStyleSheet(f"color: {desc_style['color'].name()};")
        layout.addWidget(target_desc)
        
        self.target_selector = FileSelector(
            section,
            "",
            callback=self._on_target_file_selected
        )
        layout.addWidget(self.target_selector)
        
        # 出力ファイル
        output_label = QLabel("③ 出力ファイル")
        output_label.setFont(label_style['font'])
        output_label.setStyleSheet(f"color: {label_style['color'].name()};")
        layout.addWidget(output_label)
        
        output_desc = QLabel("処理結果を保存するファイル")
        output_desc.setFont(desc_style['font'])
        output_desc.setStyleSheet(f"color: {desc_style['color'].name()};")
        layout.addWidget(output_desc)
        
        self.output_selector = FileSelector(
            section,
            "",
            file_types=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            save_mode=True
        )
        layout.addWidget(self.output_selector)
        
        return section
    
    def _create_page2_1(self) -> QWidget:
        """ページ2-1（マッチング列）を作成"""
        page = QWidget()
        page.setStyleSheet(f"background-color: {AppleStyle.COLORS['background'].name()};")
        layout = QVBoxLayout(page)
        layout.setSpacing(AppleStyle.SPACING['lg'])
        layout.setContentsMargins(
            AppleStyle.SPACING['md'],
            AppleStyle.SPACING['md'],
            AppleStyle.SPACING['md'],
            AppleStyle.SPACING['md']
        )
        
        # セクション
        section = QFrame()
        section.setStyleSheet(AppleStyle.get_frame_style('card'))
        section_layout = QVBoxLayout(section)
        section_layout.setSpacing(AppleStyle.SPACING['md'])
        section_layout.setContentsMargins(
            AppleStyle.SPACING['md'],
            AppleStyle.SPACING['md'],
            AppleStyle.SPACING['md'],
            AppleStyle.SPACING['md']
        )
        
        # セクションタイトル
        title = QLabel("ステップ2-1: マッチング列を設定")
        title_style = AppleStyle.get_label_style('heading')
        title.setFont(title_style['font'])
        title.setStyleSheet(f"color: {title_style['color'].name()};")
        section_layout.addWidget(title)
        
        desc = QLabel("2つのファイルで一致させる列を設定してください")
        desc_style = AppleStyle.get_label_style('caption')
        desc.setFont(desc_style['font'])
        desc.setStyleSheet(f"color: {desc_style['color'].name()};")
        section_layout.addWidget(desc)
        
        # マッチング列
        match_label = QLabel("マッチング列")
        label_style = AppleStyle.get_label_style('body_bold')
        match_label.setFont(label_style['font'])
        match_label.setStyleSheet(f"color: {label_style['color'].name()};")
        section_layout.addWidget(match_label)
        
        match_desc = QLabel("（2つのファイルで一致させる列）")
        match_desc.setFont(desc_style['font'])
        match_desc.setStyleSheet(f"color: {desc_style['color'].name()};")
        section_layout.addWidget(match_desc)
        
        self.match_mapper = ColumnMapper(
            section,
            "",
            source_columns=[],
            target_columns=[],
            callback=self._on_mapping_changed
        )
        section_layout.addWidget(self.match_mapper)
        
        layout.addWidget(section)
        layout.addStretch()
        
        return page
    
    def _create_page2_2(self) -> QWidget:
        """ページ2-2（コピー列）を作成"""
        page = QWidget()
        page.setStyleSheet(f"background-color: {AppleStyle.COLORS['background'].name()};")
        layout = QVBoxLayout(page)
        layout.setSpacing(AppleStyle.SPACING['lg'])
        layout.setContentsMargins(
            AppleStyle.SPACING['md'],
            AppleStyle.SPACING['md'],
            AppleStyle.SPACING['md'],
            AppleStyle.SPACING['md']
        )
        
        # セクション
        section = QFrame()
        section.setStyleSheet(AppleStyle.get_frame_style('card'))
        section_layout = QVBoxLayout(section)
        section_layout.setSpacing(AppleStyle.SPACING['md'])
        section_layout.setContentsMargins(
            AppleStyle.SPACING['md'],
            AppleStyle.SPACING['md'],
            AppleStyle.SPACING['md'],
            AppleStyle.SPACING['md']
        )
        
        # セクションタイトル
        title = QLabel("ステップ2-2: コピー列を設定")
        title_style = AppleStyle.get_label_style('heading')
        title.setFont(title_style['font'])
        title.setStyleSheet(f"color: {title_style['color'].name()};")
        section_layout.addWidget(title)
        
        desc = QLabel("ソースからターゲットにコピーする列を設定してください")
        desc_style = AppleStyle.get_label_style('caption')
        desc.setFont(desc_style['font'])
        desc.setStyleSheet(f"color: {desc_style['color'].name()};")
        section_layout.addWidget(desc)
        
        # コピー列
        copy_label = QLabel("コピー列")
        label_style = AppleStyle.get_label_style('body_bold')
        copy_label.setFont(label_style['font'])
        copy_label.setStyleSheet(f"color: {label_style['color'].name()};")
        section_layout.addWidget(copy_label)
        
        copy_desc = QLabel("（ソースからターゲットにコピーする列）")
        copy_desc.setFont(desc_style['font'])
        copy_desc.setStyleSheet(f"color: {desc_style['color'].name()};")
        section_layout.addWidget(copy_desc)
        
        self.copy_mapper = ColumnMapper(
            section,
            "",
            source_columns=[],
            target_columns=[],
            callback=self._on_mapping_changed
        )
        section_layout.addWidget(self.copy_mapper)
        
        layout.addWidget(section)
        layout.addStretch()
        
        return page
    
    def _create_page2_navigation(self) -> QFrame:
        """ページ2内のナビゲーションセクションを作成"""
        section = QFrame()
        layout = QHBoxLayout(section)
        layout.setSpacing(AppleStyle.SPACING['md'])
        
        # マッチング列へボタン
        self.to_match_btn = QPushButton("← マッチング列")
        self.to_match_btn.setStyleSheet(AppleStyle.get_button_style('secondary'))
        self.to_match_btn.setEnabled(False)  # 初期状態では無効（マッチング列ページにいるため）
        self.to_match_btn.clicked.connect(self._go_to_page2_1)
        layout.addWidget(self.to_match_btn)
        
        layout.addStretch()
        
        # コピー列へボタン
        self.to_copy_btn = QPushButton("コピー列 →")
        self.to_copy_btn.setStyleSheet(AppleStyle.get_button_style('primary'))
        self.to_copy_btn.clicked.connect(self._go_to_page2_2)
        layout.addWidget(self.to_copy_btn)
        
        return section
    
    def _go_to_page2_1(self):
        """ページ2-1（マッチング列）に遷移"""
        self.page2_stacked.setCurrentIndex(0)
        self.to_match_btn.setEnabled(False)
        self.to_copy_btn.setEnabled(True)
    
    def _go_to_page2_2(self):
        """ページ2-2（コピー列）に遷移"""
        self.page2_stacked.setCurrentIndex(1)
        self.to_match_btn.setEnabled(True)
        self.to_copy_btn.setEnabled(False)
    
    
    def _on_source_file_selected(self, file_path: str):
        """ソースファイルが選択されたときの処理"""
        try:
            df = pd.read_excel(file_path, sheet_name=0)
            self.source_columns = list(df.columns)
            # set_source_columnsは既存のマッピングを保持する
            self.match_mapper.set_source_columns(self.source_columns)
            self.copy_mapper.set_source_columns(self.source_columns)
        except Exception as e:
            QMessageBox.critical(self, "エラー", f"ファイルの読み込みに失敗しました:\n{str(e)}")
    
    def _on_target_file_selected(self, file_path: str):
        """ターゲットファイルが選択されたときの処理"""
        try:
            df = pd.read_excel(file_path, sheet_name=0)
            self.target_columns = list(df.columns)
            # set_target_columnsは既存のマッピングを保持する
            self.match_mapper.set_target_columns(self.target_columns)
            self.copy_mapper.set_target_columns(self.target_columns)
        except Exception as e:
            QMessageBox.critical(self, "エラー", f"ファイルの読み込みに失敗しました:\n{str(e)}")
    
    def _on_mapping_changed(self):
        """マッピングが変更されたときの処理"""
        pass
    
    def _validate_inputs(self) -> tuple[bool, Optional[str]]:
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
            QMessageBox.critical(self, "入力エラー", error_message)
            return
        
        # UIを無効化
        self.execute_btn.setEnabled(False)
        self.progress.show("処理を開始しています...")
        
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
        
        # ワーカースレッドを作成
        self.worker = VLookupWorker(config)
        self.worker_thread = QThread()
        
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.started.connect(self.worker.run)
        self.worker.finished.connect(self._on_processing_finished)
        self.worker.error.connect(self._on_processing_error)
        
        self.worker_thread.start()
    
    def _on_processing_finished(self, result: Dict[str, Any]):
        """処理完了時の処理"""
        self.progress.hide()
        self.execute_btn.setEnabled(True)
        
        if self.worker_thread:
            self.worker_thread.quit()
            self.worker_thread.wait()
        
        if result['success']:
            QMessageBox.information(
                self,
                "成功",
                f"処理が完了しました！\n\n"
                f"マッチした行数: {result['matched_count']}\n"
                f"ソースファイル行数: {result['source_rows']}\n"
                f"ターゲットファイル行数: {result['target_rows']}\n"
                f"出力ファイル: {result['output_file']}"
            )
        else:
            QMessageBox.critical(self, "エラー", result['message'])
    
    def _on_processing_error(self, error_message: str):
        """処理エラー時の処理"""
        self.progress.hide()
        self.execute_btn.setEnabled(True)
        
        if self.worker_thread:
            self.worker_thread.quit()
            self.worker_thread.wait()
        
        QMessageBox.critical(self, "エラー", f"処理中にエラーが発生しました:\n{error_message}")
    
    def closeEvent(self, event):
        """ウィンドウを閉じるときの処理"""
        if self.worker_thread and self.worker_thread.isRunning():
            if self.worker:
                # ワーカーを停止（可能な場合）
                pass
            self.worker_thread.quit()
            self.worker_thread.wait()
        event.accept()

