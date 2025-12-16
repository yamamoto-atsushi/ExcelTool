#!/usr/bin/env python3
"""
Excel Tool Suite - Main Entry Point
統合メインエントリーポイント
複数のExcelツール機能を統合管理
"""

import sys
import os
import tkinter as tk
from pathlib import Path
from typing import Optional

# Windowsでコンソールウィンドウを非表示にする
if sys.platform == 'win32':
    import ctypes
    # コンソールウィンドウを非表示にする
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from gui.launcher import LauncherWindow
from gui.main_window import VLookupWindow
from gui.search_window import SearchWindow
from gui.merge_window import MergeWindow
from gui.reader_window import ReaderWindow
from gui.menu_bar import MenuBar


class MainApplication:
    """メインアプリケーションクラス"""
    
    def __init__(self):
        """初期化"""
        self.root = tk.Tk()
        self.root.withdraw()  # 最初は非表示
        
        self.current_window: Optional[tk.Toplevel] = None
        self.launcher: Optional[LauncherWindow] = None
        
        # ランチャーを表示
        self.show_launcher()
    
    def show_launcher(self):
        """ランチャーを表示"""
        # #region agent log
        import json
        with open(r'c:\Users\ayama\Python\ExcelTool\.cursor\debug.log', 'a', encoding='utf-8') as f:
            f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"A,B,C,D,E","location":"app.py:37","message":"show_launcher entry","data":{"current_window_exists":self.current_window is not None,"launcher_exists":self.launcher is not None},"timestamp":int(__import__('time').time()*1000)})+'\n')
        # #endregion
        if self.current_window:
            self.current_window.destroy()
            self.current_window = None
        
        # ルートウィンドウにメニューバーを設定
        self.menu_bar = MenuBar(self.root, on_feature_select=self._on_feature_selected)
        
        # 既存のランチャーがあれば破棄
        if self.launcher:
            try:
                self.launcher.destroy()
            except:
                pass
        
        self.launcher = LauncherWindow(self.root)
        self.launcher.protocol("WM_DELETE_WINDOW", self._on_launcher_close)
        
        # #region agent log
        with open(r'c:\Users\ayama\Python\ExcelTool\.cursor\debug.log', 'a', encoding='utf-8') as f:
            f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"A,B","location":"app.py:57","message":"before wait_window","data":{"launcher_exists":self.launcher is not None},"timestamp":int(__import__('time').time()*1000)})+'\n')
        # #endregion
        
        # ランチャーが閉じられるまで待機
        self.root.wait_window(self.launcher)
        
        # #region agent log
        with open(r'c:\Users\ayama\Python\ExcelTool\.cursor\debug.log', 'a', encoding='utf-8') as f:
            f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"E","location":"app.py:60","message":"after wait_window","data":{"launcher_exists":self.launcher is not None,"selected_feature":getattr(self.launcher,'selected_feature',None) if self.launcher else None},"timestamp":int(__import__('time').time()*1000)})+'\n')
        # #endregion
        
        # ランチャーが閉じられた後の処理
        selected = self.launcher.selected_feature
        if selected:
            # #region agent log
            with open(r'c:\Users\ayama\Python\ExcelTool\.cursor\debug.log', 'a', encoding='utf-8') as f:
                f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"C","location":"app.py:62","message":"calling _open_feature","data":{"feature":selected},"timestamp":int(__import__('time').time()*1000)})+'\n')
            # #endregion
            self._open_feature(selected)
        else:
            # 何も選択されなかった場合はアプリを終了
            self.root.quit()
            self.root.destroy()
    
    def _on_launcher_close(self):
        """ランチャーが閉じられたときの処理"""
        # #region agent log
        import json
        with open(r'c:\Users\ayama\Python\ExcelTool\.cursor\debug.log', 'a', encoding='utf-8') as f:
            f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"D","location":"app.py:68","message":"_on_launcher_close called","data":{},"timestamp":int(__import__('time').time()*1000)})+'\n')
        # #endregion
        self.launcher.selected_feature = None
        self.launcher.withdraw()
        # #region agent log
        with open(r'c:\Users\ayama\Python\ExcelTool\.cursor\debug.log', 'a', encoding='utf-8') as f:
            f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"D","location":"app.py:71","message":"after withdraw in _on_launcher_close","data":{},"timestamp":int(__import__('time').time()*1000)})+'\n')
        # #endregion
    
    def _on_feature_selected(self, feature: str):
        """メニューから機能が選択されたときの処理"""
        if self.launcher:
            self.launcher.destroy()
            self.launcher = None
        
        if feature == 'launcher':
            self.show_launcher()
        else:
            self._open_feature(feature)
    
    def _open_feature(self, feature: str):
        """機能ウィンドウを開く"""
        # #region agent log
        import json
        with open(r'c:\Users\ayama\Python\ExcelTool\.cursor\debug.log', 'a', encoding='utf-8') as f:
            f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"C","location":"app.py:84","message":"_open_feature entry","data":{"feature":feature},"timestamp":int(__import__('time').time()*1000)})+'\n')
        # #endregion
        if self.current_window:
            self.current_window.destroy()
        
        if feature == 'vlookup':
            # #region agent log
            with open(r'c:\Users\ayama\Python\ExcelTool\.cursor\debug.log', 'a', encoding='utf-8') as f:
                f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"C","location":"app.py:90","message":"creating VLookupWindow","data":{},"timestamp":int(__import__('time').time()*1000)})+'\n')
            # #endregion
            self.current_window = VLookupWindow(self.root, on_home_click=self.show_launcher)
            self.current_window.protocol("WM_DELETE_WINDOW", self._on_window_close)
            # #region agent log
            with open(r'c:\Users\ayama\Python\ExcelTool\.cursor\debug.log', 'a', encoding='utf-8') as f:
                f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"C","location":"app.py:92","message":"calling mainloop on VLookupWindow","data":{},"timestamp":int(__import__('time').time()*1000)})+'\n')
            # #endregion
            self.current_window.mainloop()
        elif feature == 'search':
            # #region agent log
            with open(r'c:\Users\ayama\Python\ExcelTool\.cursor\debug.log', 'a', encoding='utf-8') as f:
                f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"C","location":"app.py:94","message":"creating SearchWindow","data":{},"timestamp":int(__import__('time').time()*1000)})+'\n')
            # #endregion
            self.current_window = SearchWindow(self.root, on_home_click=self.show_launcher)
            self.current_window.protocol("WM_DELETE_WINDOW", self._on_window_close)
            # #region agent log
            with open(r'c:\Users\ayama\Python\ExcelTool\.cursor\debug.log', 'a', encoding='utf-8') as f:
                f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"C","location":"app.py:96","message":"calling mainloop on SearchWindow","data":{},"timestamp":int(__import__('time').time()*1000)})+'\n')
            # #endregion
            self.current_window.mainloop()
        elif feature == 'merge':
            self.current_window = MergeWindow(self.root)
            self.current_window.protocol("WM_DELETE_WINDOW", self._on_window_close)
            self.current_window.mainloop()
        elif feature == 'reader':
            self.current_window = ReaderWindow(self.root)
            self.current_window.protocol("WM_DELETE_WINDOW", self._on_window_close)
            self.current_window.mainloop()
    
    def _on_window_close(self):
        """機能ウィンドウが閉じられたときの処理"""
        if self.current_window:
            self.current_window.destroy()
            self.current_window = None
        # ランチャーに戻る
        self.show_launcher()


def main():
    """メイン関数"""
    app = MainApplication()
    app.root.mainloop()


if __name__ == '__main__':
    main()

