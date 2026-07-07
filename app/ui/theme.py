"""
theme.py
========
Centralized visual design tokens (colors, fonts, spacing) so every page
and widget shares a single, consistent professional dark theme instead
of hard-coding colors throughout the codebase.
"""

from __future__ import annotations

# Core palette - modern dark UI, blue accent.
BG_PRIMARY = "#1A1D23"
BG_SECONDARY = "#22262E"
BG_SIDEBAR = "#14171C"
BG_CARD = "#262B34"
BG_CARD_HOVER = "#2E343F"

ACCENT = "#3B82F6"
ACCENT_HOVER = "#2563EB"

SUCCESS = "#2ECC71"
WARNING = "#F1C40F"
DANGER = "#E74C3C"
NEUTRAL = "#5D6D7E"

TEXT_PRIMARY = "#F5F6F7"
TEXT_SECONDARY = "#9AA3AF"
TEXT_MUTED = "#5C6470"

BORDER = "#333944"

# Typography
FONT_FAMILY = "Segoe UI"
FONT_TITLE = (FONT_FAMILY, 24, "bold")
FONT_SUBTITLE = (FONT_FAMILY, 15, "normal")
FONT_HEADING = (FONT_FAMILY, 18, "bold")
FONT_CARD_VALUE = (FONT_FAMILY, 26, "bold")
FONT_CARD_LABEL = (FONT_FAMILY, 13, "normal")
FONT_BODY = (FONT_FAMILY, 13, "normal")
FONT_BUTTON = (FONT_FAMILY, 13, "bold")
FONT_NAV = (FONT_FAMILY, 14, "normal")
FONT_MONO = ("Consolas", 13, "normal")

# Spacing
PAD_SMALL = 8
PAD_MEDIUM = 16
PAD_LARGE = 24

CORNER_RADIUS = 12
SIDEBAR_WIDTH = 220
