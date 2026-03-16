#!/usr/bin/env python3
"""
Excel Search Tool (Improved) - キーワード検索機能（改善版）
指定フォルダ内のExcelファイルからキーワードを検索し、
ファイルパス、ファイル名、ファイル編集日のリストを作成するツール
NAS環境での高速かつ安定した検索を想定

改善点:
- 詳細情報の追加（シート名、セル位置、マッチ回数、ファイルサイズ、作成日）
- 進捗表示の改善（ETA、処理速度）
- ログファイル出力
- 正規表現検索対応
- AND/OR条件の追加
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
import re


class ExcelSearchToolImproved:
    """Excelファイルからキーワードを検索するクラス（改善版）"""
    
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
                - use_regex: 正規表現を使用するか（デフォルト: False）
                - match_mode: マッチモード "any" または "all"（デフォルト: "any"）
                - include_details: 詳細情報を含めるか（デフォルト: True）
                - log_file: ログファイルのパス（省略可）
        """
        self.config = config
        self.search_path = Path(config['search_path'])
        self.keywords = config['keywords']
        self.output_file = Path(config['output_file'])
        self.recursive = config.get('recursive', True)
        self.max_workers = config.get('max_workers', 4)
        self.case_sensitive = config.get('case_sensitive', False)
        self.use_regex = config.get('use_regex', False)
        self.match_mode = config.get('match_mode', 'any')  # 'any' or 'all'
        self.include_details = config.get('include_details', True)
        self.log_file = config.get('log_file')
        
        # 検索結果を保存するリスト
        self.results: List[Dict[str, Any]] = []
        
        # Excelファイルの拡張子
        self.excel_extensions = {'.xlsx', '.xlsm', '.xls'}
        
        # ログ用
        self.log_messages: List[str] = []
        
        # 統計情報
        self.stats = {
            'total_files': 0,
            'processed_files': 0,
            'matched_files': 0,
            'error_files': 0,
            'start_time': None,
            'end_time': None
        }
        
    def log(self, message: str, level: str = 'INFO'):
        """ログメッセージを記録"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] [{level}] {message}"
        self.log_messages.append(log_message)
        print(log_message)
    
    def save_log(self):
        """ログをファイルに保存"""
        if not self.log_file:
            return
        
        try:
            log_path = Path(self.log_file)
            with open(log_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(self.log_messages))
                f.write(f'\n\n=== 統計情報 ===\n')
                f.write(f'総ファイル数: {self.stats["total_files"]}\n')
                f.write(f'処理ファイル数: {self.stats["processed_files"]}\n')
                f.write(f'マッチファイル数: {self.stats["matched_files"]}\n')
                f.write(f'エラーファイル数: {self.stats["error_files"]}\n')
                if self.stats["start_time"] and self.stats["end_time"]:
                    elapsed = self.stats["end_time"] - self.stats["start_time"]
                    f.write(f'処理時間: {elapsed:.2f}秒\n')
                    if self.stats["processed_files"] > 0:
                        f.write(f'平均処理速度: {self.stats["processed_files"]/elapsed:.2f} ファイル/秒\n')
            self.log(f"ログファイルを保存しました: {log_path}")
        except Exception as e:
            print(f"[WARN] ログファイル保存エラー: {e}", file=sys.stderr)
    
    def match_keyword(self, text: str, keyword: str) -> bool:
        """
        キーワードがテキストにマッチするかチェック
        
        Args:
            text: 検索対象のテキスト
            keyword: 検索キーワード
            
        Returns:
            マッチした場合True
        """
        if not self.case_sensitive:
            text = text.lower()
            keyword = keyword.lower()
        
        if self.use_regex:
            try:
                flags = 0 if self.case_sensitive else re.IGNORECASE
                return bool(re.search(keyword, text, flags))
            except re.error:
                # 正規表現エラーの場合は通常の文字列検索にフォールバック
                return keyword in text
        else:
            return keyword in text
    
    def search_keywords_in_excel(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        1つのExcelファイル内でキーワードを検索（改善版）
        
        Args:
            file_path: Excelファイルのパス
            
        Returns:
            キーワードが見つかった場合は辞書、見つからない場合はNone
        """
        try:
            # ファイルが存在し、読み取り可能か確認
            if not file_path.exists():
                return None
            
            # ファイル情報を取得
            stat = file_path.stat()
            modified_timestamp = stat.st_mtime
            created_timestamp = stat.st_ctime
            file_size = stat.st_size
            
            modified_date = datetime.fromtimestamp(modified_timestamp).strftime('%Y-%m-%d %H:%M:%S')
            created_date = datetime.fromtimestamp(created_timestamp).strftime('%Y-%m-%d %H:%M:%S')
            file_size_mb = file_size / (1024 * 1024)
            
            # キーワードマッチ情報を記録
            keyword_matches: Dict[str, List[Dict[str, Any]]] = {kw: [] for kw in self.keywords}
            matched_keywords = set()
            
            try:
                # Excelファイルの全シートを読み込んで検索
                with pd.ExcelFile(file_path, engine='openpyxl') as excel_file:
                    for sheet_name in excel_file.sheet_names:
                        try:
                            df = pd.read_excel(excel_file, sheet_name=sheet_name, header=None)
                            
                            # 全セルを検索
                            for keyword in self.keywords:
                                if keyword in matched_keywords and self.match_mode == 'any':
                                    continue  # 既に見つかっているキーワードはスキップ（anyモードの場合）
                                
                                # データフレーム全体を文字列として検索
                                for row_idx, row in df.iterrows():
                                    for col_idx, val in enumerate(row):
                                        val_str = str(val)
                                        if val_str == 'nan' or pd.isna(val):
                                            continue
                                        
                                        if self.match_keyword(val_str, keyword):
                                            matched_keywords.add(keyword)
                                            
                                            if self.include_details:
                                                keyword_matches[keyword].append({
                                                    'sheet': sheet_name,
                                                    'row': int(row_idx) + 1,  # 1-based index
                                                    'column': col_idx + 1,  # 1-based index
                                                    'cell_value': val_str[:100]  # 最初の100文字
                                                })
                                            else:
                                                # 詳細情報が不要な場合でも、1つでも見つかれば記録
                                                keyword_matches[keyword].append({})
                                            break  # このキーワードが見つかったので次のキーワードへ
                                        
                                    if keyword in matched_keywords:
                                        break  # このキーワードが見つかったので次のキーワードへ
                                        
                        except Exception as e:
                            # シートの読み込みエラーはスキップして続行
                            self.log(f"シート '{sheet_name}' の読み込みエラー ({file_path}): {e}", 'WARN')
                            continue
                
            except Exception as e:
                # Excelファイルの読み込みエラー
                self.log(f"Excelファイル読み込みエラー ({file_path}): {e}", 'WARN')
                return None
            
            # マッチモードに応じて判定
            if self.match_mode == 'all':
                # すべてのキーワードがマッチしている必要がある
                if len(matched_keywords) != len(self.keywords):
                    return None
            # match_mode == 'any' の場合は、1つでもマッチしていればOK
            
            # キーワードが見つかった場合のみ結果を返す
            if matched_keywords:
                result = {
                    'file_path': str(file_path.resolve()),
                    'file_name': file_path.name,
                    'modified_date': modified_date,
                    'created_date': created_date,
                    'file_size_mb': round(file_size_mb, 2),
                    'matched_keywords': sorted(list(matched_keywords)),
                }
                
                if self.include_details:
                    # 詳細情報を追加
                    keyword_details = {}
                    match_counts = {}
                    matched_sheets = set()
                    
                    for kw in matched_keywords:
                        matches = keyword_matches[kw]
                        match_counts[kw] = len(matches)
                        if matches:
                            matched_sheets.add(matches[0]['sheet'])
                            keyword_details[kw] = {
                                'count': len(matches),
                                'sheets': list(set(m['sheet'] for m in matches)),
                                'first_match': matches[0] if matches else None
                            }
                    
                    result['match_details'] = keyword_details
                    result['match_counts'] = match_counts
                    result['matched_sheets'] = sorted(list(matched_sheets))
                    result['total_matches'] = sum(match_counts.values())
                
                return result
            
            return None
            
        except PermissionError:
            self.log(f"アクセス権限エラー: {file_path}", 'WARN')
            return None
        except Exception as e:
            self.log(f"予期しないエラー ({file_path}): {e}", 'ERROR')
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
                self.log(f"検索パスが存在しません: {self.search_path}", 'ERROR')
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
            self.log(f"検索パスへのアクセス権限がありません: {self.search_path}", 'ERROR')
        except Exception as e:
            self.log(f"ファイル検索エラー: {e}", 'ERROR')
            traceback.print_exc()
        
        return excel_files
    
    def search_files_parallel(self, excel_files: List[Path]):
        """
        並列処理でExcelファイルを検索（改善版）
        
        Args:
            excel_files: 検索対象のExcelファイルのリスト
        """
        self.stats['total_files'] = len(excel_files)
        self.log(f"{len(excel_files)}個のExcelファイルを検索します...")
        self.log(f"並列処理数: {self.max_workers}")
        self.log(f"マッチモード: {self.match_mode}")
        self.log(f"正規表現: {'有効' if self.use_regex else '無効'}")
        
        processed = 0
        found_count = 0
        error_count = 0
        start_time = time.time()
        
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
                        self.log(f"キーワード発見: {file_path.name}")
                    
                    # 進捗表示の改善
                    elapsed = time.time() - start_time
                    if processed > 0:
                        avg_time_per_file = elapsed / processed
                        remaining_files = self.stats['total_files'] - processed
                        eta = avg_time_per_file * remaining_files
                        speed = processed / elapsed if elapsed > 0 else 0
                        
                        if processed % 50 == 0 or processed == self.stats['total_files']:
                            self.log(
                                f"進捗: {processed}/{self.stats['total_files']} "
                                f"({found_count}件のキーワード発見, "
                                f"エラー: {error_count}, "
                                f"速度: {speed:.1f} ファイル/秒, "
                                f"残り時間: {eta:.1f}秒)"
                            )
                
                except Exception as e:
                    error_count += 1
                    self.log(f"検索エラー ({file_path}): {e}", 'ERROR')
        
        self.stats['processed_files'] = processed
        self.stats['matched_files'] = found_count
        self.stats['error_files'] = error_count
    
    def save_results(self):
        """検索結果をファイルに保存（改善版）"""
        if not self.results:
            self.log("検索結果がありません", 'WARN')
            return
        
        try:
            # 結果をDataFrameに変換
            df_data = []
            for result in self.results:
                row = {
                    'ファイルパス': result['file_path'],
                    'ファイル名': result['file_name'],
                    '編集日時': result['modified_date'],
                    '作成日時': result.get('created_date', ''),
                    'ファイルサイズ(MB)': result.get('file_size_mb', 0),
                    'マッチしたキーワード': ', '.join(result['matched_keywords']),
                }
                
                if self.include_details:
                    row['マッチしたシート'] = ', '.join(result.get('matched_sheets', []))
                    row['総マッチ数'] = result.get('total_matches', 0)
                    
                    # 各キーワードのマッチ数を追加
                    match_counts = result.get('match_counts', {})
                    for kw in result['matched_keywords']:
                        row[f'{kw}のマッチ数'] = match_counts.get(kw, 0)
                
                df_data.append(row)
            
            df = pd.DataFrame(df_data)
            
            # 編集日時でソート（新しい順）
            if '編集日時' in df.columns:
                df['編集日時_datetime'] = pd.to_datetime(df['編集日時'])
                df = df.sort_values('編集日時_datetime', ascending=False)
                df = df.drop(columns=['編集日時_datetime'])
            
            # ファイル拡張子に応じて保存形式を決定
            if self.output_file.suffix.lower() == '.csv':
                df.to_csv(self.output_file, index=False, encoding='utf-8-sig')
            else:
                # Excel形式で保存（拡張子がない場合もExcelとする）
                df.to_excel(self.output_file, index=False, engine='openpyxl')
            
            self.log(f"検索結果を保存しました: {self.output_file}")
            self.log(f"合計 {len(self.results)} 件のファイルでキーワードが見つかりました")
        
        except Exception as e:
            self.log(f"結果保存エラー: {e}", 'ERROR')
            traceback.print_exc()
            sys.exit(1)
    
    def execute(self):
        """メイン処理を実行（改善版）"""
        self.stats['start_time'] = time.time()
        
        self.log("=" * 60)
        self.log("Excel Search Tool (Improved) - キーワード検索処理開始")
        self.log("=" * 60)
        self.log(f"検索パス: {self.search_path}")
        self.log(f"検索キーワード: {', '.join(self.keywords)}")
        self.log(f"再帰的検索: {'有効' if self.recursive else '無効'}")
        self.log(f"大文字小文字の区別: {'有効' if self.case_sensitive else '無効'}")
        self.log(f"詳細情報: {'含む' if self.include_details else '含まない'}")
        self.log("=" * 60)
        
        # Excelファイルを検索
        excel_files = self.find_excel_files()
        
        if not excel_files:
            self.log("検索対象のExcelファイルが見つかりませんでした", 'WARN')
            return
        
        # 並列処理で検索
        self.search_files_parallel(excel_files)
        
        # 結果を保存
        self.save_results()
        
        self.stats['end_time'] = time.time()
        elapsed_time = self.stats['end_time'] - self.stats['start_time']
        
        self.log("=" * 60)
        self.log(f"処理完了 (所要時間: {elapsed_time:.2f}秒)")
        self.log(f"統計: 処理={self.stats['processed_files']}, "
                 f"マッチ={self.stats['matched_files']}, "
                 f"エラー={self.stats['error_files']}")
        self.log("=" * 60)
        
        # ログファイルを保存
        self.save_log()


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


def create_sample_config(output_file: str = "config_search_improved_sample.json"):
    """サンプル設定ファイルを作成（改善版）"""
    sample_config = {
        "search_path": "\\\\nas-server\\share\\excel_files",
        "keywords": [
            "プロジェクトA",
            "2024年度"
        ],
        "output_file": "search_results_improved.xlsx",
        "recursive": True,
        "max_workers": 4,
        "case_sensitive": False,
        "use_regex": False,
        "match_mode": "any",
        "include_details": True,
        "log_file": "search_log.txt"
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(sample_config, f, ensure_ascii=False, indent=2)
    
    print(f"[OK] サンプル設定ファイルを作成しました: {output_file}")


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description='Excel Search Tool (Improved) - 指定フォルダ内のExcelファイルからキーワードを検索（改善版）'
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
        print("  python excel_search_improved.py config_search_improved.json")
        print("  python excel_search_improved.py --create-sample")
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
    tool = ExcelSearchToolImproved(config)
    tool.execute()


if __name__ == '__main__':
    main()


