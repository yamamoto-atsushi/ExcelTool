"""
Column Mapper Component
列マッピングコンポーネント
"""

import tkinter as tk
from tkinter import ttk
from typing import List, Dict, Optional, Callable
from gui.styles import AppleStyle


class ColumnMapper(tk.Frame):
    """列マッピングコンポーネント"""
    
    def __init__(self, parent, title: str, source_columns: List[str] = None,
                 target_columns: List[str] = None, callback: Optional[Callable] = None, **kwargs):
        """
        初期化
        
        Args:
            parent: 親ウィジェット
            title: タイトル
            source_columns: ソース側の利用可能な列のリスト
            target_columns: ターゲット側の利用可能な列のリスト
            callback: マッピング変更時のコールバック関数
        """
        super().__init__(parent, **AppleStyle.get_frame_style('surface'))
        self.source_columns = source_columns or []
        self.target_columns = target_columns or []
        self.callback = callback
        self.mappings: List[Dict[str, str]] = []
        
        # レイアウト
        self._create_widgets(title)
    
    def _create_widgets(self, title: str):
        """ウィジェットを作成"""
        # タイトル（空の場合は表示しない）
        if title:
            title_label = tk.Label(
                self,
                text=title,
                **AppleStyle.get_label_style('heading')
            )
            title_label.pack(anchor='w', pady=(0, AppleStyle.SPACING['md']))
        
        # マッピングリストのフレーム
        self.mappings_frame = tk.Frame(self, **AppleStyle.get_frame_style('surface'))
        self.mappings_frame.pack(fill='both', expand=True)
        
        # 追加ボタン
        add_btn = tk.Button(
            self,
            text="+ マッピングを追加",
            command=self._add_mapping,
            **AppleStyle.get_button_style('secondary')
        )
        add_btn.pack(pady=(AppleStyle.SPACING['sm'], 0))
    
    def _add_mapping(self, source: str = "", target: str = ""):
        """マッピングを追加"""
        mapping_frame = tk.Frame(
            self.mappings_frame,
            **AppleStyle.get_frame_style('surface')
        )
        mapping_frame.pack(fill='x', pady=(0, AppleStyle.SPACING['sm']))
        
        # ソース列
        source_label = tk.Label(
            mapping_frame,
            text="ソース:",
            **AppleStyle.get_label_style('body')
        )
        source_label.pack(side='left', padx=(0, AppleStyle.SPACING['sm']))
        
        source_var = tk.StringVar(value=source)
        source_combo = ttk.Combobox(
            mapping_frame,
            textvariable=source_var,
            values=self.source_columns,
            state='readonly',
            width=20
        )
        source_combo.pack(side='left', padx=(0, AppleStyle.SPACING['md']))
        
        # ターゲット列
        target_label = tk.Label(
            mapping_frame,
            text="ターゲット:",
            **AppleStyle.get_label_style('body')
        )
        target_label.pack(side='left', padx=(0, AppleStyle.SPACING['sm']))
        
        target_var = tk.StringVar(value=target)
        target_combo = ttk.Combobox(
            mapping_frame,
            textvariable=target_var,
            values=self.target_columns,
            state='readonly',
            width=20
        )
        target_combo.pack(side='left', padx=(0, AppleStyle.SPACING['md']))
        
        # 削除ボタン
        remove_btn = tk.Button(
            mapping_frame,
            text="削除",
            command=lambda: self._remove_mapping(mapping_frame),
            **AppleStyle.get_button_style('error')
        )
        remove_btn.pack(side='right')
        
        # 変更時のコールバック
        def on_change(*args):
            if self.callback:
                self.callback()
        
        source_var.trace('w', on_change)
        target_var.trace('w', on_change)
        
        # フレームに変数とコンボボックスへの参照を保存
        mapping_frame.source_var = source_var
        mapping_frame.target_var = target_var
        mapping_frame.source_combo = source_combo
        mapping_frame.target_combo = target_combo
    
    def _remove_mapping(self, mapping_frame: tk.Frame):
        """マッピングを削除"""
        mapping_frame.destroy()
        if self.callback:
            self.callback()
    
    def set_source_columns(self, columns: List[str]):
        """ソース側の利用可能な列を設定"""
        self.source_columns = columns
        # 既存のソースコンボボックスを更新
        for widget in self.mappings_frame.winfo_children():
            if isinstance(widget, tk.Frame) and hasattr(widget, 'source_combo'):
                widget.source_combo['values'] = columns
    
    def set_target_columns(self, columns: List[str]):
        """ターゲット側の利用可能な列を設定"""
        self.target_columns = columns
        # 既存のターゲットコンボボックスを更新
        for widget in self.mappings_frame.winfo_children():
            if isinstance(widget, tk.Frame) and hasattr(widget, 'target_combo'):
                widget.target_combo['values'] = columns
    
    def get_mappings(self) -> List[Dict[str, str]]:
        """マッピングのリストを取得"""
        mappings = []
        for widget in self.mappings_frame.winfo_children():
            if isinstance(widget, tk.Frame) and hasattr(widget, 'source_var'):
                source = widget.source_var.get()
                target = widget.target_var.get()
                if source and target:
                    mappings.append({
                        'source': source,
                        'target': target
                    })
        return mappings
    
    def set_mappings(self, mappings: List[Dict[str, str]]):
        """マッピングを設定"""
        # 既存のマッピングをクリア
        for widget in self.mappings_frame.winfo_children():
            widget.destroy()
        
        # 新しいマッピングを追加
        for mapping in mappings:
            self._add_mapping(
                mapping.get('source', ''),
                mapping.get('target', '')
            )

