"""
Launcher Window - 機能選択画面 (PyQt6版)
複数のExcelツール機能を選択するためのランチャー
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QGridLayout, QLabel, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QMouseEvent
from typing import Optional
from gui_qt.styles import AppleStyle


class FeatureTile(QFrame):
    """機能タイル（カード形式）"""
    
    clicked = pyqtSignal()
    
    def __init__(self, parent=None, title: str = "", subtitle: str = "", 
                 icon: str = "", detail: str = ""):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self._create_widgets(title, subtitle, icon, detail)
        self._setup_style()
    
    def _create_widgets(self, title: str, subtitle: str, icon: str, detail: str):
        """ウィジェットを作成"""
        layout = QVBoxLayout(self)
        layout.setSpacing(AppleStyle.SPACING['md'])
        layout.setContentsMargins(
            AppleStyle.SPACING['lg'],
            AppleStyle.SPACING['lg'],
            AppleStyle.SPACING['lg'],
            AppleStyle.SPACING['lg']
        )
        
        # アイコンとタイトルを横並びに配置
        header_layout = QVBoxLayout()
        header_layout.setSpacing(AppleStyle.SPACING['md'])
        
        # アイコンとタイトル
        icon_title_layout = QVBoxLayout()
        icon_title_layout.setSpacing(AppleStyle.SPACING['sm'])
        
        # アイコン
        icon_label = QLabel(icon)
        icon_label.setFont(AppleStyle.FONTS['title'])
        icon_label.setStyleSheet(f"color: {AppleStyle.COLORS['primary'].name()};")
        icon_title_layout.addWidget(icon_label)
        
        # タイトル
        title_label = QLabel(title)
        title_style = AppleStyle.get_label_style('heading')
        title_label.setFont(title_style['font'])
        title_label.setStyleSheet(f"color: {title_style['color'].name()};")
        icon_title_layout.addWidget(title_label)
        
        header_layout.addLayout(icon_title_layout)
        
        # サブタイトル
        subtitle_label = QLabel(subtitle)
        subtitle_style = AppleStyle.get_label_style('body')
        subtitle_label.setFont(subtitle_style['font'])
        subtitle_label.setStyleSheet(f"color: {subtitle_style['color'].name()};")
        subtitle_label.setWordWrap(True)
        header_layout.addWidget(subtitle_label)
        
        # 詳細説明
        if detail:
            detail_label = QLabel(detail)
            detail_style = AppleStyle.get_label_style('caption')
            detail_label.setFont(detail_style['font'])
            detail_label.setStyleSheet(f"color: {detail_style['color'].name()};")
            detail_label.setWordWrap(True)
            header_layout.addWidget(detail_label)
        
        layout.addLayout(header_layout)
        layout.addStretch()
    
    def _setup_style(self):
        """スタイルを設定"""
        self.setStyleSheet(AppleStyle.get_frame_style('card') + """
            QFrame {
                border: none;
            }
        """)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
    
    def mousePressEvent(self, event: QMouseEvent):
        """マウスクリックイベント"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)
    
    def enterEvent(self, event):
        """マウスが入ったとき"""
        self.setStyleSheet(AppleStyle.get_frame_style('card') + f"""
            QFrame {{
                background-color: {AppleStyle.COLORS['background'].name()};
                border: none;
            }}
        """)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """マウスが出たとき"""
        self.setStyleSheet(AppleStyle.get_frame_style('card') + """
            QFrame {
                border: none;
            }
        """)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        super().leaveEvent(event)


class LauncherWindow(QDialog):
    """機能選択ランチャーウィンドウ（PyQt6版）"""
    
    feature_selected = pyqtSignal(str)
    
    def __init__(self, parent=None):
        """
        初期化
        
        Args:
            parent: 親ウィンドウ（Noneの場合は独立ウィンドウ）
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
        
        self.setWindowTitle("Excel Tool Suite")
        self.resize(800, 600)
        
        # 選択された機能
        self.selected_feature: Optional[str] = None
        
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
        title_label = QLabel("Excel Tool Suite")
        title_style = AppleStyle.get_label_style('title')
        title_label.setFont(title_style['font'])
        title_label.setStyleSheet(f"color: {title_style['color'].name()};")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # サブタイトル
        subtitle_label = QLabel("使用する機能を選択してください")
        subtitle_style = AppleStyle.get_label_style('caption')
        subtitle_label.setFont(subtitle_style['font'])
        subtitle_label.setStyleSheet(f"color: {subtitle_style['color'].name()};")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(subtitle_label)
        
        # タイル表示セクション
        tiles_layout = QGridLayout()
        tiles_layout.setSpacing(AppleStyle.SPACING['md'])
        
        # 機能1: VLOOKUP風機能
        vlookup_tile = FeatureTile(
            self,
            "VLOOKUP風機能",
            "2つのExcelファイルを比較してデータをコピー",
            "📊",
            "複数のキーワード列でマッチングし、指定列のデータをコピーします"
        )
        vlookup_tile.clicked.connect(lambda: self._select_feature('vlookup'))
        tiles_layout.addWidget(vlookup_tile, 0, 0)
        
        # 機能2: キーワード検索機能
        search_tile = FeatureTile(
            self,
            "キーワード検索",
            "Excelファイルからキーワードを検索",
            "🔍",
            "指定フォルダ内のExcelファイルからキーワードを検索して結果を出力します"
        )
        search_tile.clicked.connect(lambda: self._select_feature('search'))
        tiles_layout.addWidget(search_tile, 0, 1)
        
        # 機能3: ファイル統合機能
        merge_tile = FeatureTile(
            self,
            "ファイル統合",
            "分割されたExcelファイルを統合して1つに",
            "📋",
            "フォルダ内のExcelファイルまたは複数のExcelファイルを統合して1つのファイルにします"
        )
        merge_tile.clicked.connect(lambda: self._select_feature('merge'))
        tiles_layout.addWidget(merge_tile, 1, 0)
        
        # 機能4: 読み上げ機能
        reader_tile = FeatureTile(
            self,
            "読み上げ機能",
            "Excelファイルの内容を音声で読み上げ",
            "🔊",
            "Excelファイルの内容を音声で読み上げます（音声エンジンが必要です）"
        )
        reader_tile.clicked.connect(lambda: self._select_feature('reader'))
        tiles_layout.addWidget(reader_tile, 1, 1)
        
        # グリッドの重みを設定
        tiles_layout.setColumnStretch(0, 1)
        tiles_layout.setColumnStretch(1, 1)
        tiles_layout.setRowStretch(0, 1)
        tiles_layout.setRowStretch(1, 1)
        
        main_layout.addLayout(tiles_layout)
        main_layout.addStretch()
    
    def _select_feature(self, feature: str):
        """機能を選択"""
        self.selected_feature = feature
        self.feature_selected.emit(feature)
        self.hide()  # 非表示にする（閉じない）
    
    def closeEvent(self, event):
        """ウィンドウを閉じるときの処理"""
        self.selected_feature = None
        self.reject()  # アプリケーションを終了する
        event.accept()

