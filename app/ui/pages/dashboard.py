"""
dashboard.py
============
Landing page showing at-a-glance system status cards and a recent
activity feed. Refreshes its stats every time the page is shown.
"""

from __future__ import annotations

from datetime import datetime

import customtkinter as ctk

from app.core.file_utils import count_all_images
from app.ui import theme
from app.ui.context import AppContext
from app.ui.widgets.info_card import InfoCard


class DashboardPage(ctk.CTkFrame):
    def __init__(self, master, context: AppContext):
        super().__init__(master, fg_color=theme.BG_PRIMARY, corner_radius=0)
        self._context = context
        self._activity_log: list[str] = []

        self._build_header()
        self._build_cards()
        self._build_activity_feed()
        self.refresh()

    # ------------------------------------------------------------------
    def _build_header(self) -> None:
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=theme.PAD_LARGE, pady=(theme.PAD_LARGE, theme.PAD_MEDIUM))

        ctk.CTkLabel(header, text="Dashboard", font=theme.FONT_TITLE, text_color=theme.TEXT_PRIMARY).pack(anchor="w")
        ctk.CTkLabel(
            header,
            text="System overview and recent activity",
            font=theme.FONT_SUBTITLE,
            text_color=theme.TEXT_SECONDARY,
        ).pack(anchor="w")

    def _build_cards(self) -> None:
        grid = ctk.CTkFrame(self, fg_color="transparent")
        grid.pack(fill="x", padx=theme.PAD_LARGE, pady=theme.PAD_SMALL)
        for col in range(4):
            grid.grid_columnconfigure(col, weight=1, uniform="cards")

        self._card_persons = InfoCard(grid, "👥", "Registered Persons", "0")
        self._card_images = InfoCard(grid, "🖼️", "Stored Images", "0")
        self._card_last_enroll = InfoCard(grid, "🕒", "Last Enrollment", "Never")
        self._card_camera = InfoCard(grid, "📷", "Camera Status", "Idle", accent=theme.NEUTRAL)
        self._card_recognition = InfoCard(grid, "🧠", "Recognition Status", "Idle", accent=theme.NEUTRAL)
        self._card_robot = InfoCard(grid, "🤖", "Robot Status", "Simulated", accent=theme.NEUTRAL)
        self._card_calibration = InfoCard(grid, "📐", "Distance Calibration", "Configured", accent=theme.SUCCESS)

        cards = [
            self._card_persons, self._card_images, self._card_last_enroll, self._card_camera,
            self._card_recognition, self._card_robot, self._card_calibration,
        ]
        for idx, card in enumerate(cards):
            row, col = divmod(idx, 4)
            card.grid(row=row, column=col, sticky="nsew", padx=8, pady=8)

    def _build_activity_feed(self) -> None:
        section = ctk.CTkFrame(self, fg_color=theme.BG_CARD, corner_radius=theme.CORNER_RADIUS)
        section.pack(fill="both", expand=True, padx=theme.PAD_LARGE, pady=(theme.PAD_MEDIUM, theme.PAD_LARGE))

        ctk.CTkLabel(
            section, text="Recent Activity", font=theme.FONT_HEADING, text_color=theme.TEXT_PRIMARY
        ).pack(anchor="w", padx=theme.PAD_MEDIUM, pady=(theme.PAD_MEDIUM, 4))

        self._activity_box = ctk.CTkTextbox(
            section, fg_color=theme.BG_SECONDARY, text_color=theme.TEXT_SECONDARY,
            font=theme.FONT_MONO, wrap="word", state="disabled",
        )
        self._activity_box.pack(fill="both", expand=True, padx=theme.PAD_MEDIUM, pady=(0, theme.PAD_MEDIUM))

    # ------------------------------------------------------------------
    def log_activity(self, message: str) -> None:
        timestamp = datetime.now().strftime("%H:%M:%S")
        self._activity_log.insert(0, f"[{timestamp}] {message}")
        self._activity_log = self._activity_log[:50]
        self._render_activity()

    def _render_activity(self) -> None:
        self._activity_box.configure(state="normal")
        self._activity_box.delete("1.0", "end")
        if not self._activity_log:
            self._activity_box.insert("1.0", "No activity yet. Enroll a person or start Live Recognition to begin.")
        else:
            self._activity_box.insert("1.0", "\n".join(self._activity_log))
        self._activity_box.configure(state="disabled")

    def refresh(self) -> None:
        """Recompute and redisplay all dashboard statistics."""
        db = self._context.database
        config = self._context.config

        total_persons = db.total_persons()
        total_images = count_all_images(config.images_root)
        last_enrollment = db.last_enrollment_timestamp() or "Never"

        self._card_persons.set_value(str(total_persons))
        self._card_images.set_value(str(total_images))
        self._card_last_enroll.set_value(last_enrollment if last_enrollment == "Never" else last_enrollment.split("T")[0])
        self._render_activity()

    def set_camera_status(self, status: str) -> None:
        self._card_camera.set_value(status)

    def set_recognition_status(self, status: str) -> None:
        self._card_recognition.set_value(status)

    def set_robot_status(self, status: str) -> None:
        self._card_robot.set_value(status)
