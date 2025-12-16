#!/usr/bin/env python3
"""
Excel Reader Tool - 読み上げ機能（Command Line Interface）
Excelファイルの内容を音声で読み上げるツール（コマンドライン版）
"""

import sys
import argparse
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core import ExcelReader  # noqa: E402


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description='Excel Reader Tool - Excelファイルの内容を音声で読み上げる'
    )
    parser.add_argument(
        'file',
        help='読み上げるExcelファイルのパス'
    )
    parser.add_argument(
        '--sheet',
        type=str,
        default=0,
        help='シート名またはインデックス（デフォルト: 0）'
    )
    parser.add_argument(
        '--speed',
        type=int,
        default=0,
        help='読み上げ速度（-10から10、デフォルト: 0）'
    )
    parser.add_argument(
        '--column-delay',
        type=float,
        default=0.5,
        help='列間の待ち時間（秒、デフォルト: 0.5）'
    )
    
    args = parser.parse_args()
    
    # 設定を作成
    config = {
        'file_path': args.file,
        'sheet_name': args.sheet,
        'speed': args.speed,
        'column_delay': args.column_delay
    }
    
    # バリデーション
    if not Path(args.file).exists():
        print(f"[ERROR] ファイルが見つかりません: {args.file}", file=sys.stderr)
        sys.exit(1)
    
    if args.speed < -10 or args.speed > 10:
        print("[ERROR] 読み上げ速度は-10から10の範囲で指定してください", file=sys.stderr)
        sys.exit(1)
    
    if args.column_delay < 0:
        print("[ERROR] 列間の待ち時間は0以上を指定してください", file=sys.stderr)
        sys.exit(1)
    
    # 読み上げツールを作成して実行
    print("=" * 60)
    print("Excel Reader Tool - 読み上げ開始")
    print("=" * 60)
    print(f"ファイル: {args.file}")
    print(f"シート: {args.sheet}")
    print(f"読み上げ速度: {args.speed}")
    print(f"列間の待ち時間: {args.column_delay}秒")
    print("=" * 60)
    print("読み上げ中...（Ctrl+Cで停止）")
    print()
    
    try:
        reader = ExcelReader(config)
        result = reader.read_excel()
        
        print()
        print("=" * 60)
        if result['success']:
            print(f"[OK] {result['message']}")
        else:
            print(f"[ERROR] {result['message']}", file=sys.stderr)
            sys.exit(1)
        print("=" * 60)
        
    except KeyboardInterrupt:
        print()
        print("\n[INFO] 読み上げを停止しました")
        reader.stop()
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] 予期しないエラーが発生しました: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()


