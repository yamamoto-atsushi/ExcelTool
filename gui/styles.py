"""
Apple-inspired UI/UX Styles
Apple UI/UXデザインに準拠したスタイル定義
"""

from typing import Dict, Any


class AppleStyle:
    """Apple UI/UXに準拠したスタイル定義"""
    
    # カラーパレット（Apple風）
    COLORS = {
        'background': '#F5F5F7',  # ライトグレー背景
        'surface': '#FFFFFF',     # 白い表面
        'primary': '#007AFF',     # Apple Blue
        'primary_hover': '#0051D5',
        'secondary': '#8E8E93',   # グレー
        'text_primary': '#1D1D1F',  # ダークグレー
        'text_secondary': '#6E6E73',  # ミディアムグレー
        'success': '#34C759',     # Apple Green
        'error': '#FF3B30',       # Apple Red
        'warning': '#FF9500',     # Apple Orange
        'border': '#D1D1D6',      # ライトボーダー
        'shadow': '#00000015',    # 影（透明度付き）
    }
    
    # フォント設定（Windows互換性のためSegoe UIを使用）
    FONTS = {
        'title': ('Segoe UI', 28, 'normal'),
        'heading': ('Segoe UI', 20, 'normal'),
        'body': ('Segoe UI', 14, 'normal'),
        'body_bold': ('Segoe UI', 14, 'bold'),
        'caption': ('Segoe UI', 12, 'normal'),
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
    def get_button_style(cls, variant: str = 'primary') -> Dict[str, Any]:
        """
        ボタンスタイルを取得
        
        Args:
            variant: ボタンのバリアント ('primary', 'secondary', 'success', 'error')
            
        Returns:
            スタイル辞書
        """
        base_style = {
            'relief': 'flat',
            'borderwidth': 1,
            'cursor': 'hand2',
            'font': cls.FONTS['body_bold'],
        }
        
        if variant == 'primary':
            return {
                **base_style,
                'bg': cls.COLORS['primary'],
                'fg': '#FFFFFF',
                'activebackground': cls.COLORS['primary_hover'],
                'activeforeground': '#FFFFFF',
                'highlightbackground': cls.COLORS['primary'],
                'highlightthickness': 0,
                'relief': 'flat',
                'borderwidth': 0,
            }
        elif variant == 'secondary':
            return {
                **base_style,
                'bg': cls.COLORS['surface'],
                'fg': cls.COLORS['text_primary'],
                'activebackground': cls.COLORS['background'],
                'activeforeground': cls.COLORS['text_primary'],
                'highlightbackground': cls.COLORS['border'],
                'highlightthickness': 1,
                'relief': 'solid',
                'borderwidth': 1,
            }
        elif variant == 'success':
            return {
                **base_style,
                'bg': cls.COLORS['success'],
                'fg': '#FFFFFF',
                'activebackground': '#2AAD4A',
                'activeforeground': '#FFFFFF',
                'highlightbackground': cls.COLORS['success'],
                'highlightthickness': 0,
            }
        elif variant == 'error':
            return {
                **base_style,
                'bg': cls.COLORS['error'],
                'fg': '#FFFFFF',
                'activebackground': '#D32F2F',
                'activeforeground': '#FFFFFF',
                'highlightbackground': cls.COLORS['error'],
                'highlightthickness': 0,
            }
        else:
            return base_style
    
    @classmethod
    def get_entry_style(cls) -> Dict[str, Any]:
        """
        エントリースタイルを取得
        
        Returns:
            スタイル辞書
        """
        return {
            'relief': 'flat',
            'borderwidth': 1,
            'bg': cls.COLORS['surface'],
            'fg': cls.COLORS['text_primary'],
            'font': cls.FONTS['body'],
            'highlightthickness': 2,
            'highlightbackground': cls.COLORS['border'],
            'highlightcolor': cls.COLORS['primary'],
            'insertbackground': cls.COLORS['primary'],
        }
    
    @classmethod
    def get_label_style(cls, variant: str = 'body', bg_color: str = None) -> Dict[str, Any]:
        """
        ラベルスタイルを取得
        
        Args:
            variant: ラベルのバリアント ('title', 'heading', 'body', 'caption')
            bg_color: 背景色（Noneの場合は親の背景に合わせる）
            
        Returns:
            スタイル辞書
        """
        # 背景色が指定されていない場合は、親の背景に合わせる（システムデフォルト）
        if bg_color is None:
            # システムデフォルトの背景色を使用（親ウィジェットの背景に合わせる）
            style = {
                'fg': cls.COLORS['text_primary'],
            }
        else:
            style = {
                'bg': bg_color,
                'fg': cls.COLORS['text_primary'],
            }
        
        if variant == 'title':
            style['font'] = cls.FONTS['title']
        elif variant == 'heading':
            style['font'] = cls.FONTS['heading']
        elif variant == 'caption':
            style['font'] = cls.FONTS['caption']
            style['fg'] = cls.COLORS['text_secondary']
        else:  # body
            style['font'] = cls.FONTS['body']
        
        return style
    
    @classmethod
    def get_frame_style(cls, variant: str = 'surface') -> Dict[str, Any]:
        """
        フレームスタイルを取得
        
        Args:
            variant: フレームのバリアント ('background', 'surface', 'card')
            
        Returns:
            スタイル辞書
        """
        if variant == 'surface':
            return {
                'bg': cls.COLORS['surface'],
                'relief': 'flat',
                'borderwidth': 0,
            }
        elif variant == 'card':
            # カードスタイル（軽いボーダーで視覚的分離）
            return {
                'bg': cls.COLORS['surface'],
                'relief': 'flat',
                'borderwidth': 1,
                'highlightbackground': cls.COLORS['border'],
                'highlightthickness': 1,
            }
        else:  # background
            return {
                'bg': cls.COLORS['background'],
                'relief': 'flat',
                'borderwidth': 0,
            }

