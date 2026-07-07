"""
info_card.py
============
Reusable dashboard "stat card" widget: icon/emoji, big value, small
label, with a subtle hover effect - mirrors the card components found
in modern commercial admin dashboards.
"""

from __future__ import annotations

import customtkinter as ctk

from app.ui import theme


class InfoCard(ctk.CTkFrame):
    def __init__(self, master, icon: str, label: str, value: str, accent: str = theme.ACCENT, **kwargs):
        super().__init__(
            master,
            fg_color=theme.BG_CARD,
            corner_radius=theme.CORNER_RADIUS,
            border_width=1,
            border_color=theme.BORDER,
            **kwargs,
        )
        self.grid_columnconfigure(0, weight=1)

        self._icon_label = ctk.CTkLabel(
            self, text=icon, font=("Segoe UI Emoji", 26), text_color=accent
        )
        self._icon_label.grid(row=0, column=0, sticky="w", padx=theme.PAD_MEDIUM, pady=(theme.PAD_MEDIUM, 0))

        self._value_label = ctk.CTkLabel(
            self, text=value, font=theme.FONT_CARD_VALUE, text_color=theme.TEXT_PRIMARY
        )
        self._value_label.grid(row=1, column=0, sticky="w", padx=theme.PAD_MEDIUM, pady=(4, 0))

        self._name_label = ctk.CTkLabel(
            self, text=label, font=theme.FONT_CARD_LABEL, text_color=theme.TEXT_SECONDARY
        )
        self._name_label.grid(row=2, column=0, sticky="w", padx=theme.PAD_MEDIUM, pady=(0, theme.PAD_MEDIUM))

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        for child in (self._icon_label, self._value_label, self._name_label):
            child.bind("<Enter>", self._on_enter)
            child.bind("<Leave>", self._on_leave)

    def _on_enter(self, _event=None) -> None:
        self.configure(fg_color=theme.BG_CARD_HOVER)

    def _on_leave(self, _event=None) -> None:
        self.configure(fg_color=theme.BG_CARD)

    def set_value(self, value: str) -> None:
        self._value_label.configure(text=value)
