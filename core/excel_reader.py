"""
Excel Reader - 読み上げ機能
Excelファイルの内容を音声で読み上げる機能を提供するクラス
"""

import pandas as pd
import time
from pathlib import Path
from typing import Dict, Any, Optional
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
    
    def update_settings(self, speed: Optional[int] = None, volume: Optional[float] = None,
                       column_delay: Optional[float] = None, row_delay: Optional[float] = None):
        """読み上げ中に設定を更新"""
        if speed is not None:
            self.speed = speed
            # エンジンが既に初期化されている場合は、速度を更新
            if self._speech_engine is not None:
                rate = 200 + (self.speed * 12.5)
                rate = max(50, min(300, rate))
                try:
                    self._speech_engine.setProperty('rate', rate)
                except Exception:
                    pass
        
        if volume is not None:
            self.volume = volume
            # エンジンが既に初期化されている場合は、音量を更新
            if self._speech_engine is not None:
                volume_val = max(0.1, min(1.0, self.volume))
                try:
                    self._speech_engine.setProperty('volume', volume_val)
                except Exception:
                    pass
        
        if column_delay is not None:
            self.column_delay = column_delay
        
        if row_delay is not None:
            self.row_delay = row_delay
        
        # エンジンを再初期化して新しい設定を反映
        if self._speech_engine is not None and (speed is not None or volume is not None):
            try:
                # エンジンを破棄して再初期化
                del self._speech_engine
                self._speech_engine = None
            except Exception:
                self._speech_engine = None
        
    def _get_speech_engine(self):
        """音声エンジンを取得（pyttsx3を使用）"""
        if self._speech_engine is None:
            try:
                import pyttsx3
                import platform
                
                # プラットフォームに応じてドライバーを指定
                system = platform.system()
                if system == 'Windows':
                    # WindowsではSAPI5を使用
                    try:
                        self._speech_engine = pyttsx3.init('sapi5')
                    except Exception:
                        # SAPI5が利用できない場合はデフォルトを試す
                        self._speech_engine = pyttsx3.init()
                elif system == 'Darwin':  # macOS
                    # macOSではnsssを使用
                    try:
                        self._speech_engine = pyttsx3.init('nsss')
                    except Exception:
                        self._speech_engine = pyttsx3.init()
                else:
                    # Linuxなど
                    self._speech_engine = pyttsx3.init()
                
                # 読み上げ速度を設定（pyttsx3は通常50-300の範囲、デフォルト200）
                # speedが-10から10の範囲なので、50-300にマッピング
                # speed=0 -> 200, speed=-10 -> 50, speed=10 -> 300
                rate = 200 + (self.speed * 12.5)
                rate = max(50, min(300, rate))
                self._speech_engine.setProperty('rate', rate)
                
                # 音量を設定（0.0-1.0の範囲、最低0.1を確保）
                volume = max(0.1, min(1.0, self.volume))
                self._speech_engine.setProperty('volume', volume)
                
                # デバッグ: 現在の設定を確認
                print(f"[DEBUG] 音声エンジン初期化完了: rate={rate}, volume={volume}", file=sys.stderr)
                
            except ImportError:
                print("[ERROR] pyttsx3 が利用できません。pyttsx3をインストールしてください。", file=sys.stderr)
                print("[ERROR] インストール方法: pip install pyttsx3", file=sys.stderr)
                raise
            except Exception as e:
                print(f"[ERROR] 音声エンジンの初期化に失敗しました: {e}", file=sys.stderr)
                import traceback
                traceback.print_exc(file=sys.stderr)
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
            # 停止リクエストをチェック
            if self._stop_requested:
                return
            
            # 一時停止を待つ
            while self._pause_requested and not self._stop_requested:
                time.sleep(0.1)
            
            if self._stop_requested:
                return
            
            # テキストを読み上げ
            # 各読み上げの前にエンジンを再初期化して、確実に読み上げられるようにする
            print(f"[DEBUG] 読み上げ開始: {text_str[:50]}", file=sys.stderr)
            
            # 前のエンジンをクリアして新しいエンジンを作成
            # これにより、各読み上げが独立して実行される
            try:
                if self._speech_engine is not None:
                    try:
                        self._speech_engine.stop()
                    except Exception:
                        pass
                    # エンジンを破棄
                    del self._speech_engine
                    self._speech_engine = None
            except Exception:
                pass
            
            # 新しいエンジンを取得
            engine = self._get_speech_engine()
            
            engine.say(text_str)
            print(f"[DEBUG] say()を呼び出しました: {text_str[:50]}", file=sys.stderr)
            
            # runAndWait()を呼び出す
            try:
                print(f"[DEBUG] runAndWait()を呼び出します...", file=sys.stderr)
                engine.runAndWait()
                print(f"[DEBUG] runAndWait()が完了しました: {text_str[:50]}", file=sys.stderr)
            except RuntimeError as e:
                # runAndWait()が既に実行中の場合は、新しいエンジンインスタンスを作成
                print(f"[WARNING] runAndWait()エラー、エンジンを再初期化: {e}", file=sys.stderr)
                self._speech_engine = None
                engine = self._get_speech_engine()
                engine.say(text_str)
                engine.runAndWait()
                print(f"[DEBUG] 読み上げ完了（再初期化後）: {text_str[:50]}", file=sys.stderr)
            except Exception as e:
                print(f"[WARNING] runAndWait()で予期しないエラー: {e}", file=sys.stderr)
                import traceback
                traceback.print_exc(file=sys.stderr)
                # エラーが発生しても続行する（エンジンを再初期化）
                try:
                    self._speech_engine = None
                    engine = self._get_speech_engine()
                    engine.say(text_str)
                    engine.runAndWait()
                    print(f"[DEBUG] 読み上げ完了（エラー後再試行）: {text_str[:50]}", file=sys.stderr)
                except Exception as e2:
                    print(f"[ERROR] 再試行も失敗: {e2}", file=sys.stderr)
                    # それでも続行する
                    pass
            
        except Exception as e:
            print(f"[WARNING] 読み上げエラー: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
            # エラーが発生しても続行する（次のセルに進む）
    
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
            
            # Excelファイルを読み込む（1行目をヘッダーとして扱う）
            df = pd.read_excel(self.file_path, sheet_name=self.sheet_name, header=0)
            
            if df.empty:
                return {
                    'success': False,
                    'message': 'Excelファイルが空です',
                    'rows_read': 0
                }
            
            # 読み上げる列を取得（選択された列、またはすべての列）
            selected_columns = self.config.get('selected_columns', None)
            if selected_columns is None:
                # 選択されていない場合はすべての列
                column_indices = list(range(len(df.columns)))
            else:
                # 選択された列のみ
                column_indices = [idx for idx in selected_columns if 0 <= idx < len(df.columns)]
            
            if not column_indices:
                return {
                    'success': False,
                    'message': '読み上げる列が選択されていません',
                    'rows_read': 0
                }
            
            # 読み上げ開始
            self._is_reading = True
            self._stop_requested = False
            
            rows_read = 0
            total_rows = len(df)
            
            # 行ごとに読み上げ
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
                
                # 選択された列のみ読み上げ
                for col_idx in column_indices:
                    if self._stop_requested:
                        break
                    
                    # 一時停止を待つ
                    while self._pause_requested and not self._stop_requested:
                        time.sleep(0.1)
                    
                    if self._stop_requested:
                        break
                    
                    cell_value = row.iloc[col_idx]
                    # 列名を取得（1行目のヘッダーから）
                    if col_idx < len(df.columns):
                        col_name = str(df.columns[col_idx])
                        # 列名が空の場合は列番号を使用
                        if not col_name or col_name == 'nan' or col_name.strip() == '':
                            def get_column_letter(idx):
                                """列インデックスをExcel列名（A, B, C...）に変換"""
                                result = ""
                                idx += 1
                                while idx > 0:
                                    idx -= 1
                                    result = chr(65 + (idx % 26)) + result
                                    idx //= 26
                                return result
                            column_name = f"列{get_column_letter(col_idx)}"
                        else:
                            column_name = col_name
                    else:
                        def get_column_letter(idx):
                            result = ""
                            idx += 1
                            while idx > 0:
                                idx -= 1
                                result = chr(65 + (idx % 26)) + result
                                idx //= 26
                            return result
                        column_name = f"列{get_column_letter(col_idx)}"
                    
                    # 進捗コールバックを呼び出し
                    if self.progress_callback:
                        try:
                            self.progress_callback(row_idx, total_rows, column_name, cell_value)
                        except Exception:
                            pass
                    
                    # セルが空でない場合のみ読み上げ
                    if not pd.isna(cell_value):
                        cell_str = str(cell_value).strip()
                        if cell_str:
                            print(f"[DEBUG] 読み上げ予定: 行{row_idx}, 列{col_idx+1} ({column_name}): {cell_str[:50]}", file=sys.stderr)
                            try:
                                self._speak(cell_value)
                                print(f"[DEBUG] _speak()が完了: 行{row_idx}, 列{col_idx+1} ({column_name})", file=sys.stderr)
                            except Exception as e:
                                print(f"[ERROR] 読み上げエラー（続行）: 行{row_idx}, 列{col_idx+1}: {e}", file=sys.stderr)
                                import traceback
                                traceback.print_exc(file=sys.stderr)
                                # エラーが発生しても続行する
                                pass
                    
                    # 列間の待ち時間（最後の列以外）
                    if col_idx != column_indices[-1]:
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

