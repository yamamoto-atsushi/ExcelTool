"""
Config Manager - Configuration file management
設定ファイルの読み込み、保存、検証を行う
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, Tuple


class ConfigManager:
    """設定ファイルの管理を行うクラス"""
    
    @staticmethod
    def load_config(config_file: str) -> Dict[str, Any]:
        """
        設定ファイルを読み込む
        
        Args:
            config_file: 設定ファイルのパス
            
        Returns:
            設定辞書
            
        Raises:
            FileNotFoundError: ファイルが見つからない場合
            json.JSONDecodeError: JSON形式が不正な場合
        """
        config_path = Path(config_file)
        if not config_path.exists():
            raise FileNotFoundError(f"設定ファイル '{config_file}' が見つかりません")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"設定ファイルのJSON形式が不正です: {e}", e.doc, e.pos)
    
    @staticmethod
    def save_config(config: Dict[str, Any], output_file: str) -> None:
        """
        設定ファイルを保存する
        
        Args:
            config: 設定辞書
            output_file: 出力ファイルパス
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    
    @staticmethod
    def create_sample_config(output_file: str = "config_sample.json") -> None:
        """
        サンプル設定ファイルを作成
        
        Args:
            output_file: 出力ファイルパス
        """
        sample_config = {
            "source_file": "source.xlsx",
            "target_file": "target.xlsx",
            "output_file": "output.xlsx",
            "source_sheet": 0,
            "target_sheet": 0,
            "match_columns": [
                {
                    "source": "キーワード列1",
                    "target": "キーワード列1"
                },
                {
                    "source": "キーワード列2",
                    "target": "キーワード列2"
                }
            ],
            "copy_columns": [
                {
                    "source": "コピー元列1",
                    "target": "コピー先列1"
                },
                {
                    "source": "コピー元列2",
                    "target": "コピー先列2"
                }
            ]
        }
        
        ConfigManager.save_config(sample_config, output_file)
    
    @staticmethod
    def validate_config(config: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        設定ファイルの検証
        
        Args:
            config: 設定辞書
            
        Returns:
            (is_valid, error_message) のタプル
        """
        required_fields = ['source_file', 'target_file', 'output_file', 
                          'match_columns', 'copy_columns']
        
        for field in required_fields:
            if field not in config:
                return False, f"必須フィールド '{field}' が設定されていません"
        
        if not isinstance(config['match_columns'], list) or len(config['match_columns']) == 0:
            return False, "'match_columns' は空でないリストである必要があります"
        
        if not isinstance(config['copy_columns'], list) or len(config['copy_columns']) == 0:
            return False, "'copy_columns' は空でないリストである必要があります"
        
        for match_col in config['match_columns']:
            if 'source' not in match_col or 'target' not in match_col:
                return False, "'match_columns' の各要素には 'source' と 'target' が必要です"
        
        for copy_col in config['copy_columns']:
            if 'source' not in copy_col or 'target' not in copy_col:
                return False, "'copy_columns' の各要素には 'source' と 'target' が必要です"
        
        return True, None

