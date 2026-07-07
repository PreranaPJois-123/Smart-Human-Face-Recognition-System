"""
dialogs.py
==========
Reusable modal dialogs: an indeterminate/determinate progress dialog
used during enrollment processing, and a three-way choice dialog used
when enrolling a name that already exists (Overwrite / Append / Cancel).
"""

from __future__ import annotations

from typing import Callable, Optional

import customtkinter as ctk

from app.ui import theme


class ProgressDialog(ctk.CTkToplevel):
    """Modal progress dialog with a determinate progress bar and status
    text, used while processing enrollment images."""

    def __init__(self, master, title: str = "Processing..."):
        super().__init__(master)
        self.title(title)
        self.geometry("420x160")
        self.resizable(False, False)
        self.configure(fg_color=theme.BG_SECONDARY)
        self.transient(master)
        self.grab_set()

        self._label = ctk.CTkLabel(self, text="Starting...", font=theme.FONT_BODY, text_color=theme.TEXT_PRIMARY)
        self._label.pack(pady=(30, 10), padx=20)

        self._progress = ctk.CTkProgressBar(self, width=360, progress_color=theme.ACCENT)
        self._progress.pack(pady=10, padx=20)
        self._progress.set(0)

        self._detail_label = ctk.CTkLabel(self, text="", font=theme.FONT_CARD_LABEL, text_color=theme.TEXT_SECONDARY)
        self._detail_label.pack(pady=(0, 10))

        self.protocol("WM_DELETE_WINDOW", lambda: None)  # prevent manual close mid-task
        self._center_on_parent(master)

    def _center_on_parent(self, master) -> None:
        self.update_idletasks()
        parent_x = master.winfo_rootx()
        parent_y = master.winfo_rooty()
        parent_w = master.winfo_width()
        parent_h = master.winfo_height()
        x = parent_x + (parent_w // 2) - 210
        y = parent_y + (parent_h // 2) - 80
        self.geometry(f"+{max(x, 0)}+{max(y, 0)}")

    def update_progress(self, fraction: float, message: str, detail: str = "") -> None:
        self._progress.set(max(0.0, min(1.0, fraction)))
        self._label.configure(text=message)
        self._detail_label.configure(text=detail)
        self.update_idletasks()

    def close(self) -> None:
        self.grab_release()
        self.destroy()


class DuplicateIdentityDialog(ctk.CTkToplevel):
    """Presented when enrolling a name that already exists in the
    database. Offers Overwrite / Append Images / Cancel."""

    def __init__(self, master, person_name: str, on_choice: Callable[[Optional[str]], None]):
        super().__init__(master)
        self.title("Identity Already Exists")
        self.geometry("440x220")
        self.resizable(False, False)
        self.configure(fg_color=theme.BG_SECONDARY)
        self.transient(master)
        self.grab_set()
        self._on_choice = on_choice
        self._result: Optional[str] = None

        ctk.CTkLabel(
            self,
            text=f"'{person_name}' is already enrolled.",
            font=theme.FONT_HEADING,
            text_color=theme.TEXT_PRIMARY,
            wraplength=380,
        ).pack(pady=(24, 4), padx=20)

        ctk.CTkLabel(
            self,
            text="Choose how to proceed with the newly uploaded images.",
            font=theme.FONT_BODY,
            text_color=theme.TEXT_SECONDARY,
            wraplength=380,
        ).pack(pady=(0, 16), padx=20)

        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(pady=10)

        ctk.CTkButton(
            button_frame, text="Overwrite", width=120, fg_color=theme.DANGER, hover_color="#C0392B",
            command=lambda: self._choose("overwrite"),
        ).grid(row=0, column=0, padx=6)

        ctk.CTkButton(
            button_frame, text="Append Images", width=140, fg_color=theme.ACCENT, hover_color=theme.ACCENT_HOVER,
            command=lambda: self._choose("append"),
        ).grid(row=0, column=1, padx=6)

        ctk.CTkButton(
            button_frame, text="Cancel", width=100, fg_color=theme.NEUTRAL, hover_color="#4A5764",
            command=lambda: self._choose(None),
        ).grid(row=0, column=2, padx=6)

        self.protocol("WM_DELETE_WINDOW", lambda: self._choose(None))

    def _choose(self, choice: Optional[str]) -> None:
        self._result = choice
        self.grab_release()
        self.destroy()
        self._on_choice(choice)


def show_info_dialog(master, title: str, message: str, success: bool = True) -> None:
    """Simple acknowledgement dialog used for success/error notifications."""
    dialog = ctk.CTkToplevel(master)
    dialog.title(title)
    dialog.geometry("380x180")
    dialog.resizable(False, False)
    dialog.configure(fg_color=theme.BG_SECONDARY)
    dialog.transient(master)
    dialog.grab_set()

    icon = "✅" if success else "⚠️"
    ctk.CTkLabel(dialog, text=icon, font=("Segoe UI Emoji", 32)).pack(pady=(24, 6))
    ctk.CTkLabel(
        dialog, text=message, font=theme.FONT_BODY, text_color=theme.TEXT_PRIMARY, wraplength=330, justify="center"
    ).pack(pady=(0, 16), padx=16)
    ctk.CTkButton(
        dialog, text="OK", width=100, fg_color=theme.ACCENT, hover_color=theme.ACCENT_HOVER,
        command=dialog.destroy,
    ).pack(pady=(0, 16))


def show_confirm_dialog(
    master, title: str, message: str, on_confirm: Callable[[], None], confirm_text: str = "Confirm"
) -> None:
    """Yes/No confirmation dialog used before destructive or impactful
    actions (delete, exit, etc.)."""
    dialog = ctk.CTkToplevel(master)
    dialog.title(title)
    dialog.geometry("380x180")
    dialog.resizable(False, False)
    dialog.configure(fg_color=theme.BG_SECONDARY)
    dialog.transient(master)
    dialog.grab_set()

    ctk.CTkLabel(dialog, text="⚠️", font=("Segoe UI Emoji", 30)).pack(pady=(20, 6))
    ctk.CTkLabel(
        dialog, text=message, font=theme.FONT_BODY, text_color=theme.TEXT_PRIMARY, wraplength=330, justify="center"
    ).pack(pady=(0, 16), padx=16)

    button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
    button_frame.pack(pady=(0, 16))

    def _confirm():
        dialog.destroy()
        on_confirm()

    ctk.CTkButton(
        button_frame, text=confirm_text, width=110, fg_color=theme.DANGER, hover_color="#C0392B", command=_confirm,
    ).grid(row=0, column=0, padx=6)
    ctk.CTkButton(
        button_frame, text="Cancel", width=110, fg_color=theme.NEUTRAL, hover_color="#4A5764",
        command=dialog.destroy,
    ).grid(row=0, column=1, padx=6)
