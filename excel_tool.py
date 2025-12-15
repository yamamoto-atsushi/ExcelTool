#!/usr/bin/env python3
"""
Excel Tool - VLOOKUP-like functionality (Command Line Interface)
比較する2つのExcelファイルから、キーワード列でマッチングし、
指定列のデータをコピーするツール（コマンドライン版）
"""

import sys
import argparse
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core import ExcelVLookupProcessor  # noqa: E402
from utils import ConfigManager  # noqa: E402


class ExcelVLookupTool:
    """Excelファイルを比較してVLOOKUP風の機能を提供するクラス（後方互換性のためのラッパー）"""

    def __init__(self, config):
        """初期化（後方互換性のため）"""
        self.processor = ExcelVLookupProcessor(config)
        self.config = config

    def execute(self):
        """メイン処理を実行"""
        print("=" * 60)
        print("Excel VLOOKUP Tool - 処理開始")
        print("=" * 60)

        result = self.processor.execute()

        if result['success']:
            print(f"[OK] ソースファイル読み込み完了: {result['source_rows']}行")
            print(f"[OK] ターゲットファイル読み込み完了: {result['target_rows']}行")
            print(f"[OK] マッチング完了: {result['matched_count']}行がマッチしました")
            print(f"[OK] 結果を保存しました: {result['output_file']}")
        else:
            print(f"[ERROR] {result['message']}", file=sys.stderr)
            sys.exit(1)

        print("=" * 60)
        print("処理完了")
        print("=" * 60)


def load_config(config_file: str):
    """設定ファイルを読み込む"""
    try:
        return ConfigManager.load_config(config_file)
    except FileNotFoundError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)


def create_sample_config(output_file: str = "config_sample.json"):
    """サンプル設定ファイルを作成"""
    try:
        ConfigManager.create_sample_config(output_file)
        print(f"[OK] サンプル設定ファイルを作成しました: {output_file}")
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description='Excel VLOOKUP Tool - 2つのExcelファイルを比較してデータをコピー'
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
        print("  python excel_tool.py config.json")
        print("  python excel_tool.py --create-sample")
        sys.exit(1)

    # 設定読み込み
    config = load_config(args.config)

    # ツール実行
    tool = ExcelVLookupTool(config)
    tool.execute()


if __name__ == '__main__':
    main()
