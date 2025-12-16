#!/usr/bin/env python3
"""
Excel Reader Simulation - 読み上げ機能のシミュレーション
テスト用のExcelファイルを作成して読み上げ機能をテストします
"""

import pandas as pd
from pathlib import Path
import sys

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core import ExcelReader


def create_test_excel(file_path: str = "test_read_data.xlsx"):
    """テスト用のExcelファイルを作成"""
    # サンプルデータを作成
    data = {
        'A列': ['商品A', '商品B', '商品C', '商品D', ''],  # 最後はブランクで終了
        'B列': ['1000', '2000', '3000', '4000', ''],
        'C列': ['在庫あり', '在庫なし', '在庫あり', '在庫あり', ''],
        'D列': ['東京', '大阪', '名古屋', '福岡', '']
    }
    
    df = pd.DataFrame(data)
    df.to_excel(file_path, index=False)
    print(f"[OK] テスト用Excelファイルを作成しました: {file_path}")
    print("\nデータ内容:")
    print(df.to_string())
    print()
    return file_path


def simulate_reading(file_path: str, speed: int = 0, column_delay: float = 0.5):
    """読み上げ機能のシミュレーションを実行"""
    print("=" * 60)
    print("Excel Reader Simulation - 読み上げシミュレーション")
    print("=" * 60)
    print(f"ファイル: {file_path}")
    print(f"読み上げ速度: {speed}")
    print(f"列間の待ち時間: {column_delay}秒")
    print("=" * 60)
    print()
    
    # 進捗コールバック関数（デバッグ用）
    cells_read = []
    
    def progress_callback(row_idx, total_rows, column_name, cell_value):
        """進捗コールバック（デバッグ用）"""
        cell_info = {
            'row': row_idx,
            'column': column_name,
            'value': str(cell_value)[:50] if not pd.isna(cell_value) else '(空)'
        }
        cells_read.append(cell_info)
        print(f"[進捗] 行{row_idx}/{total_rows}, 列: {column_name}, 値: {cell_info['value']}")
    
    # 設定を作成
    config = {
        'file_path': file_path,
        'sheet_name': 0,
        'speed': speed,
        'column_delay': column_delay,
        'progress_callback': progress_callback
    }
    
    # 読み上げツールを作成
    reader = ExcelReader(config)
    
    print("読み上げを開始します...")
    print("（実際の音声読み上げが開始されます）")
    print()
    
    try:
        # 読み上げを実行
        result = reader.read_excel()
        
        print()
        print("=" * 60)
        if result['success']:
            print(f"[OK] {result['message']}")
        else:
            print(f"[ERROR] {result['message']}")
        print("=" * 60)
        
        print()
        print("=" * 60)
        print("読み上げたセルの詳細:")
        print("=" * 60)
        for i, cell in enumerate(cells_read, 1):
            print(f"{i}. 行{cell['row']}, 列{cell['column']}: {cell['value']}")
        print(f"\n合計: {len(cells_read)}セル")
        print("=" * 60)
        
        return result
        
    except KeyboardInterrupt:
        print()
        print("\n[INFO] 読み上げを停止しました")
        reader.stop()
        return None
    except Exception as e:
        print(f"\n[ERROR] 予期しないエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """メイン関数"""
    # テスト用Excelファイルを作成
    test_file = create_test_excel()
    
    if not Path(test_file).exists():
        print(f"[ERROR] テストファイルの作成に失敗しました: {test_file}", file=sys.stderr)
        sys.exit(1)
    
    print()
    print("読み上げシミュレーションを開始します...")
    print()
    
    # シミュレーションを実行
    result = simulate_reading(test_file, speed=0, column_delay=0.5)
    
    if result and result['success']:
        print(f"\n[OK] シミュレーションが正常に完了しました")
        print(f"読み上げた行数: {result['rows_read']}")
    else:
        print("\n[ERROR] シミュレーションが失敗しました", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()

