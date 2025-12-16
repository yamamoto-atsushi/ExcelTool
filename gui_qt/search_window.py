"""
Search Window - キーワード検索機能のGUI (PyQt6版)
Excelファイルキーワード検索機能専用のウィンドウ
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFileDialog, QTextEdit, QLineEdit, QMessageBox, QFrame, QCheckBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QObject
from pathlib import Path
from typing import Optional, Callable
import sys

from gui_qt.styles import AppleStyle
from gui_qt.components import ProgressIndicator


class SearchWorker(QObject):
    """検索処理を実行するワーカースレッド"""
    
    finished = pyqtSignal()
    error = pyqtSignal(str)
    
    def __init__(self, config: dict):
        super().__init__()
        self.config = config
    
    def run(self):
        """検索処理を実行"""
        try:
            # ExcelSearchToolをインポート
            project_root = Path(__file__).parent.parent
            sys.path.insert(0, str(project_root))
            
            from excel_search import ExcelSearchTool
            
            # ツール実行
            tool = ExcelSearchTool(self.config)
            tool.execute()
            
            self.finished.emit()
            
        except Exception as e:
            self.error.emit(str(e))


class SearchWindow(QDialog):
    """キーワード検索ウィンドウ（PyQt6版）"""
    
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
        
        self.setWindowTitle("Excel キーワード検索")
        self.resize(700, 650)
        
        self.on_home_click = on_home_click
        self.worker: Optional[SearchWorker] = None
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
        title_label = QLabel("Excel キーワード検索")
        title_style = AppleStyle.get_label_style('title')
        title_label.setFont(title_style['font'])
        title_label.setStyleSheet(f"color: {title_style['color'].name()};")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # サブタイトル
        subtitle_label = QLabel("指定フォルダ内のExcelファイルからキーワードを検索します")
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
        
        # 検索パス
        path_label = QLabel("検索フォルダ:")
        label_style = AppleStyle.get_label_style('body_bold')
        path_label.setFont(label_style['font'])
        path_label.setStyleSheet(f"color: {label_style['color'].name()};")
        layout.addWidget(path_label)
        
        path_layout = QHBoxLayout()
        self.search_path_edit = QLineEdit()
        self.search_path_edit.setStyleSheet(AppleStyle.get_entry_style())
        self.search_path_edit.setPlaceholderText("検索フォルダを選択...")
        path_layout.addWidget(self.search_path_edit)
        
        browse_btn = QPushButton("参照...")
        browse_btn.setStyleSheet(AppleStyle.get_button_style('secondary'))
        browse_btn.clicked.connect(self._browse_folder)
        path_layout.addWidget(browse_btn)
        
        layout.addLayout(path_layout)
        
        # サブフォルダも検索するチェックボックス
        self.recursive_checkbox = QCheckBox("下層フォルダも検索対象にする")
        checkbox_style = AppleStyle.get_label_style('body')
        self.recursive_checkbox.setFont(checkbox_style['font'])
        self.recursive_checkbox.setStyleSheet(f"""
            QCheckBox {{
                color: {checkbox_style['color'].name()};
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
            }}
        """)
        self.recursive_checkbox.setChecked(True)  # デフォルトで有効
        layout.addWidget(self.recursive_checkbox)
        
        # キーワード
        keywords_label = QLabel("検索キーワード（1行に1つ）:")
        keywords_label.setFont(label_style['font'])
        keywords_label.setStyleSheet(f"color: {label_style['color'].name()};")
        layout.addWidget(keywords_label)
        
        self.keywords_text = QTextEdit()
        # 入力エリアであることがわかりやすいスタイルを適用
        entry_style = AppleStyle.get_entry_style()
        self.keywords_text.setStyleSheet(f"""
            QTextEdit {{
                {entry_style}
                background-color: #FFFFFF;
                border: 1px solid #007AFF;
                border-radius: 4px;
                padding: 8px;
            }}
            QTextEdit:focus {{
                border: 2px solid #007AFF;
                background-color: #F5F5F7;
            }}
        """)
        self.keywords_text.setPlaceholderText("キーワードを1行に1つずつ入力してください\n（すべてのキーワードが含まれるファイルが検索されます）")
        self.keywords_text.setMinimumHeight(120)
        layout.addWidget(self.keywords_text)
        
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
        
        self.execute_btn = QPushButton("▶ 検索を開始")
        self.execute_btn.setStyleSheet(AppleStyle.get_button_style('primary'))
        self.execute_btn.setFont(AppleStyle.FONTS['body_bold'])
        self.execute_btn.clicked.connect(self._execute_search)
        layout.addWidget(self.execute_btn)
        
        layout.addStretch()
        
        return section
    
    def _browse_folder(self):
        """フォルダ選択ダイアログを表示"""
        folder_path = QFileDialog.getExistingDirectory(self, "検索フォルダを選択")
        if folder_path:
            self.search_path_edit.setText(folder_path)
    
    def _browse_output_file(self):
        """出力ファイル選択ダイアログを表示"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "出力ファイルを保存",
            "",
            "Excel Files (*.xlsx);;CSV Files (*.csv);;All Files (*)"
        )
        if file_path:
            self.output_path_edit.setText(file_path)
    
    def _validate_inputs(self) -> tuple[bool, Optional[str]]:
        """入力の検証"""
        search_path = self.search_path_edit.text().strip()
        keywords_text = self.keywords_text.toPlainText().strip()
        output_path = self.output_path_edit.text().strip()
        
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
            QMessageBox.critical(self, "入力エラー", error_message)
            return
        
        # UIを無効化
        self.execute_btn.setEnabled(False)
        self.progress.show("検索を開始しています...")
        
        # 設定を作成
        keywords = [k.strip() for k in self.keywords_text.toPlainText().strip().split('\n') if k.strip()]
        
        config = {
            'search_path': self.search_path_edit.text().strip(),
            'keywords': keywords,
            'output_file': self.output_path_edit.text().strip(),
            'recursive': self.recursive_checkbox.isChecked(),
            'max_workers': 4,
            'case_sensitive': False,
        }
        
        # ワーカースレッドを作成
        self.worker = SearchWorker(config)
        self.worker_thread = QThread()
        
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.started.connect(self.worker.run)
        self.worker.finished.connect(self._on_search_finished)
        self.worker.error.connect(self._on_search_error)
        
        self.worker_thread.start()
    
    def _on_search_finished(self):
        """検索完了時の処理"""
        self.progress.hide()
        self.execute_btn.setEnabled(True)
        
        if self.worker_thread:
            self.worker_thread.quit()
            self.worker_thread.wait()
        
        QMessageBox.information(
            self,
            "成功",
            f"検索が完了しました。\n結果を保存しました: {self.output_path_edit.text()}"
        )
    
    def _on_search_error(self, error_message: str):
        """検索エラー時の処理"""
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

