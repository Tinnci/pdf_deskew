from dataclasses import dataclass


@dataclass
class ThemeColors:
    primary: str
    primary_light: str
    secondary: str
    background: str
    surface: str
    border: str
    text_primary: str
    text_secondary: str
    success: str
    error: str


# Define some default themes
LIGHT_THEME = ThemeColors(
    primary="#1a73e8",
    primary_light="rgba(26, 115, 232, 0.1)",
    secondary="#5f6368",
    background="#f0f2f5",  # Softer grey-blue background
    surface="#fdfdfd",  # Off-white surface
    border="#dcdfe6",
    text_primary="#2c3e50",
    text_secondary="#606266",
    success="#67c23a",
    error="#f56c6c",
)

DARK_THEME = ThemeColors(
    primary="#409eff",
    primary_light="rgba(64, 158, 255, 0.1)",
    secondary="#909399",
    background="#1a1a1a",
    surface="#2d2d2d",
    border="#4c4c4c",
    text_primary="#e5eaf3",
    text_secondary="#a8abb2",
    success="#67c23a",
    error="#f56c6c",
)

BLUE_THEME = ThemeColors(
    primary="#0052cc",
    primary_light="rgba(0, 82, 204, 0.1)",
    secondary="#42526e",
    background="#f4f5f7",
    surface="#ffffff",
    border="#dfe1e6",
    text_primary="#172b4d",
    text_secondary="#42526e",
    success="#36b37e",
    error="#ff5630",
)


class StyleManager:
    _current_theme = LIGHT_THEME

    @classmethod
    def set_theme(cls, theme_name: str):
        if theme_name.lower() == "dark":
            cls._current_theme = DARK_THEME
        elif theme_name.lower() == "blue":
            cls._current_theme = BLUE_THEME
        else:
            cls._current_theme = LIGHT_THEME

    @classmethod
    def get_theme(cls) -> ThemeColors:
        return cls._current_theme

    @classmethod
    def get_main_style(cls) -> str:
        theme = cls._current_theme
        return f"""
            QMainWindow {{
                background-color: {theme.background};
            }}
            QWidget {{
                color: {theme.text_primary};
            }}
        """

    @classmethod
    def get_sidebar_style(cls) -> str:
        theme = cls._current_theme
        return f"""
            QScrollArea {{
                background-color: {theme.background};
                border: none;
            }}
        """

    @classmethod
    def get_preview_panel_style(cls) -> str:
        theme = cls._current_theme
        return f"""
            background-color: {theme.background};
        """

    @classmethod
    def get_preview_label_style(cls) -> str:
        theme = cls._current_theme
        return f"""
            background-color: {theme.surface};
            border: 1px solid {theme.border};
            border-radius: 8px;
        """
