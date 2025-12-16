"""
Apple-inspired UI/UX Styles for PyQt6
Apple UI/UXデザインに準拠したスタイル定義（PyQt6版）
"""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QPalette
from PyQt6.QtWidgets import QApplication
from typing import Dict, Any


class AppleStyle:
    """Apple UI/UXに準拠したスタイル定義（PyQt6版）"""
    
    # カラーパレット（Apple風）
    COLORS = {
        'background': QColor(245, 245, 247),  # #F5F5F7
        'surface': QColor(255, 255, 255),     # #FFFFFF
        'primary': QColor(0, 122, 255),       # #007AFF
        'primary_hover': QColor(0, 81, 213),  # #0051D5
        'secondary': QColor(142, 142, 147),   # #8E8E93
        'text_primary': QColor(29, 29, 31),    # #1D1D1F
        'text_secondary': QColor(110, 110, 115),  # #6E6E73
        'success': QColor(52, 199, 89),        # #34C759
        'error': QColor(255, 59, 48),          # #FF3B30
        'warning': QColor(255, 149, 0),        # #FF9500
        'border': QColor(209, 209, 214),      # #D1D1D6
    }
    
    # フォント設定
    FONTS = {
        'title': QFont('Segoe UI', 28, QFont.Weight.Normal),
        'heading': QFont('Segoe UI', 20, QFont.Weight.Normal),
        'body': QFont('Segoe UI', 14, QFont.Weight.Normal),
        'body_bold': QFont('Segoe UI', 14, QFont.Weight.Bold),
        'caption': QFont('Segoe UI', 12, QFont.Weight.Normal),
    }
    
    # スペーシング
    SPACING = {
        'xs': 4,
        'sm': 8,
        'md': 16,
        'lg': 24,
        'xl': 32,
        'xxl': 48,
    }
    
    # ボーダー半径
    BORDER_RADIUS = {
        'sm': 8,
        'md': 12,
        'lg': 16,
        'xl': 20,
    }
    
    @classmethod
    def get_button_style(cls, variant: str = 'primary') -> str:
        """
        ボタンスタイルシートを取得
        
        Args:
            variant: ボタンのバリアント ('primary', 'secondary', 'success', 'error')
            
        Returns:
            QSSスタイルシート文字列
        """
        if variant == 'primary':
            return f"""
                QPushButton {{
                    background-color: {cls.COLORS['primary'].name()};
                    color: white;
                    border: none;
                    border-radius: {cls.BORDER_RADIUS['md']}px;
                    padding: {cls.SPACING['sm']}px {cls.SPACING['md']}px;
                    font: {cls.FONTS['body_bold'].toString()};
                }}
                QPushButton:hover {{
                    background-color: {cls.COLORS['primary_hover'].name()};
                }}
                QPushButton:pressed {{
                    background-color: {cls.COLORS['primary_hover'].name()};
                }}
                QPushButton:disabled {{
                    background-color: {cls.COLORS['secondary'].name()};
                    color: {cls.COLORS['text_secondary'].name()};
                }}
            """
        elif variant == 'secondary':
            return f"""
                QPushButton {{
                    background-color: {cls.COLORS['surface'].name()};
                    color: {cls.COLORS['text_primary'].name()};
                    border: 1px solid {cls.COLORS['border'].name()};
                    border-radius: {cls.BORDER_RADIUS['md']}px;
                    padding: {cls.SPACING['sm']}px {cls.SPACING['md']}px;
                    font: {cls.FONTS['body_bold'].toString()};
                }}
                QPushButton:hover {{
                    background-color: {cls.COLORS['background'].name()};
                }}
                QPushButton:pressed {{
                    background-color: {cls.COLORS['background'].name()};
                }}
                QPushButton:disabled {{
                    background-color: {cls.COLORS['surface'].name()};
                    color: {cls.COLORS['text_secondary'].name()};
                    border-color: {cls.COLORS['border'].name()};
                }}
            """
        elif variant == 'success':
            return f"""
                QPushButton {{
                    background-color: {cls.COLORS['success'].name()};
                    color: white;
                    border: none;
                    border-radius: {cls.BORDER_RADIUS['md']}px;
                    padding: {cls.SPACING['sm']}px {cls.SPACING['md']}px;
                    font: {cls.FONTS['body_bold'].toString()};
                }}
                QPushButton:hover {{
                    background-color: #2AAD4A;
                }}
            """
        elif variant == 'error':
            return f"""
                QPushButton {{
                    background-color: {cls.COLORS['error'].name()};
                    color: white;
                    border: none;
                    border-radius: {cls.BORDER_RADIUS['md']}px;
                    padding: {cls.SPACING['sm']}px {cls.SPACING['md']}px;
                    font: {cls.FONTS['body_bold'].toString()};
                }}
                QPushButton:hover {{
                    background-color: #D32F2F;
                }}
            """
        else:
            return ""
    
    @classmethod
    def get_entry_style(cls) -> str:
        """
        エントリースタイルシートを取得
        
        Returns:
            QSSスタイルシート文字列
        """
        return f"""
            QLineEdit, QTextEdit {{
                background-color: {cls.COLORS['surface'].name()};
                color: {cls.COLORS['text_primary'].name()};
                border: 1px solid {cls.COLORS['border'].name()};
                border-radius: {cls.BORDER_RADIUS['sm']}px;
                padding: {cls.SPACING['sm']}px {cls.SPACING['md']}px;
                font: {cls.FONTS['body'].toString()};
                min-height: 20px;
            }}
            QLineEdit:focus, QTextEdit:focus {{
                border: 2px solid {cls.COLORS['primary'].name()};
                outline: none;
            }}
            QLineEdit:disabled, QTextEdit:disabled {{
                background-color: {cls.COLORS['background'].name()};
                color: {cls.COLORS['text_secondary'].name()};
            }}
        """
    
    @classmethod
    def get_label_style(cls, variant: str = 'body') -> Dict[str, Any]:
        """
        ラベルスタイルを取得
        
        Args:
            variant: ラベルのバリアント ('title', 'heading', 'body', 'caption')
            
        Returns:
            スタイル辞書（'font'と'color'を含む）
        """
        style = {}
        
        if variant == 'title':
            style['font'] = cls.FONTS['title']
            style['color'] = cls.COLORS['text_primary']
        elif variant == 'heading':
            style['font'] = cls.FONTS['heading']
            style['color'] = cls.COLORS['text_primary']
        elif variant == 'caption':
            style['font'] = cls.FONTS['caption']
            style['color'] = cls.COLORS['text_secondary']
        else:  # body
            style['font'] = cls.FONTS['body']
            style['color'] = cls.COLORS['text_primary']
        
        return style
    
    @classmethod
    def get_frame_style(cls, variant: str = 'surface') -> str:
        """
        フレームスタイルシートを取得
        
        Args:
            variant: フレームのバリアント ('background', 'surface', 'card')
            
        Returns:
            QSSスタイルシート文字列
        """
        if variant == 'surface':
            return f"""
                QFrame {{
                    background-color: {cls.COLORS['surface'].name()};
                    border: none;
                }}
            """
        elif variant == 'card':
            return f"""
                QFrame {{
                    background-color: {cls.COLORS['surface'].name()};
                    border: none;
                    border-radius: {cls.BORDER_RADIUS['md']}px;
                }}
            """
        else:  # background
            return f"""
                QFrame {{
                    background-color: {cls.COLORS['background'].name()};
                    border: none;
                }}
            """
    
    @classmethod
    def apply_global_style(cls, app: QApplication):
        """
        アプリケーション全体にスタイルを適用
        
        Args:
            app: QApplicationインスタンス
        """
        # パレットを設定
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, cls.COLORS['background'])
        palette.setColor(QPalette.ColorRole.WindowText, cls.COLORS['text_primary'])
        palette.setColor(QPalette.ColorRole.Base, cls.COLORS['surface'])
        palette.setColor(QPalette.ColorRole.AlternateBase, cls.COLORS['background'])
        palette.setColor(QPalette.ColorRole.Text, cls.COLORS['text_primary'])
        palette.setColor(QPalette.ColorRole.Button, cls.COLORS['surface'])
        palette.setColor(QPalette.ColorRole.ButtonText, cls.COLORS['text_primary'])
        palette.setColor(QPalette.ColorRole.Highlight, cls.COLORS['primary'])
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
        
        app.setPalette(palette)
        
        # グローバルスタイルシート
        global_style = f"""
            QMainWindow, QDialog, QWidget {{
                background-color: {cls.COLORS['background'].name()};
                color: {cls.COLORS['text_primary'].name()};
            }}
            QLabel {{
                border: none;
                background: transparent;
            }}
            QFrame {{
                border: none;
            }}
            QFrame[frameShape="0"] {{
                border: none;
            }}
            QFrame[frameShape="1"] {{
                border: none;
            }}
            QFrame[frameShape="2"] {{
                border: none;
            }}
            QFrame[frameShape="3"] {{
                border: none;
            }}
            QFrame[frameShape="4"] {{
                border: none;
            }}
            QFrame[frameShape="5"] {{
                border: none;
            }}
            QScrollBar:vertical {{
                background: {cls.COLORS['background'].name()};
                width: 12px;
                border: none;
            }}
            QScrollBar::handle:vertical {{
                background: {cls.COLORS['border'].name()};
                border-radius: 6px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {cls.COLORS['secondary'].name()};
            }}
        """
        app.setStyleSheet(global_style)

