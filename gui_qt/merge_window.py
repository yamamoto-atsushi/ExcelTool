"""
Merge Window - Excelファイル統合機能のGUI (PyQt6版)
分割されたExcelファイルを統合する機能専用のウィンドウ
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFileDialog, QLineEdit, QMessageBox, QFrame, QRadioButton,
    QCheckBox, QButtonGroup
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QObject
from pathlib import Path
from typing import Optional, Dict, Any, Callable
import sys

from gui_qt.styles import AppleStyle
from gui_qt.components import ProgressIndicator


class MergeWorker(QObject):
    """統合処理を実行するワーカースレッド"""
    
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, config: dict):
        super().__init__()
        self.config = config
    
    def run(self):
        """統合処理を実行"""
        try:
            # ExcelMergerをインポート
            project_root = Path(__file__).parent.parent
            sys.path.insert(0, str(project_root))
            
            from core.excel_merger import ExcelMerger
            
            # ツール実行
            merger = ExcelMerger(self.config)
            result = merger.merge()
            
            self.finished.emit(result)
            
        except Exception as e:
            self.error.emit(str(e))


class MergeWindow(QDialog):
    """Excelファイル統合ウィンドウ（PyQt6版）"""
    
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
        
        self.setWindowTitle("Excel ファイル統合")
        self.resize(700, 650)
        
        self.on_home_click = on_home_click
        self.worker: Optional[MergeWorker] = None
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
        title_label = QLabel("Excel ファイル統合")
        title_style = AppleStyle.get_label_style('title')
        title_label.setFont(title_style['font'])
        title_label.setStyleSheet(f"color: {title_style['color'].name()};")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # サブタイトル
        subtitle_label = QLabel("分割されたExcelファイルを統合して1つのファイルにします")
        subtitle_style = AppleStyle.get_label_style('caption')
        subtitle_label.setFont(subtitle_style['font'])
        subtitle_label.setStyleSheet(f"color: {subtitle_style['color'].name()};")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(subtitle_label)
        
        # 設定セクション
        settings_section = self._create_settings_section()
        main_layout.addWidget(settings_section)
        
        # 実行ボタン
        button_section = self._create_button_section()
        main_layout.addWidget(button_section)
        
        # 進捗表示
        self.progress = ProgressIndicator(self)
        main_layout.addWidget(self.progress)
        
        main_layout.addStretch()
    
    def _create_settings_section(self) -> QFrame:
        """設定セクションを作成"""
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
        
        label_style = AppleStyle.get_label_style('body_bold')
        
        # 入力タイプ選択
        input_type_label = QLabel("入力タイプ:")
        input_type_label.setFont(label_style['font'])
        input_type_label.setStyleSheet(f"color: {label_style['color'].name()};")
        layout.addWidget(input_type_label)
        
        type_layout = QHBoxLayout()
        self.input_type_group = QButtonGroup(self)
        
        folder_radio = QRadioButton("フォルダを指定")
        folder_radio.setChecked(True)
        self.input_type_group.addButton(folder_radio, 0)
        type_layout.addWidget(folder_radio)
        
        file_radio = QRadioButton("ファイルを指定（複数選択可）")
        self.input_type_group.addButton(file_radio, 1)
        type_layout.addWidget(file_radio)
        
        type_layout.addStretch()
        layout.addLayout(type_layout)
        
        # 入力パス
        input_path_label = QLabel("入力パス:")
        input_path_label.setFont(label_style['font'])
        input_path_label.setStyleSheet(f"color: {label_style['color'].name()};")
        layout.addWidget(input_path_label)
        
        input_path_hint = QLabel("統合するExcelファイルを含むフォルダ、または統合するExcelファイルを選択してください")
        hint_style = AppleStyle.get_label_style('caption')
        input_path_hint.setFont(hint_style['font'])
        input_path_hint.setStyleSheet(f"color: {hint_style['color'].name()};")
        input_path_hint.setWordWrap(True)
        layout.addWidget(input_path_hint)
        
        input_path_layout = QHBoxLayout()
        self.input_path_edit = QLineEdit()
        self.input_path_edit.setStyleSheet(AppleStyle.get_entry_style())
        self.input_path_edit.setPlaceholderText("入力パスを選択...")
        input_path_layout.addWidget(self.input_path_edit)
        
        self.browse_btn = QPushButton("参照...")
        self.browse_btn.setStyleSheet(AppleStyle.get_button_style('secondary'))
        self.browse_btn.clicked.connect(self._browse_input_path)
        input_path_layout.addWidget(self.browse_btn)
        
        layout.addLayout(input_path_layout)
        
        # シート名
        sheet_label = QLabel("シート名（番号または名前）:")
        sheet_label.setFont(label_style['font'])
        sheet_label.setStyleSheet(f"color: {label_style['color'].name()};")
        layout.addWidget(sheet_label)
        
        sheet_hint = QLabel("統合するシートを指定します（デフォルト: 0 = 最初のシート）")
        sheet_hint.setFont(hint_style['font'])
        sheet_hint.setStyleSheet(f"color: {hint_style['color'].name()};")
        layout.addWidget(sheet_hint)
        
        self.sheet_edit = QLineEdit("0")
        self.sheet_edit.setStyleSheet(AppleStyle.get_entry_style())
        layout.addWidget(self.sheet_edit)
        
        # オプション
        options_label = QLabel("オプション:")
        options_label.setFont(label_style['font'])
        options_label.setStyleSheet(f"color: {label_style['color'].name()};")
        layout.addWidget(options_label)
        
        self.recursive_check = QCheckBox("サブフォルダも検索する")
        layout.addWidget(self.recursive_check)
        
        self.include_header_check = QCheckBox("すべてのファイルでヘッダーを含める（最初のファイルのみでない）")
        self.include_header_check.setChecked(True)
        layout.addWidget(self.include_header_check)
        
        # 出力ファイル
        output_label = QLabel("出力ファイル:")
        output_label.setFont(label_style['font'])
        output_label.setStyleSheet(f"color: {label_style['color'].name()};")
        layout.addWidget(output_label)
        
        output_layout = QHBoxLayout()
        self.output_path_edit = QLineEdit()
        self.output_path_edit.setStyleSheet(AppleStyle.get_entry_style())
        self.output_path_edit.setPlaceholderText("出力ファイルを指定...")
        output_layout.addWidget(self.output_path_edit)
        
        output_browse_btn = QPushButton("参照...")
        output_browse_btn.setStyleSheet(AppleStyle.get_button_style('secondary'))
        output_browse_btn.clicked.connect(self._browse_output_file)
        output_layout.addWidget(output_browse_btn)
        
        layout.addLayout(output_layout)
        
        return section
    
    def _create_button_section(self) -> QFrame:
        """ボタンセクションを作成"""
        section = QFrame()
        layout = QHBoxLayout(section)
        layout.addStretch()
        
        self.execute_btn = QPushButton("▶ 統合を実行")
        self.execute_btn.setStyleSheet(AppleStyle.get_button_style('primary'))
        self.execute_btn.setFont(AppleStyle.FONTS['body_bold'])
        self.execute_btn.clicked.connect(self._execute_merge)
        layout.addWidget(self.execute_btn)
        
        layout.addStretch()
        
        return section
    
    def _browse_input_path(self):
        """入力パス選択ダイアログを表示"""
        input_type = self.input_type_group.checkedId()
        
        if input_type == 0:  # フォルダ
            folder_path = QFileDialog.getExistingDirectory(
                self,
                "統合するExcelファイルを含むフォルダを選択"
            )
            if folder_path:
                self.input_path_edit.setText(folder_path)
        else:  # ファイル
            file_paths, _ = QFileDialog.getOpenFileNames(
                self,
                "統合するExcelファイルを選択",
                "",
                "Excel Files (*.xlsx *.xlsm *.xls);;All Files (*)"
            )
            if file_paths:
                # 複数ファイルのパスをセミコロンで区切って保存
                self.input_path_edit.setText(';'.join(file_paths))
    
    def _browse_output_file(self):
        """出力ファイル選択ダイアログを表示"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "統合結果を保存",
            "",
            "Excel Files (*.xlsx);;All Files (*)"
        )
        if file_path:
            self.output_path_edit.setText(file_path)
    
    def _validate_inputs(self) -> tuple[bool, Optional[str]]:
        """入力の検証"""
        input_path = self.input_path_edit.text().strip()
        output_path = self.output_path_edit.text().strip()
        
        if not input_path:
            return False, "入力パスを指定してください"
        
        input_type = self.input_type_group.checkedId()
        if input_type == 0:  # フォルダ
            if not Path(input_path).exists():
                return False, "入力フォルダが見つかりません"
            if not Path(input_path).is_dir():
                return False, "入力パスはフォルダである必要があります"
        else:  # ファイル
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
            QMessageBox.critical(self, "入力エラー", error_message)
            return
        
        # UIを無効化
        self.execute_btn.setEnabled(False)
        self.progress.show("統合を開始しています...")
        
        # 設定を作成
        input_path = self.input_path_edit.text().strip()
        input_type = self.input_type_group.checkedId()
        
        # シート名の処理
        sheet_name = self.sheet_edit.text().strip()
        try:
            sheet_name = int(sheet_name)
        except ValueError:
            pass  # 文字列として使用
        
        config = {}
        
        if input_type == 1:  # ファイル
            file_paths = [p.strip() for p in input_path.split(';') if p.strip()]
            if file_paths:
                config['input_files'] = file_paths
            else:
                QMessageBox.critical(self, "エラー", "入力ファイルが指定されていません")
                self.execute_btn.setEnabled(True)
                self.progress.hide()
                return
        else:  # フォルダ
            config['input_path'] = input_path
        
        config.update({
            'output_file': self.output_path_edit.text().strip(),
            'sheet_name': sheet_name,
            'recursive': self.recursive_check.isChecked(),
            'include_header': self.include_header_check.isChecked(),
        })
        
        # ワーカースレッドを作成
        self.worker = MergeWorker(config)
        self.worker_thread = QThread()
        
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.started.connect(self.worker.run)
        self.worker.finished.connect(self._on_merge_finished)
        self.worker.error.connect(self._on_merge_error)
        
        self.worker_thread.start()
    
    def _on_merge_finished(self, result: Dict[str, Any]):
        """統合完了時の処理"""
        self.progress.hide()
        self.execute_btn.setEnabled(True)
        
        if self.worker_thread:
            self.worker_thread.quit()
            self.worker_thread.wait()
        
        if result['success']:
            QMessageBox.information(
                self,
                "成功",
                f"統合が完了しました。\n\n"
                f"処理ファイル数: {result['files_processed']}個\n"
                f"総行数: {result['total_rows']}行\n"
                f"出力ファイル: {result['output_file']}"
            )
        else:
            QMessageBox.critical(self, "エラー", f"統合処理中にエラーが発生しました:\n{result['message']}")
    
    def _on_merge_error(self, error_message: str):
        """統合エラー時の処理"""
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

