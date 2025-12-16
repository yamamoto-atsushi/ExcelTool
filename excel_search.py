#!/usr/bin/env python3
"""
Excel Search Tool - キーワード検索機能
指定フォルダ内のExcelファイルからキーワードを検索し、
ファイルパス、ファイル名、ファイル編集日のリストを作成するツール
NAS環境での高速かつ安定した検索を想定
"""

import pandas as pd
import json
import argparse
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import traceback


class ExcelSearchTool:
    """Excelファイルからキーワードを検索するクラス"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初期化
        
        Args:
            config: 設定辞書
                - search_path: 検索対象フォルダパス
                - keywords: 検索キーワードのリスト（1つ以上）
                - output_file: 出力ファイルパス（CSVまたはExcel）
                - recursive: 下層フォルダも検索するか（デフォルト: True）
                - max_workers: 並列処理のワーカー数（デフォルト: 4）
                - case_sensitive: 大文字小文字を区別するか（デフォルト: False）
        """
        self.config = config
        self.search_path = Path(config['search_path'])
        self.keywords = config['keywords']
        self.output_file = Path(config['output_file'])
        self.recursive = config.get('recursive', True)
        self.max_workers = config.get('max_workers', 4)
        self.case_sensitive = config.get('case_sensitive', False)
        
        # 検索結果を保存するリスト
        self.results: List[Dict[str, Any]] = []
        
        # Excelファイルの拡張子
        self.excel_extensions = {'.xlsx', '.xlsm', '.xls'}
        
    def search_keywords_in_excel(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        1つのExcelファイル内でキーワードを検索
        
        Args:
            file_path: Excelファイルのパス
            
        Returns:
            キーワードが見つかった場合は辞書、見つからない場合はNone
            辞書には以下が含まれる:
                - file_path: ファイルパス（文字列）
                - file_name: ファイル名
                - modified_date: 編集日時（文字列）
                - matched_keywords: マッチしたキーワードのリスト
        """
        try:
            # ファイルが存在し、読み取り可能か確認
            if not file_path.exists():
                return None
            
            # ファイル編集日を取得
            modified_timestamp = file_path.stat().st_mtime
            modified_date = datetime.fromtimestamp(modified_timestamp).strftime('%Y-%m-%d %H:%M:%S')
            
            # Excelファイルを読み込んで検索（AND条件：すべてのキーワードが見つかった場合のみマッチ）
            matched_keywords = set()
            
            try:
                # Excelファイルの全シートを読み込んで検索
                excel_file = pd.ExcelFile(file_path, engine='openpyxl')
                
                # 全シートのデータを一度に文字列として取得（メモリ効率を考慮）
                all_text = ""
                
                for sheet_name in excel_file.sheet_names:
                    try:
                        df = pd.read_excel(excel_file, sheet_name=sheet_name, header=None)
                        
                        # データフレーム全体を文字列に変換して結合
                        df_str = df.astype(str)
                        for col in df_str.columns:
                            for val in df_str[col]:
                                val_str = str(val)
                                if val_str != 'nan':
                                    if not self.case_sensitive:
                                        val_str = val_str.lower()
                                    all_text += val_str + " "
                                    
                    except Exception as e:
                        # シートの読み込みエラーはスキップして続行
                        print(f"[WARN] シート '{sheet_name}' の読み込みエラー ({file_path}): {e}", file=sys.stderr)
                        continue
                
                excel_file.close()
                
                # AND条件：すべてのキーワードが含まれているかチェック
                all_found = True
                for keyword in self.keywords:
                    search_keyword = keyword if self.case_sensitive else keyword.lower()
                    if search_keyword not in all_text:
                        all_found = False
                        break
                    matched_keywords.add(keyword)
                
            except Exception as e:
                # Excelファイルの読み込みエラー
                print(f"[WARN] Excelファイル読み込みエラー ({file_path}): {e}", file=sys.stderr)
                return None
            
            # AND条件：すべてのキーワードが見つかった場合のみ結果を返す
            if all_found and matched_keywords:
                return {
                    'file_path': str(file_path.resolve()),
                    'file_name': file_path.name,
                    'modified_date': modified_date,
                    'matched_keywords': sorted(list(matched_keywords))
                }
            
            return None
            
        except PermissionError:
            print(f"[WARN] アクセス権限エラー: {file_path}", file=sys.stderr)
            return None
        except Exception as e:
            print(f"[WARN] 予期しないエラー ({file_path}): {e}", file=sys.stderr)
            traceback.print_exc()
            return None
    
    def find_excel_files(self) -> List[Path]:
        """
        検索パス内のExcelファイルをすべて見つける
        
        Returns:
            Excelファイルのパスのリスト
        """
        excel_files = []
        
        try:
            if not self.search_path.exists():
                print(f"[ERROR] 検索パスが存在しません: {self.search_path}", file=sys.stderr)
                return excel_files
            
            if self.recursive:
                # 再帰的に検索
                for file_path in self.search_path.rglob('*'):
                    if file_path.is_file() and file_path.suffix.lower() in self.excel_extensions:
                        excel_files.append(file_path)
            else:
                # 指定パスのみ検索
                for file_path in self.search_path.iterdir():
                    if file_path.is_file() and file_path.suffix.lower() in self.excel_extensions:
                        excel_files.append(file_path)
        
        except PermissionError:
            print(f"[ERROR] 検索パスへのアクセス権限がありません: {self.search_path}", file=sys.stderr)
        except Exception as e:
            print(f"[ERROR] ファイル検索エラー: {e}", file=sys.stderr)
            traceback.print_exc()
        
        return excel_files
    
    def search_files_parallel(self, excel_files: List[Path]):
        """
        並列処理でExcelファイルを検索
        
        Args:
            excel_files: 検索対象のExcelファイルのリスト
        """
        total_files = len(excel_files)
        print(f"[INFO] {total_files}個のExcelファイルを検索します...")
        print(f"[INFO] 並列処理数: {self.max_workers}")
        
        processed = 0
        found_count = 0
        
        # 並列処理で検索
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # すべてのファイルに対する検索タスクを開始
            future_to_file = {
                executor.submit(self.search_keywords_in_excel, file_path): file_path
                for file_path in excel_files
            }
            
            # 完了したタスクから結果を取得
            for future in as_completed(future_to_file):
                processed += 1
                file_path = future_to_file[future]
                
                try:
                    result = future.result()
                    if result:
                        self.results.append(result)
                        found_count += 1
                        print(f"[OK] キーワード発見: {file_path.name}")
                
                except Exception as e:
                    print(f"[ERROR] 検索エラー ({file_path}): {e}", file=sys.stderr)
                
                # 進捗表示（100ファイルごと、または最後）
                if processed % 100 == 0 or processed == total_files:
                    print(f"[INFO] 進捗: {processed}/{total_files} ファイル処理完了 ({found_count}件のキーワード発見)")
    
    def save_results(self):
        """検索結果をファイルに保存（大量データでも安全に保存）"""
        if not self.results:
            print("[WARN] 検索結果がありません")
            return
        
        try:
            total_results = len(self.results)
            print(f"[INFO] {total_results} 件の検索結果を保存します...")
            
            # ファイル拡張子に応じて保存形式を決定
            if self.output_file.suffix.lower() == '.csv':
                # CSV形式で保存（チャンクごとに書き込み）
                self._save_csv_chunked()
            else:
                # Excel形式で保存（大量データの場合はチャンクごとに保存）
                self._save_excel_chunked()
            
            print(f"[OK] 検索結果を保存しました: {self.output_file}")
            print(f"[INFO] 合計 {total_results} 件のファイルでキーワードが見つかりました")
        
        except Exception as e:
            print(f"[ERROR] 結果保存エラー: {e}", file=sys.stderr)
            traceback.print_exc()
            sys.exit(1)
    
    def _save_csv_chunked(self):
        """CSV形式でチャンクごとに保存（大量データでも安全）"""
        chunk_size = 10000  # 1チャンクあたりの行数
        
        with open(self.output_file, 'w', encoding='utf-8-sig', newline='') as f:
            import csv
            writer = csv.writer(f)
            
            # ヘッダーを書き込み
            writer.writerow(['ファイルパス', 'ファイル名', '編集日時'])
            
            # チャンクごとに書き込み
            for i in range(0, len(self.results), chunk_size):
                chunk = self.results[i:i + chunk_size]
                for result in chunk:
                    writer.writerow([
                        result['file_path'],
                        result['file_name'],
                        result['modified_date']
                    ])
                
                if i + chunk_size < len(self.results):
                    print(f"[INFO] 進捗: {min(i + chunk_size, len(self.results))}/{len(self.results)} 件保存完了")
    
    def _save_excel_chunked(self):
        """Excel形式でチャンクごとに保存（大量データでも安全）"""
        chunk_size = 50000  # 1チャンクあたりの行数（メモリ効率を考慮）
        
        # 大量データの場合はチャンクごとに処理
        if len(self.results) > chunk_size:
            # チャンクごとにDataFrameを作成して結合
            dfs = []
            for i in range(0, len(self.results), chunk_size):
                chunk = self.results[i:i + chunk_size]
                df_data = []
                for result in chunk:
                    df_data.append({
                        'ファイルパス': result['file_path'],
                        'ファイル名': result['file_name'],
                        '編集日時': result['modified_date']
                    })
                
                df_chunk = pd.DataFrame(df_data)
                dfs.append(df_chunk)
                
                print(f"[INFO] 進捗: {min(i + chunk_size, len(self.results))}/{len(self.results)} 件処理完了")
            
            # すべてのチャンクを結合
            df = pd.concat(dfs, ignore_index=True)
        else:
            # 少量データの場合は一度に処理
            df_data = []
            for result in self.results:
                df_data.append({
                    'ファイルパス': result['file_path'],
                    'ファイル名': result['file_name'],
                    '編集日時': result['modified_date']
                })
            df = pd.DataFrame(df_data)
        
        # Excel形式で保存（openpyxlエンジンを使用）
        try:
            df.to_excel(self.output_file, index=False, engine='openpyxl')
        except Exception:
            # Excel保存に失敗した場合はCSV形式で保存を試みる
            csv_file = self.output_file.with_suffix('.csv')
            print(f"[WARN] Excel保存に失敗しました。CSV形式で保存します: {csv_file}", file=sys.stderr)
            df.to_csv(csv_file, index=False, encoding='utf-8-sig')
            raise
    
    def execute(self):
        """メイン処理を実行"""
        print("=" * 60)
        print("Excel Search Tool - キーワード検索処理開始")
        print("=" * 60)
        print(f"検索パス: {self.search_path}")
        print(f"検索キーワード: {', '.join(self.keywords)}")
        print(f"再帰的検索: {'有効' if self.recursive else '無効'}")
        print(f"大文字小文字の区別: {'有効' if self.case_sensitive else '無効'}")
        print("=" * 60)
        
        start_time = time.time()
        
        # Excelファイルを検索
        excel_files = self.find_excel_files()
        
        if not excel_files:
            print("[WARN] 検索対象のExcelファイルが見つかりませんでした")
            return
        
        # 並列処理で検索
        self.search_files_parallel(excel_files)
        
        # 結果を保存
        self.save_results()
        
        elapsed_time = time.time() - start_time
        print("=" * 60)
        print(f"処理完了 (所要時間: {elapsed_time:.2f}秒)")
        print("=" * 60)


def load_config(config_file: str) -> Dict[str, Any]:
    """設定ファイルを読み込む"""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print(f"[ERROR] 設定ファイル '{config_file}' が見つかりません", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"[ERROR] 設定ファイルのJSON形式が不正です: {e}", file=sys.stderr)
        sys.exit(1)


def create_sample_config(output_file: str = "config_search_sample.json"):
    """サンプル設定ファイルを作成"""
    sample_config = {
        "search_path": "\\\\nas-server\\share\\excel_files",
        "keywords": [
            "キーワード1",
            "キーワード2"
        ],
        "output_file": "search_results.xlsx",
        "recursive": True,
        "max_workers": 4,
        "case_sensitive": False
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(sample_config, f, ensure_ascii=False, indent=2)
    
    print(f"[OK] サンプル設定ファイルを作成しました: {output_file}")


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description='Excel Search Tool - 指定フォルダ内のExcelファイルからキーワードを検索'
    )
    parser.add_argument(
        'config',
        nargs='?',
        help='設定ファイルのパス (JSON形式)'
    )
    parser.add_argument(
        '--create-sample',
        action='store_true',
        help='サンプル設定ファイルを作成'
    )
    
    args = parser.parse_args()
    
    if args.create_sample:
        create_sample_config()
        return
    
    if not args.config:
        parser.print_help()
        print("\n使用例:")
        print("  python excel_search.py config_search.json")
        print("  python excel_search.py --create-sample")
        sys.exit(1)
    
    # 設定読み込み
    config = load_config(args.config)
    
    # 必須パラメータのチェック
    required_keys = ['search_path', 'keywords', 'output_file']
    for key in required_keys:
        if key not in config:
            print(f"[ERROR] 設定ファイルに必須項目 '{key}' がありません", file=sys.stderr)
            sys.exit(1)
    
    # キーワードが空でないことを確認
    if not config['keywords'] or not isinstance(config['keywords'], list):
        print(f"[ERROR] 'keywords' は空でないリストである必要があります", file=sys.stderr)
        sys.exit(1)
    
    # ツール実行
    tool = ExcelSearchTool(config)
    tool.execute()


if __name__ == '__main__':
    main()


