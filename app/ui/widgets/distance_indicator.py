"""
distance_indicator.py
======================
Circular, color-coded distance-zone indicator shown on the Live
Recognition and Robot Mode pages. Updates live as the distance reading
changes between TOO CLOSE / IDEAL / TOO FAR / OUT OF RANGE.
"""

from __future__ import annotations

import tkinter as tk

import customtkinter as ctk

from app.core.distance_utils import DistanceReading
from app.ui import theme


class DistanceIndicator(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        # CustomTkinter has no native Canvas widget, so the raw tkinter
        # Canvas is used here for drawing the colored circular indicator.
        self._canvas = tk.Canvas(
            self, width=90, height=90, bg=theme.BG_CARD, highlightthickness=0
        )
        self._canvas.pack(side="left", padx=(0, theme.PAD_MEDIUM))
        self._circle = self._canvas.create_oval(10, 10, 80, 80, fill=theme.NEUTRAL, outline="")

        text_frame = ctk.CTkFrame(self, fg_color="transparent")
        text_frame.pack(side="left", fill="y")

        self._distance_label = ctk.CTkLabel(
            text_frame, text="-- cm", font=theme.FONT_HEADING, text_color=theme.TEXT_PRIMARY
        )
        self._distance_label.pack(anchor="w")

        self._zone_label = ctk.CTkLabel(
            text_frame, text="NO FACE DETECTED", font=theme.FONT_CARD_LABEL, text_color=theme.TEXT_SECONDARY
        )
        self._zone_label.pack(anchor="w")

    def update_reading(self, reading: DistanceReading) -> None:
        self._canvas.itemconfig(self._circle, fill=reading.color_hex)
        if reading.distance_cm >= 0:
            self._distance_label.configure(text=f"{reading.distance_cm:.0f} cm")
        else:
            self._distance_label.configure(text="-- cm")
        self._zone_label.configure(text=reading.label)

    def clear(self) -> None:
        self._canvas.itemconfig(self._circle, fill=theme.NEUTRAL)
        self._distance_label.configure(text="-- cm")
        self._zone_label.configure(text="NO FACE DETECTED")
