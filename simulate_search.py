#!/usr/bin/env python3
"""
Excel Search Tool のシミュレーション実行スクリプト
テスト用のExcelファイルを作成して検索を実行します
"""

import pandas as pd
from pathlib import Path
import json
import shutil
from datetime import datetime
import sys

# テスト用のデータ
test_files = [
    {
        'name': 'プロジェクトA_2024年度.xlsx',
        'data': {
            'Sheet1': pd.DataFrame({
                '項目': ['プロジェクトA', '売上', '予算', '実績'],
                '値': [1000000, 950000, 50000, 45000]
            }),
            'Sheet2': pd.DataFrame({
                '部署': ['営業部', '開発部', '管理部'],
                '担当者': ['山田太郎', '鈴木花子', '佐藤次郎'],
                '備考': ['2024年度', 'プロジェクトA', '管理']
            })
        },
        'keywords': ['プロジェクトA', '2024年度']
    },
    {
        'name': '売上報告_2023.xlsx',
        'data': {
            'Sheet1': pd.DataFrame({
                '月': ['1月', '2月', '3月', '4月'],
                '売上': [500000, 600000, 700000, 800000],
                '備考': ['2023年度', '前期比110%', '好調', '売上増加']
            })
        },
        'keywords': ['売上']
    },
    {
        'name': '人事データ.xlsx',
        'data': {
            'Sheet1': pd.DataFrame({
                '名前': ['田中一郎', '伊藤三郎', '中村四郎'],
                '部署': ['総務部', '経理部', '人事部'],
                '入社日': ['2020-04-01', '2019-04-01', '2021-04-01']
            })
        },
        'keywords': []  # このファイルにはキーワードが含まれない
    },
    {
        'name': 'サブフォルダ/2024年度_予算.xlsx',
        'data': {
            'Sheet1': pd.DataFrame({
                '部門': ['営業', '開発', '管理'],
                '予算': [5000000, 8000000, 2000000],
                '備考': ['2024年度', 'プロジェクトA', '予算承認済み']
            })
        },
        'keywords': ['2024年度', 'プロジェクトA']  # このファイルにはキーワードが含まれる
    },
    {
        'name': 'サブフォルダ/売上実績.xlsx',
        'data': {
            'Sheet1': pd.DataFrame({
                '商品': ['商品A', '商品B', '商品C'],
                '数量': [100, 200, 150],
                '単価': [10000, 15000, 12000],
                '備考': ['売上目標達成', '売上増加', '売上好調']
            })
        },
        'keywords': ['売上']
    },
    {
        'name': 'サブフォルダ/その他データ.xlsx',
        'data': {
            'Sheet1': pd.DataFrame({
                'データ1': ['A', 'B', 'C'],
                'データ2': [1, 2, 3],
                'データ3': ['X', 'Y', 'Z']
            })
        },
        'keywords': []  # このファイルにはキーワードが含まれない
    }
]


def create_test_environment():
    """テスト用の環境を作成"""
    print("=" * 60)
    print("テスト環境の作成")
    print("=" * 60)
    
    # テスト用のフォルダを作成
    test_dir = Path('test_search_data')
    if test_dir.exists():
        print(f"[INFO] 既存のテストフォルダを削除: {test_dir}")
        shutil.rmtree(test_dir)
    
    test_dir.mkdir(exist_ok=True)
    (test_dir / 'サブフォルダ').mkdir(exist_ok=True)
    
    print(f"[OK] テストフォルダを作成: {test_dir}")
    
    # テスト用のExcelファイルを作成
    created_files = []
    for file_info in test_files:
        file_path = test_dir / file_info['name']
        
        # 親フォルダが存在することを確認
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 複数シートのExcelファイルを作成
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            for sheet_name, df in file_info['data'].items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        created_files.append(file_path)
        print(f"[OK] テストファイルを作成: {file_path}")
    
    print(f"[OK] {len(created_files)}個のテストファイルを作成しました")
    return test_dir


def create_test_config(test_dir: Path):
    """テスト用の設定ファイルを作成"""
    config = {
        "search_path": str(test_dir.resolve()),
        "keywords": [
            "プロジェクトA",
            "2024年度",
            "売上"
        ],
        "output_file": "test_search_results.xlsx",
        "recursive": True,
        "max_workers": 2,
        "case_sensitive": False
    }
    
    config_path = Path('config_test_search.json')
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    print(f"[OK] テスト設定ファイルを作成: {config_path}")
    return config_path


def run_simulation():
    """シミュレーションを実行"""
    print("\n" + "=" * 60)
    print("Excel Search Tool シミュレーション")
    print("=" * 60)
    
    try:
        # テスト環境を作成
        test_dir = create_test_environment()
        
        # テスト設定ファイルを作成
        config_path = create_test_config(test_dir)
        
        print("\n" + "=" * 60)
        print("検索ツールの実行")
        print("=" * 60)
        
        # excel_search.pyをインポートして実行
        from excel_search import ExcelSearchTool, load_config
        
        config = load_config(str(config_path))
        tool = ExcelSearchTool(config)
        tool.execute()
        
        print("\n" + "=" * 60)
        print("シミュレーション完了")
        print("=" * 60)
        print(f"\n検索結果は '{config['output_file']}' に保存されました")
        print(f"テストデータは '{test_dir}' にあります")
        print("\n期待される結果:")
        print("  - プロジェクトA_2024年度.xlsx: 'プロジェクトA', '2024年度' がマッチ")
        print("  - 売上報告_2023.xlsx: '売上' がマッチ")
        print("  - サブフォルダ/2024年度_予算.xlsx: '2024年度', 'プロジェクトA' がマッチ")
        print("  - サブフォルダ/売上実績.xlsx: '売上' がマッチ")
        print("  - 人事データ.xlsx: マッチなし（結果に含まれない）")
        print("  - サブフォルダ/その他データ.xlsx: マッチなし（結果に含まれない）")
        
    except Exception as e:
        print(f"\n[ERROR] シミュレーションエラー: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    run_simulation()

