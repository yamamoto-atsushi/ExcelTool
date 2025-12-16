"""
Excel VLOOKUP Processor - Core business logic
Excelファイルを比較してVLOOKUP風の機能を提供するクラス
"""

import pandas as pd
import sys
import json
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime


class ExcelVLookupProcessor:
    """Excelファイルを比較してVLOOKUP風の機能を提供するクラス"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初期化
        
        Args:
            config: 設定辞書
                - source_file: ソースファイルパス
                - target_file: ターゲットファイルパス
                - output_file: 出力ファイルパス
                - source_sheet: ソースシート名（省略可）
                - target_sheet: ターゲットシート名（省略可）
                - match_columns: マッチングに使用する列のペア [{"source": "列名", "target": "列名"}, ...]
                - copy_columns: コピーする列のペア [{"source": "列名", "target": "列名"}, ...]
        """
        self.config = config
        self.source_file = config['source_file']
        self.target_file = config['target_file']
        self.output_file = config['output_file']
        self.source_sheet = config.get('source_sheet', 0)
        self.target_sheet = config.get('target_sheet', 0)
        self.match_columns = config['match_columns']
        self.copy_columns = config['copy_columns']
        
        # #region agent log
        log_path = Path(__file__).parent.parent / '.cursor' / 'debug.log'
        try:
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps({
                    'sessionId': 'debug-session',
                    'runId': 'run1',
                    'hypothesisId': 'A,B,C,D,E',
                    'location': 'excel_processor.py:__init__',
                    'message': 'Processor initialized with config',
                    'data': {
                        'match_columns': self.match_columns,
                        'copy_columns': self.copy_columns,
                        'source_file': str(self.source_file),
                        'target_file': str(self.target_file)
                    },
                    'timestamp': int(datetime.now().timestamp() * 1000)
                }) + '\n')
        except Exception:
            pass
        # #endregion
        
    def load_excel_files(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Excelファイルを読み込む
        
        Returns:
            (source_df, target_df) のタプル
            
        Raises:
            FileNotFoundError: ファイルが見つからない場合
            ValueError: ファイルの読み込みに失敗した場合
        """
        try:
            source_df = pd.read_excel(self.source_file, sheet_name=self.source_sheet)
            target_df = pd.read_excel(self.target_file, sheet_name=self.target_sheet)
            return source_df, target_df
        except FileNotFoundError as e:
            raise FileNotFoundError(f"ファイルが見つかりません: {e}")
        except Exception as e:
            raise ValueError(f"ファイル読み込みエラー: {e}")
    
    def match_rows(self, source_df: pd.DataFrame, target_df: pd.DataFrame) -> pd.DataFrame:
        """
        キーワード列でマッチングを行う
        
        Args:
            source_df: ソースデータフレーム
            target_df: ターゲットデータフレーム
            
        Returns:
            マッチング結果を含むターゲットデータフレーム
            
        Raises:
            ValueError: 有効なマッチング列が見つからない場合
        """
        # #region agent log
        log_path = Path(__file__).parent.parent / '.cursor' / 'debug.log'
        try:
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps({
                    'sessionId': 'debug-session',
                    'runId': 'run1',
                    'hypothesisId': 'A,D',
                    'location': 'excel_processor.py:match_rows:entry',
                    'message': 'match_rows called',
                    'data': {
                        'source_columns': list(source_df.columns),
                        'target_columns': list(target_df.columns),
                        'copy_columns': self.copy_columns
                    },
                    'timestamp': int(datetime.now().timestamp() * 1000)
                }) + '\n')
        except Exception:
            pass
        # #endregion
        
        result_df = target_df.copy()
        
        # マッチング用のマージキーを作成
        # 複数のキーワード列を結合してマッチング
        source_keys = []
        target_keys = []
        
        for match_col in self.match_columns:
            source_col = match_col['source']
            target_col = match_col['target']
            
            if source_col not in source_df.columns:
                continue
            if target_col not in target_df.columns:
                continue
            
            source_keys.append(source_col)
            target_keys.append(target_col)
        
        if not source_keys:
            raise ValueError("有効なマッチング列が見つかりません")
        
        # マージキーを作成（複数列を結合）
        source_df['_merge_key'] = source_df[source_keys].apply(
            lambda row: '|'.join(row.astype(str)), axis=1
        )
        result_df['_merge_key'] = result_df[target_keys].apply(
            lambda row: '|'.join(row.astype(str)), axis=1
        )
        
        # マッチング処理
        matched_count = 0
        for copy_col in self.copy_columns:
            source_col = copy_col['source']
            target_col = copy_col['target']
            
            # #region agent log
            try:
                with open(log_path, 'a', encoding='utf-8') as f:
                    f.write(json.dumps({
                        'sessionId': 'debug-session',
                        'runId': 'run1',
                        'hypothesisId': 'A,D',
                        'location': 'excel_processor.py:match_rows:before_copy',
                        'message': 'Before copying column',
                        'data': {
                            'source_col': source_col,
                            'target_col': target_col,
                            'source_col_exists': source_col in source_df.columns,
                            'target_col_exists': target_col in result_df.columns,
                            'target_df_columns': list(result_df.columns)
                        },
                        'timestamp': int(datetime.now().timestamp() * 1000)
                    }) + '\n')
            except Exception:
                pass
            # #endregion
            
            if source_col not in source_df.columns:
                continue
            
            # マージキーでマージしてデータをコピー
            merge_df = source_df[['_merge_key', source_col]].copy()
            merge_df = merge_df.rename(columns={source_col: '_copy_value'})
            
            result_df = result_df.merge(
                merge_df,
                on='_merge_key',
                how='left'
            )
            
            # #region agent log
            try:
                with open(log_path, 'a', encoding='utf-8') as f:
                    f.write(json.dumps({
                        'sessionId': 'debug-session',
                        'runId': 'run1',
                        'hypothesisId': 'A,D',
                        'location': 'excel_processor.py:match_rows:after_merge',
                        'message': 'After merge, before assignment',
                        'data': {
                            'target_col': target_col,
                            'target_col_in_result_df': target_col in result_df.columns,
                            'result_df_columns': list(result_df.columns),
                            'result_df_shape': list(result_df.shape)
                        },
                        'timestamp': int(datetime.now().timestamp() * 1000)
                    }) + '\n')
            except Exception:
                pass
            # #endregion
            
            # マッチした行のみコピー
            mask = result_df['_copy_value'].notna()
            
            # #region agent log
            try:
                with open(log_path, 'a', encoding='utf-8') as f:
                    f.write(json.dumps({
                        'sessionId': 'debug-session',
                        'runId': 'run1',
                        'hypothesisId': 'A,D',
                        'location': 'excel_processor.py:match_rows:mask_check',
                        'message': 'Mask check before assignment',
                        'data': {
                            'target_col': target_col,
                            'source_col': source_col,
                            'mask_any': mask.any(),
                            'mask_sum': mask.sum(),
                            'result_df_shape': list(result_df.shape),
                            '_copy_value_exists': '_copy_value' in result_df.columns,
                            'sample_copy_values': result_df['_copy_value'].head(5).tolist() if '_copy_value' in result_df.columns else []
                        },
                        'timestamp': int(datetime.now().timestamp() * 1000)
                    }) + '\n')
            except Exception:
                pass
            # #endregion
            
            if mask.any():
                # #region agent log
                try:
                    with open(log_path, 'a', encoding='utf-8') as f:
                        f.write(json.dumps({
                            'sessionId': 'debug-session',
                            'runId': 'run1',
                            'hypothesisId': 'A,D',
                            'location': 'excel_processor.py:match_rows:before_assign',
                            'message': 'Before assigning to target_col',
                            'data': {
                                'target_col': target_col,
                                'target_col_in_result_df': target_col in result_df.columns,
                                'result_df_columns': list(result_df.columns),
                                'mask_count': mask.sum(),
                                'sample_copy_values': result_df.loc[mask, '_copy_value'].head(3).tolist() if mask.any() else []
                            },
                            'timestamp': int(datetime.now().timestamp() * 1000)
                        }) + '\n')
                except Exception:
                    pass
                # #endregion
                
                # ターゲット列が存在しない場合はエラー
                if target_col not in result_df.columns:
                    # #region agent log
                    try:
                        with open(log_path, 'a', encoding='utf-8') as f:
                            f.write(json.dumps({
                                'sessionId': 'debug-session',
                                'runId': 'run1',
                                'hypothesisId': 'A,D',
                                'location': 'excel_processor.py:match_rows:target_col_missing',
                                'message': 'ERROR: target_col not in result_df after merge',
                                'data': {
                                    'target_col': target_col,
                                    'result_df_columns': list(result_df.columns)
                                },
                                'timestamp': int(datetime.now().timestamp() * 1000)
                            }) + '\n')
                    except Exception:
                        pass
                    # #endregion
                    continue
                
                # 代入前の値を記録
                before_values = result_df.loc[mask, target_col].head(3).tolist() if mask.any() else []
                copy_values = result_df.loc[mask, '_copy_value'].head(3).tolist() if mask.any() else []
                
                # #region agent log
                try:
                    with open(log_path, 'a', encoding='utf-8') as f:
                        f.write(json.dumps({
                            'sessionId': 'debug-session',
                            'runId': 'run1',
                            'hypothesisId': 'A,D',
                            'location': 'excel_processor.py:match_rows:before_assign_values',
                            'message': 'Values before assignment',
                            'data': {
                                'target_col': target_col,
                                'source_col': source_col,
                                'before_values_sample': before_values,
                                'copy_values_sample': copy_values,
                                'mask_count': mask.sum()
                            },
                            'timestamp': int(datetime.now().timestamp() * 1000)
                        }) + '\n')
                except Exception:
                    pass
                # #endregion
                
                result_df.loc[mask, target_col] = result_df.loc[mask, '_copy_value']
                
                # 代入後の値を記録
                after_values = result_df.loc[mask, target_col].head(3).tolist() if mask.any() else []
                
                # #region agent log
                try:
                    with open(log_path, 'a', encoding='utf-8') as f:
                        f.write(json.dumps({
                            'sessionId': 'debug-session',
                            'runId': 'run1',
                            'hypothesisId': 'A,D',
                            'location': 'excel_processor.py:match_rows:after_assign_values',
                            'message': 'Values after assignment',
                            'data': {
                                'target_col': target_col,
                                'source_col': source_col,
                                'after_values_sample': after_values,
                                'assigned_count': mask.sum()
                            },
                            'timestamp': int(datetime.now().timestamp() * 1000)
                        }) + '\n')
                except Exception:
                    pass
                # #endregion
                
                matched_count = max(matched_count, mask.sum())
            
            # 一時列を削除
            result_df = result_df.drop(columns=['_copy_value'])
        
        # マージキーを削除
        result_df = result_df.drop(columns=['_merge_key'])
        
        # #region agent log
        try:
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps({
                    'sessionId': 'debug-session',
                    'runId': 'run1',
                    'hypothesisId': 'A,D',
                    'location': 'excel_processor.py:match_rows:exit',
                    'message': 'match_rows completed',
                    'data': {
                        'final_columns': list(result_df.columns),
                        'matched_count': matched_count
                    },
                    'timestamp': int(datetime.now().timestamp() * 1000)
                }) + '\n')
        except Exception:
            pass
        # #endregion
        
        return result_df, matched_count
    
    def save_result(self, result_df: pd.DataFrame) -> None:
        """
        結果をExcelファイルに保存
        
        Args:
            result_df: 保存するデータフレーム
            
        Raises:
            IOError: 保存に失敗した場合
        """
        try:
            result_df.to_excel(self.output_file, index=False, engine='openpyxl')
        except Exception as e:
            raise IOError(f"保存エラー: {e}")
    
    def execute(self) -> Dict[str, Any]:
        """
        メイン処理を実行
        
        Returns:
            処理結果の辞書
                - success: 成功フラグ
                - message: メッセージ
                - matched_count: マッチした行数
                - source_rows: ソースファイルの行数
                - target_rows: ターゲットファイルの行数
        """
        try:
            # ファイル読み込み
            source_df, target_df = self.load_excel_files()
            source_rows = len(source_df)
            target_rows = len(target_df)
            
            # マッチング処理
            result_df, matched_count = self.match_rows(source_df, target_df)
            
            # 結果保存
            self.save_result(result_df)
            
            return {
                'success': True,
                'message': f'処理が完了しました。{matched_count}行がマッチしました。',
                'matched_count': matched_count,
                'source_rows': source_rows,
                'target_rows': target_rows,
                'output_file': self.output_file
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'エラーが発生しました: {str(e)}',
                'matched_count': 0,
                'source_rows': 0,
                'target_rows': 0,
                'output_file': None
            }

