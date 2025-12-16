"""
Column Mapper Component (PyQt6版)
列マッピングコンポーネント
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QFrame, QScrollArea
)
from PyQt6.QtCore import Qt
from PyQt6.QtCore import Qt
from typing import List, Dict, Optional, Callable
from gui_qt.styles import AppleStyle


class ColumnMapper(QWidget):
    """列マッピングコンポーネント（PyQt6版）"""
    
    def __init__(self, parent=None, title: str = "", source_columns: List[str] = None,
                 target_columns: List[str] = None, callback: Optional[Callable] = None):
        """
        初期化
        
        Args:
            parent: 親ウィジェット
            title: タイトル
            source_columns: ソース側の利用可能な列のリスト
            target_columns: ターゲット側の利用可能な列のリスト
            callback: マッピング変更時のコールバック関数
        """
        super().__init__(parent)
        self.source_columns = source_columns or []
        self.target_columns = target_columns or []
        self.callback = callback
        self.mappings: List[Dict[str, str]] = []
        self.mapping_widgets: List[Dict] = []
        
        # レイアウト
        self._create_widgets(title)
    
    def _create_widgets(self, title: str):
        """ウィジェットを作成"""
        layout = QVBoxLayout(self)
        layout.setSpacing(AppleStyle.SPACING['md'])
        layout.setContentsMargins(0, 0, 0, 0)
        
        # タイトル（空の場合は表示しない）
        if title:
            title_label = QLabel(title)
            title_style = AppleStyle.get_label_style('heading')
            title_label.setFont(title_style['font'])
            title_label.setStyleSheet(f"color: {title_style['color'].name()};")
            layout.addWidget(title_label)
        
        # マッピングリストのスクロールエリア
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        scroll_area.setMinimumHeight(100)
        scroll_area.setMaximumHeight(300)
        
        # マッピングリストのフレーム
        self.mappings_widget = QWidget()
        self.mappings_layout = QVBoxLayout(self.mappings_widget)
        self.mappings_layout.setSpacing(AppleStyle.SPACING['sm'])
        self.mappings_layout.setContentsMargins(0, 0, 0, 0)
        self.mappings_layout.addStretch()  # 下部にスペースを追加
        
        scroll_area.setWidget(self.mappings_widget)
        layout.addWidget(scroll_area)
        
        # 追加ボタン
        add_btn = QPushButton("+ マッピングを追加")
        add_btn.setStyleSheet(AppleStyle.get_button_style('secondary'))
        add_btn.clicked.connect(self._add_mapping)
        layout.addWidget(add_btn)
    
    def _add_mapping(self, source: str = "", target: str = ""):
        """マッピングを追加"""
        mapping_widget = QFrame()
        mapping_widget.setFrameShape(QFrame.Shape.NoFrame)
        mapping_widget.setStyleSheet("QFrame { border: none; }")
        mapping_layout = QHBoxLayout(mapping_widget)
        mapping_layout.setSpacing(AppleStyle.SPACING['sm'])
        mapping_layout.setContentsMargins(
            AppleStyle.SPACING['sm'],
            AppleStyle.SPACING['sm'],
            AppleStyle.SPACING['sm'],
            AppleStyle.SPACING['sm']
        )
        
        # ソース列
        source_label = QLabel("ソース:")
        label_style = AppleStyle.get_label_style('body')
        source_label.setFont(label_style['font'])
        source_label.setStyleSheet(f"color: {label_style['color'].name()};")
        mapping_layout.addWidget(source_label)
        
        source_combo = QComboBox()
        source_combo.addItems(self.source_columns)
        if source:
            index = source_combo.findText(source)
            if index >= 0:
                source_combo.setCurrentIndex(index)
        source_combo.setMinimumWidth(150)
        source_combo.currentTextChanged.connect(self._on_mapping_changed)
        mapping_layout.addWidget(source_combo)
        
        # ターゲット列
        target_label = QLabel("ターゲット:")
        target_label.setFont(label_style['font'])
        target_label.setStyleSheet(f"color: {label_style['color'].name()};")
        mapping_layout.addWidget(target_label)
        
        target_combo = QComboBox()
        target_combo.addItems(self.target_columns)
        if target:
            index = target_combo.findText(target)
            if index >= 0:
                target_combo.setCurrentIndex(index)
        target_combo.setMinimumWidth(150)
        target_combo.currentTextChanged.connect(self._on_mapping_changed)
        mapping_layout.addWidget(target_combo)
        
        # 削除ボタン
        remove_btn = QPushButton("削除")
        remove_btn.setStyleSheet(AppleStyle.get_button_style('error'))
        remove_btn.setMaximumWidth(60)
        remove_btn.clicked.connect(lambda: self._remove_mapping(mapping_widget))
        mapping_layout.addWidget(remove_btn)
        
        mapping_layout.addStretch()
        
        # マッピング情報を保存
        mapping_info = {
            'widget': mapping_widget,
            'source_combo': source_combo,
            'target_combo': target_combo
        }
        self.mapping_widgets.append(mapping_info)
        
        # ストレッチを削除してから追加
        # 最後のアイテムがストレッチかどうかを確認
        if self.mappings_layout.count() > 0:
            last_item = self.mappings_layout.itemAt(self.mappings_layout.count() - 1)
            if last_item and last_item.spacerItem():
                self.mappings_layout.removeItem(last_item)
        
        self.mappings_layout.addWidget(mapping_widget)
        self.mappings_layout.addStretch()  # 下部にスペースを追加
        
        # ウィジェットを表示
        mapping_widget.setVisible(True)
        mapping_widget.show()
        
        # コールバックを呼び出し
        self._on_mapping_changed()
    
    def _on_mapping_changed(self):
        """マッピングが変更されたときの処理"""
        if self.callback:
            self.callback()
    
    def _remove_mapping(self, widget: QWidget):
        """マッピングを削除"""
        # ウィジェット情報を削除
        for i, mapping_info in enumerate(self.mapping_widgets):
            if mapping_info['widget'] == widget:
                self.mapping_widgets.pop(i)
                break
        
        # ウィジェットを削除
        widget.setParent(None)
        widget.deleteLater()
        
        # コールバックを呼び出し
        self._on_mapping_changed()
    
    def set_source_columns(self, columns: List[str]):
        """ソース列を設定"""
        self.source_columns = columns
        for mapping_info in self.mapping_widgets:
            current_text = mapping_info['source_combo'].currentText()
            mapping_info['source_combo'].clear()
            mapping_info['source_combo'].addItems(columns)
            if current_text in columns:
                index = mapping_info['source_combo'].findText(current_text)
                if index >= 0:
                    mapping_info['source_combo'].setCurrentIndex(index)
    
    def set_target_columns(self, columns: List[str]):
        """ターゲット列を設定"""
        self.target_columns = columns
        for mapping_info in self.mapping_widgets:
            current_text = mapping_info['target_combo'].currentText()
            mapping_info['target_combo'].clear()
            mapping_info['target_combo'].addItems(columns)
            if current_text in columns:
                index = mapping_info['target_combo'].findText(current_text)
                if index >= 0:
                    mapping_info['target_combo'].setCurrentIndex(index)
    
    def get_mappings(self) -> List[Dict[str, str]]:
        """現在のマッピングを取得"""
        import json
        from pathlib import Path
        from datetime import datetime
        
        mappings = []
        for i, mapping_info in enumerate(self.mapping_widgets):
            source = mapping_info['source_combo'].currentText()
            target = mapping_info['target_combo'].currentText()
            source_index = mapping_info['source_combo'].currentIndex()
            target_index = mapping_info['target_combo'].currentIndex()
            
            # #region agent log
            log_path = Path(__file__).parent.parent.parent / '.cursor' / 'debug.log'
            try:
                with open(log_path, 'a', encoding='utf-8') as f:
                    f.write(json.dumps({
                        'sessionId': 'debug-session',
                        'runId': 'run1',
                        'hypothesisId': 'B,E',
                        'location': f'column_mapper.py:get_mappings:mapping_{i}',
                        'message': 'Individual mapping retrieved',
                        'data': {
                            'mapping_index': i,
                            'source_text': source,
                            'target_text': target,
                            'source_index': source_index,
                            'target_index': target_index,
                            'source_combo_items': [mapping_info['source_combo'].itemText(j) for j in range(mapping_info['source_combo'].count())],
                            'target_combo_items': [mapping_info['target_combo'].itemText(j) for j in range(mapping_info['target_combo'].count())]
                        },
                        'timestamp': int(datetime.now().timestamp() * 1000)
                    }) + '\n')
            except Exception:
                pass
            # #endregion
            
            if source and target:
                mappings.append({
                    'source': source,
                    'target': target
                })
        
        # #region agent log
        try:
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps({
                    'sessionId': 'debug-session',
                    'runId': 'run1',
                    'hypothesisId': 'B,E',
                    'location': 'column_mapper.py:get_mappings:final',
                    'message': 'Final mappings array',
                    'data': {
                        'mappings': mappings,
                        'source_columns': self.source_columns,
                        'target_columns': self.target_columns
                    },
                    'timestamp': int(datetime.now().timestamp() * 1000)
                }) + '\n')
        except Exception:
            pass
        # #endregion
        
        return mappings

