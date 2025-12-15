"""
Excel Merger - Excelファイル統合機能
分割されたExcelファイルを統合して1つのファイルにする機能
"""

import pandas as pd
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import traceback


class ExcelMerger:
    """Excelファイルを統合するクラス"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初期化
        
        Args:
            config: 設定辞書
                - input_path: 入力パス（ファイルまたはフォルダ）
                - input_files: 入力ファイルリスト（複数ファイル指定時、input_pathより優先）
                - output_file: 出力ファイルパス
                - sheet_name: シート名（省略可、デフォルト: 0）
                - recursive: サブフォルダも検索するか（デフォルト: False）
                - include_header: ヘッダーを含めるか（デフォルト: True、最初のファイルのみ）
        """
        self.config = config
        self.input_files = config.get('input_files', None)
        if self.input_files:
            # ファイルリストが指定されている場合
            self.input_path = None
        else:
            self.input_path = Path(config['input_path'])
        self.output_file = Path(config['output_file'])
        self.sheet_name = config.get('sheet_name', 0)
        self.recursive = config.get('recursive', False)
        self.include_header = config.get('include_header', True)
    
    def _get_excel_files(self) -> List[Path]:
        """
        Excelファイルのリストを取得
        
        Returns:
            Excelファイルのパスリスト
        """
        excel_files = []
        
        # ファイルリストが指定されている場合
        if self.input_files:
            for file_path_str in self.input_files:
                file_path = Path(file_path_str)
                if file_path.exists() and file_path.is_file() and self._is_excel_file(file_path):
                    excel_files.append(file_path)
        elif self.input_path:
            if self.input_path.is_file():
                # ファイルが指定されている場合
                if self._is_excel_file(self.input_path):
                    excel_files.append(self.input_path)
            elif self.input_path.is_dir():
                # フォルダが指定されている場合
                pattern = "**/*" if self.recursive else "*"
                for file_path in self.input_path.glob(pattern):
                    if file_path.is_file() and self._is_excel_file(file_path):
                        excel_files.append(file_path)
            else:
                raise ValueError(f"入力パスが存在しません: {self.input_path}")
        
        # ファイル名でソート
        excel_files.sort(key=lambda p: str(p))
        
        return excel_files
    
    def _is_excel_file(self, file_path: Path) -> bool:
        """Excelファイルかどうかを判定"""
        excel_extensions = ['.xlsx', '.xlsm', '.xls']
        return file_path.suffix.lower() in excel_extensions
    
    def _read_excel_file(self, file_path: Path) -> Optional[pd.DataFrame]:
        """
        Excelファイルを読み込む
        
        Args:
            file_path: Excelファイルのパス
            
        Returns:
            データフレーム（読み込み失敗時はNone）
        """
        try:
            df = pd.read_excel(file_path, sheet_name=self.sheet_name)
            return df
        except Exception as e:
            print(f"[WARNING] ファイル読み込みエラー ({file_path}): {e}", file=sys.stderr)
            return None
    
    def merge(self) -> Dict[str, Any]:
        """
        Excelファイルを統合
        
        Returns:
            結果辞書
                - success: 成功フラグ
                - message: メッセージ
                - files_processed: 処理したファイル数
                - total_rows: 統合後の総行数
                - output_file: 出力ファイルパス
        """
        try:
            # Excelファイルのリストを取得
            excel_files = self._get_excel_files()
            
            if not excel_files:
                return {
                    'success': False,
                    'message': '統合するExcelファイルが見つかりませんでした',
                    'files_processed': 0,
                    'total_rows': 0,
                    'output_file': None
                }
            
            # データフレームのリスト
            dataframes = []
            files_processed = 0
            total_rows = 0
            
            # 各Excelファイルを読み込む
            for i, file_path in enumerate(excel_files):
                df = self._read_excel_file(file_path)
                if df is not None:
                    # ヘッダーを含めるかどうか
                    if i == 0 or self.include_header:
                        # 最初のファイルまたは常にヘッダーを含める
                        dataframes.append(df)
                        files_processed += 1
                        total_rows += len(df)
                    else:
                        # ヘッダーをスキップ（最初の行を除外）
                        if len(df) > 0:
                            dataframes.append(df.iloc[1:])
                            files_processed += 1
                            total_rows += len(df) - 1
            
            if not dataframes:
                return {
                    'success': False,
                    'message': '読み込めるExcelファイルがありませんでした',
                    'files_processed': 0,
                    'total_rows': 0,
                    'output_file': None
                }
            
            # データフレームを結合
            merged_df = pd.concat(dataframes, ignore_index=True)
            
            # 出力ファイルのディレクトリを作成
            self.output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Excelファイルとして保存
            merged_df.to_excel(self.output_file, index=False, engine='openpyxl')
            
            return {
                'success': True,
                'message': f'{files_processed}個のファイルを統合しました',
                'files_processed': files_processed,
                'total_rows': total_rows,
                'output_file': str(self.output_file)
            }
            
        except Exception as e:
            error_message = f"統合処理中にエラーが発生しました: {str(e)}"
            print(f"[ERROR] {error_message}", file=sys.stderr)
            traceback.print_exc()
            return {
                'success': False,
                'message': error_message,
                'files_processed': 0,
                'total_rows': 0,
                'output_file': None
            }

