#!/usr/bin/env python3
"""
Excel Tool Suite - Main Entry Point (PyQt6版)
統合メインエントリーポイント（PyQt6版）
複数のExcelツール機能を統合管理
"""

import sys
from pathlib import Path
from typing import Optional

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import QApplication, QMainWindow
from gui_qt.styles import AppleStyle
from gui_qt import LauncherWindow, ReaderWindow, SearchWindow, MergeWindow, VLookupWindow


class MainApplication(QMainWindow):
    """メインアプリケーションクラス（PyQt6版）"""
    
    def __init__(self):
        super().__init__()
        self.current_window: Optional[QMainWindow] = None
        self.launcher: Optional[LauncherWindow] = None
        self._show_launcher()
    
    def _show_launcher(self):
        """ランチャーを表示"""
        # 既存のツールウィンドウを閉じる
        if self.current_window:
            self.current_window.close()
            self.current_window = None
        
        # ランチャーが既に存在する場合は表示、なければ作成
        if self.launcher is None:
            self.launcher = LauncherWindow(self)
            self.launcher.feature_selected.connect(self._on_feature_selected)
            self.launcher.finished.connect(self._on_launcher_closed)
        
        self.launcher.show()
        self.launcher.raise_()
        self.launcher.activateWindow()
    
    def _on_launcher_closed(self, result):
        """ランチャーが閉じられたときの処理"""
        # ランチャーが閉じられた場合はアプリを終了
        if result == LauncherWindow.DialogCode.Rejected:
            QApplication.instance().quit()
    
    def _on_feature_selected(self, feature: str):
        """機能が選択されたときの処理"""
        # ランチャーを非表示
        if self.launcher:
            self.launcher.hide()
        
        # 機能ウィンドウを開く
        self._open_feature(feature)
    
    def _open_feature(self, feature: str):
        """機能ウィンドウを開く"""
        if self.current_window:
            self.current_window.close()
            self.current_window = None
        
        if feature == 'reader':
            self.current_window = ReaderWindow(self, on_home_click=self._show_launcher)
            self.current_window.finished.connect(lambda: self._on_window_closed())
            self.current_window.show()
        elif feature == 'vlookup':
            self.current_window = VLookupWindow(self, on_home_click=self._show_launcher)
            self.current_window.finished.connect(lambda: self._on_window_closed())
            self.current_window.show()
        elif feature == 'search':
            self.current_window = SearchWindow(self, on_home_click=self._show_launcher)
            self.current_window.finished.connect(lambda: self._on_window_closed())
            self.current_window.show()
        elif feature == 'merge':
            self.current_window = MergeWindow(self, on_home_click=self._show_launcher)
            self.current_window.finished.connect(lambda: self._on_window_closed())
            self.current_window.show()
    
    def _on_window_closed(self):
        """ウィンドウが閉じられたときの処理"""
        if self.current_window:
            self.current_window = None
        # ランチャーに戻る
        self._show_launcher()


def main():
    """メイン関数"""
    app = QApplication(sys.argv)
    
    # グローバルスタイルを適用
    AppleStyle.apply_global_style(app)
    
    # メインアプリケーションを表示
    main_app = MainApplication()
    main_app.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()

