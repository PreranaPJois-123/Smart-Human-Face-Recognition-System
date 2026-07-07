"""
settings.py
===========
Settings page allowing the user to edit recognition thresholds,
distance thresholds, camera index, robot configuration, serial port,
and application theme. Changes are validated and persisted back to
config.yaml via AppConfig.save().
"""

from __future__ import annotations

import customtkinter as ctk

from app.ui import theme
from app.ui.context import AppContext
from app.ui.widgets.dialogs import show_info_dialog


class _SettingRow(ctk.CTkFrame):
    """A labeled entry row used repeatedly throughout the settings form."""

    def __init__(self, master, label: str, initial_value: str, description: str = ""):
        super().__init__(master, fg_color="transparent")
        self.columnconfigure(0, weight=1)

        text_frame = ctk.CTkFrame(self, fg_color="transparent")
        text_frame.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(text_frame, text=label, font=theme.FONT_BODY, text_color=theme.TEXT_PRIMARY).pack(anchor="w")
        if description:
            ctk.CTkLabel(
                text_frame, text=description, font=theme.FONT_CARD_LABEL, text_color=theme.TEXT_MUTED
            ).pack(anchor="w")

        self.entry = ctk.CTkEntry(self, width=140, height=34, fg_color=theme.BG_SECONDARY, border_color=theme.BORDER)
        self.entry.insert(0, initial_value)
        self.entry.grid(row=0, column=1, sticky="e", padx=(theme.PAD_MEDIUM, 0))

    def get(self) -> str:
        return self.entry.get().strip()


class SettingsPage(ctk.CTkFrame):
    def __init__(self, master, context: AppContext, on_saved=None):
        super().__init__(master, fg_color=theme.BG_PRIMARY, corner_radius=0)
        self._context = context
        self._on_saved = on_saved

        self._build_header()
        self._build_form()

    # ------------------------------------------------------------------
    def _build_header(self) -> None:
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=theme.PAD_LARGE, pady=(theme.PAD_LARGE, theme.PAD_SMALL))
        ctk.CTkLabel(header, text="Settings", font=theme.FONT_TITLE, text_color=theme.TEXT_PRIMARY).pack(anchor="w")
        ctk.CTkLabel(
            header, text="Configure recognition, distance, camera, and robot behavior",
            font=theme.FONT_SUBTITLE, text_color=theme.TEXT_SECONDARY,
        ).pack(anchor="w")

    def _build_form(self) -> None:
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=theme.PAD_LARGE, pady=(0, theme.PAD_LARGE))

        cfg = self._context.config

        self._section(scroll, "Recognition")
        self._similarity_row = self._row(scroll, "Similarity Threshold", str(cfg.recognition.similarity_threshold),
                                          "Minimum cosine similarity (0-1) to accept a match")
        self._smoothing_row = self._row(scroll, "Label Smoothing Window", str(cfg.recognition.recognition_smoothing_window),
                                         "Number of frames used to stabilize on-screen names")

        self._section(scroll, "Distance Estimation")
        self._too_close_row = self._row(scroll, "Too Close Max (cm)", str(cfg.distance.too_close_max_cm))
        self._ideal_max_row = self._row(scroll, "Ideal Max (cm)", str(cfg.distance.ideal_max_cm))
        self._too_far_max_row = self._row(scroll, "Too Far Max (cm)", str(cfg.distance.too_far_max_cm))
        self._focal_length_row = self._row(scroll, "Focal Length (px)", str(cfg.distance.focal_length_px),
                                            "Calibration constant - see distance_utils.calibrate_focal_length")

        self._section(scroll, "Camera")
        self._camera_index_row = self._row(scroll, "Camera Index", str(cfg.camera.device_index))

        self._section(scroll, "Robot")
        self._simulate_switch_var = ctk.BooleanVar(value=cfg.robot.simulate_hardware)
        simulate_row = ctk.CTkFrame(scroll, fg_color="transparent")
        simulate_row.pack(fill="x", pady=6)
        ctk.CTkLabel(simulate_row, text="Simulate Hardware", font=theme.FONT_BODY, text_color=theme.TEXT_PRIMARY).pack(side="left")
        ctk.CTkSwitch(
            simulate_row, text="", variable=self._simulate_switch_var,
            progress_color=theme.ACCENT,
        ).pack(side="right")

        self._serial_port_row = self._row(scroll, "Serial Port", cfg.robot.serial_port)
        self._baud_rate_row = self._row(scroll, "Baud Rate", str(cfg.robot.baud_rate))
        self._dead_zone_row = self._row(scroll, "Center Dead Zone (px)", str(cfg.robot.center_dead_zone_px))

        self._section(scroll, "Appearance")
        self._theme_menu = ctk.CTkOptionMenu(
            scroll, values=["dark", "light", "system"], fg_color=theme.BG_SECONDARY, button_color=theme.ACCENT,
        )
        self._theme_menu.set(cfg.app.theme)
        self._theme_menu.pack(fill="x", pady=6)

        ctk.CTkButton(
            scroll, text="💾  Save Settings", width=200, height=42, fg_color=theme.SUCCESS, hover_color="#27AE60",
            font=theme.FONT_BUTTON, command=self._save,
        ).pack(anchor="w", pady=theme.PAD_LARGE)

    def _section(self, master, title: str) -> None:
        ctk.CTkLabel(master, text=title, font=theme.FONT_HEADING, text_color=theme.TEXT_PRIMARY).pack(
            anchor="w", pady=(theme.PAD_MEDIUM, 4)
        )
        ctk.CTkFrame(master, fg_color=theme.BORDER, height=1).pack(fill="x", pady=(0, 6))

    def _row(self, master, label: str, value: str, description: str = "") -> _SettingRow:
        row = _SettingRow(master, label, value, description)
        row.pack(fill="x", pady=6)
        return row

    # ------------------------------------------------------------------
    def _save(self) -> None:
        cfg = self._context.config
        try:
            similarity = float(self._similarity_row.get())
            smoothing = int(self._smoothing_row.get())
            too_close = int(self._too_close_row.get())
            ideal_max = int(self._ideal_max_row.get())
            too_far_max = int(self._too_far_max_row.get())
            focal_length = float(self._focal_length_row.get())
            camera_index = int(self._camera_index_row.get())
            baud_rate = int(self._baud_rate_row.get())
            dead_zone = int(self._dead_zone_row.get())
            serial_port = self._serial_port_row.get()

            if not (0.0 <= similarity <= 1.0):
                raise ValueError("Similarity Threshold must be between 0 and 1")
            if not (too_close < ideal_max < too_far_max):
                raise ValueError("Distance thresholds must satisfy Too Close < Ideal Max < Too Far Max")

        except ValueError as exc:
            show_info_dialog(self, "Invalid Settings", f"Please correct the following:\n{exc}", success=False)
            return

        cfg.recognition.similarity_threshold = similarity
        cfg.recognition.recognition_smoothing_window = smoothing
        cfg.distance.too_close_max_cm = too_close
        cfg.distance.ideal_min_cm = too_close
        cfg.distance.ideal_max_cm = ideal_max
        cfg.distance.too_far_max_cm = too_far_max
        cfg.distance.focal_length_px = focal_length
        cfg.camera.device_index = camera_index
        cfg.robot.simulate_hardware = self._simulate_switch_var.get()
        cfg.robot.serial_port = serial_port
        cfg.robot.baud_rate = baud_rate
        cfg.robot.center_dead_zone_px = dead_zone
        cfg.app.theme = self._theme_menu.get()

        cfg.save()
        self._context.reload_config()

        ctk.set_appearance_mode(cfg.app.theme)
        show_info_dialog(self, "Settings Saved", "Your configuration changes have been saved successfully.", success=True)

        if self._on_saved:
            self._on_saved()
