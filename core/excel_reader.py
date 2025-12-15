"""
Excel Reader - 読み上げ機能
Excelファイルの内容を音声で読み上げる機能を提供するクラス
"""

import pandas as pd
import time
from pathlib import Path
from typing import Optional, Dict, Any, Callable
import sys


class ExcelReader:
    """Excelファイルの内容を音声で読み上げるクラス"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初期化
        
        Args:
            config: 設定辞書
                - file_path: Excelファイルパス
                - sheet_name: シート名（省略可、デフォルト: 0）
                - speed: 読み上げ速度（-10から10、デフォルト: 0）
                - column_delay: 列間の待ち時間（秒、デフォルト: 0.5）
                - row_delay: 行間の待ち時間（秒、デフォルト: 0.0）
                - volume: 音量（0.0-1.0、デフォルト: 1.0）
                - progress_callback: 進捗コールバック関数（行番号、列名、セル内容を受け取る）
        """
        self.config = config
        self.file_path = config['file_path']
        self.sheet_name = config.get('sheet_name', 0)
        self.speed = config.get('speed', 0)
        self.column_delay = config.get('column_delay', 0.5)
        self.row_delay = config.get('row_delay', 0.0)
        self.volume = config.get('volume', 1.0)
        self.progress_callback = config.get('progress_callback', None)
        self._speech_engine = None
        self._is_reading = False
        self._stop_requested = False
        self._pause_requested = False
        
    def _get_speech_engine(self):
        """音声エンジンを取得（pyttsx3を使用）"""
        if self._speech_engine is None:
            try:
                import pyttsx3
                self._speech_engine = pyttsx3.init()
                # 読み上げ速度を設定（pyttsx3は通常50-300の範囲、デフォルト200）
                # speedが-10から10の範囲なので、50-300にマッピング
                # speed=0 -> 200, speed=-10 -> 50, speed=10 -> 300
                rate = 200 + (self.speed * 12.5)
                rate = max(50, min(300, rate))
                self._speech_engine.setProperty('rate', rate)
                # 音量を設定（0.0-1.0の範囲）
                volume = max(0.0, min(1.0, self.volume))
                self._speech_engine.setProperty('volume', volume)
            except ImportError:
                print("[ERROR] pyttsx3 が利用できません。pyttsx3をインストールしてください。", file=sys.stderr)
                raise
            except Exception as e:
                print(f"[ERROR] 音声エンジンの初期化に失敗しました: {e}", file=sys.stderr)
                raise
        return self._speech_engine
    
    def _speak(self, text: str):
        """テキストを読み上げる"""
        if not text or pd.isna(text):
            return
        
        text_str = str(text).strip()
        if not text_str:
            return
        
        try:
            engine = self._get_speech_engine()
            engine.say(text_str)
            engine.runAndWait()
        except Exception as e:
            print(f"[WARNING] 読み上げエラー: {e}", file=sys.stderr)
    
    def read_excel(self) -> Dict[str, Any]:
        """
        Excelファイルを読み上げる
        
        Returns:
            結果辞書
                - success: 成功フラグ
                - message: メッセージ
                - rows_read: 読み上げた行数
        """
        try:
            # ファイルの存在確認
            if not Path(self.file_path).exists():
                return {
                    'success': False,
                    'message': f'ファイルが見つかりません: {self.file_path}',
                    'rows_read': 0
                }
            
            # Excelファイルを読み込む
            df = pd.read_excel(self.file_path, sheet_name=self.sheet_name)
            
            if df.empty:
                return {
                    'success': False,
                    'message': 'Excelファイルが空です',
                    'rows_read': 0
                }
            
            # 最終列を取得
            last_column = df.columns[-1]
            last_column_index = df.columns.get_loc(last_column)
            
            # 読み上げ開始
            self._is_reading = True
            self._stop_requested = False
            
            rows_read = 0
            total_rows = len(df)
            
            # A列から最終列まで、行ごとに読み上げ
            for row_idx, (index, row) in enumerate(df.iterrows(), start=1):
                # A列がブランクかチェック
                first_col_value = row.iloc[0]
                if pd.isna(first_col_value) or str(first_col_value).strip() == '':
                    # A列がブランクなので終了
                    break
                
                # 停止リクエストをチェック
                if self._stop_requested:
                    break
                
                # 一時停止を待つ
                while self._pause_requested and not self._stop_requested:
                    time.sleep(0.1)
                
                if self._stop_requested:
                    break
                
                # A列から最終列まで読み上げ
                for col_idx in range(last_column_index + 1):
                    if self._stop_requested:
                        break
                    
                    # 一時停止を待つ
                    while self._pause_requested and not self._stop_requested:
                        time.sleep(0.1)
                    
                    if self._stop_requested:
                        break
                    
                    cell_value = row.iloc[col_idx]
                    column_name = df.columns[col_idx] if col_idx < len(df.columns) else f"列{col_idx + 1}"
                    
                    # 進捗コールバックを呼び出し
                    if self.progress_callback:
                        try:
                            self.progress_callback(row_idx, total_rows, column_name, cell_value)
                        except Exception:
                            pass
                    
                    if not pd.isna(cell_value):
                        self._speak(cell_value)
                    
                    # 列間の待ち時間（最後の列以外）
                    if col_idx < last_column_index:
                        time.sleep(self.column_delay)
                
                rows_read += 1
                
                # 行間の待ち時間（最後の行以外）
                if row_idx < total_rows:
                    time.sleep(self.row_delay)
            
            self._is_reading = False
            
            return {
                'success': True,
                'message': f'読み上げが完了しました（{rows_read}行）',
                'rows_read': rows_read
            }
            
        except FileNotFoundError:
            return {
                'success': False,
                'message': f'ファイルが見つかりません: {self.file_path}',
                'rows_read': 0
            }
        except Exception as e:
            self._is_reading = False
            return {
                'success': False,
                'message': f'エラーが発生しました: {str(e)}',
                'rows_read': rows_read if 'rows_read' in locals() else 0
            }
    
    def stop(self):
        """読み上げを停止"""
        self._stop_requested = True
        self._pause_requested = False
        try:
            if self._speech_engine:
                self._speech_engine.stop()
        except Exception:
            pass
    
    def pause(self):
        """読み上げを一時停止"""
        self._pause_requested = True
    
    def resume(self):
        """読み上げを再開"""
        self._pause_requested = False
    
    def is_reading(self) -> bool:
        """読み上げ中かどうかを返す"""
        return self._is_reading
    
    def is_paused(self) -> bool:
        """一時停止中かどうかを返す"""
        return self._pause_requested

