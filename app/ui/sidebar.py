"""
sidebar.py
==========
Left-hand navigation sidebar. Renders a button per application page and
highlights the currently active page, similar to modern desktop admin
tools (VS Code, Notion, commercial SaaS dashboards).
"""

from __future__ import annotations

from typing import Callable, Dict, List, Tuple

import customtkinter as ctk

from app.ui import theme

NAV_ITEMS: List[Tuple[str, str, str]] = [
    ("dashboard", "🏠", "Dashboard"),
    ("enroll", "👤", "Enroll Person"),
    ("registered", "📋", "Registered Persons"),
    ("live", "🎥", "Live Recognition"),
    ("robot", "🤖", "Robot Mode"),
    ("settings", "⚙", "Settings"),
]


class Sidebar(ctk.CTkFrame):
    def __init__(self, master, on_navigate: Callable[[str], None], on_exit: Callable[[], None]):
        super().__init__(master, width=theme.SIDEBAR_WIDTH, fg_color=theme.BG_SIDEBAR, corner_radius=0)
        self.grid_propagate(False)
        self._on_navigate = on_navigate
        self._on_exit = on_exit
        self._nav_buttons: Dict[str, ctk.CTkButton] = {}
        self._active_key = "dashboard"

        self._build_brand()
        self._build_nav_buttons()
        self._build_exit_button()

    def _build_brand(self) -> None:
        brand_frame = ctk.CTkFrame(self, fg_color="transparent")
        brand_frame.pack(fill="x", padx=theme.PAD_MEDIUM, pady=(theme.PAD_LARGE, theme.PAD_LARGE))

        ctk.CTkLabel(
            brand_frame, text="🛡️ VisionGuard", font=("Segoe UI", 19, "bold"), text_color=theme.TEXT_PRIMARY
        ).pack(anchor="w")
        ctk.CTkLabel(
            brand_frame, text="AI Recognition Suite", font=theme.FONT_CARD_LABEL, text_color=theme.TEXT_SECONDARY
        ).pack(anchor="w")

    def _build_nav_buttons(self) -> None:
        nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        nav_frame.pack(fill="x", padx=12)

        for key, icon, label in NAV_ITEMS:
            button = ctk.CTkButton(
                nav_frame,
                text=f"  {icon}   {label}",
                anchor="w",
                font=theme.FONT_NAV,
                fg_color="transparent",
                hover_color=theme.BG_CARD_HOVER,
                text_color=theme.TEXT_SECONDARY,
                corner_radius=8,
                height=42,
                command=lambda k=key: self._handle_click(k),
            )
            button.pack(fill="x", pady=3)
            self._nav_buttons[key] = button

        self._highlight_active()

    def _build_exit_button(self) -> None:
        exit_frame = ctk.CTkFrame(self, fg_color="transparent")
        exit_frame.pack(side="bottom", fill="x", padx=12, pady=theme.PAD_LARGE)

        ctk.CTkButton(
            exit_frame,
            text="  🚪   Exit",
            anchor="w",
            font=theme.FONT_NAV,
            fg_color="transparent",
            hover_color=theme.DANGER,
            text_color=theme.TEXT_SECONDARY,
            corner_radius=8,
            height=42,
            command=self._on_exit,
        ).pack(fill="x")

    def _handle_click(self, key: str) -> None:
        self._active_key = key
        self._highlight_active()
        self._on_navigate(key)

    def _highlight_active(self) -> None:
        for key, button in self._nav_buttons.items():
            if key == self._active_key:
                button.configure(fg_color=theme.ACCENT, text_color=theme.TEXT_PRIMARY)
            else:
                button.configure(fg_color="transparent", text_color=theme.TEXT_SECONDARY)
