import os

import customtkinter as ctk
import theme
from utils.resource_path import resource_path

# Brand logo asset path (resolved for dev and PyInstaller environments).
LOGO_PATH = resource_path("assets/AcoustiGuard logo.png")


class HeaderBar(ctk.CTkFrame):

    def __init__(self, master, right_label="Back", right_command=None, **kwargs):
        super().__init__(
            master,
            fg_color=theme.COLOR_HEADER,
            corner_radius=0,
            height=68,
            border_width=0,
            **kwargs
        )
        self.pack_propagate(False)

        # Try to load the primary logo image. CTkImage keeps a reference to
        # the underlying PIL image internally, so it is not garbage-collected
        # while the label exists. self.logo_image must stay referenced.
        self.logo_image = None
        if os.path.isfile(LOGO_PATH):
            try:
                from PIL import Image
                self.logo_image = ctk.CTkImage(
                    Image.open(LOGO_PATH),
                    size=(150, 40),
                )
            except Exception:
                # Missing or invalid image file: fall back to the text title.
                self.logo_image = None

        # Left section: logo image, or accent bar + text title as fallback.
        if self.logo_image is not None:
            logo_label = ctk.CTkLabel(
                self,
                image=self.logo_image,
                text="",
                text_color=theme.COLOR_HEADER_TEXT,
            )
            logo_label.pack(side="left", padx=(16, 12), pady=(14, 0))
        else:
            # Accent bar + text title fallback (only reached when the logo
            # could not be loaded). Everything here must stay inside this
            # else block so 'accent' is never referenced when unused.
            accent = ctk.CTkFrame(
                self,
            fg_color=theme.COLOR_PRIMARY,
                width=4,
                height=36,
                corner_radius=2,
            )
            accent.pack(side="left", padx=(16, 12), pady=(16, 0))

            title = ctk.CTkLabel(
                self,
                text="AcoustiGuard",
                text_color=theme.COLOR_HEADER_TEXT,
                font=theme.font_header(),
                anchor="w",
            )
            title.pack(side="left", padx=4)

        if right_label:
            btn = ctk.CTkButton(
                self,
                text=right_label,
                width=88,
                height=36,
                fg_color="transparent",
                hover_color=theme.COLOR_CARD_HOVER,
                text_color=theme.COLOR_HEADER_TEXT,
                font=theme.font_body_bold(),
                corner_radius=theme.CORNER_RADIUS_SM,
                border_width=1,
                border_color=theme.COLOR_BORDER,
                command=right_command,
            )
            btn.pack(side="right", padx=(0, 16))


class AccentButton(ctk.CTkButton):

    def __init__(self, master, text, command=None, fg_color=None, hover_color=None, **kwargs):
        super().__init__(
            master,
            text=text,
            command=command,
            fg_color=fg_color or theme.COLOR_PRIMARY,
            hover_color=hover_color or theme.COLOR_PRIMARY_HOVER,
            text_color=theme.COLOR_TEXT_ON_PRIMARY,
            font=theme.font_button(),
            corner_radius=theme.CORNER_RADIUS,
            height=50,
            border_width=0,
            **kwargs
        )


class GradientButton(ctk.CTkButton):

    def __init__(self, master, text, command=None, **kwargs):
        super().__init__(
            master,
            text=text,
            command=command,
            fg_color=theme.COLOR_ACCENT,
            hover_color=theme.COLOR_ACCENT_HOVER,
            text_color=theme.COLOR_TEXT_ON_PRIMARY,
            font=theme.font_button(),
            corner_radius=theme.CORNER_RADIUS,
            height=50,
            border_width=0,
            **kwargs
        )


class SecondaryButton(ctk.CTkButton):
    """Outlined button, e.g. 'VIEW SCAN HISTORY'."""

    def __init__(self, master, text, command=None, **kwargs):
        super().__init__(
            master,
            text=text,
            command=command,
            fg_color="transparent",
            border_width=1,
            border_color=theme.COLOR_BORDER,
            hover_color=theme.COLOR_CARD_HOVER,
            text_color=theme.COLOR_TEXT_PRIMARY,
            font=theme.font_button(),
            corner_radius=theme.CORNER_RADIUS,
            height=50,
            **kwargs
        )


class DangerButton(ctk.CTkButton):
    """Red danger button, e.g. 'STOP MASKING' or 'CLEAR HISTORY'."""

    def __init__(self, master, text, command=None, **kwargs):
        super().__init__(
            master,
            text=text,
            command=command,
            fg_color=theme.COLOR_DANGER,
            hover_color="#FB6F6A",
            text_color=theme.COLOR_TEXT_ON_PRIMARY,
            font=theme.font_button(),
            corner_radius=theme.CORNER_RADIUS,
            height=50,
            border_width=0,
            **kwargs
        )


class Card(ctk.CTkFrame):
    """Modern rounded card container used to group content."""

    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color=theme.COLOR_CARD,
            corner_radius=theme.CORNER_RADIUS_LG,
            border_width=1,
            border_color=theme.COLOR_BORDER,
            **kwargs
        )


class CardHollow(ctk.CTkFrame):
    """Card with transparent background and border, e.g. for masks/labels."""

    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color="transparent",
            corner_radius=theme.CORNER_RADIUS,
            border_width=1,
            border_color=theme.COLOR_BORDER,
            **kwargs
        )


class RiskBadge(ctk.CTkFrame):
    """Glowing pill showing a risk level (Low/Medium/High/Critical)."""

    def __init__(self, master, risk_level="Medium", **kwargs):
        config = theme.RISK_COLORS.get(risk_level, theme.RISK_COLORS["Medium"])
        super().__init__(
            master,
            fg_color=config["bg"],
            corner_radius=20,
            height=36,
            **kwargs
        )
        self.pack_propagate(False)
        label = ctk.CTkLabel(
            self,
            text=risk_level.upper(),
            text_color=config["text"],
            font=theme.font_body_bold(),
        )
        label.pack(padx=14, pady=6)


class ProgressBar(ctk.CTkFrame):
    """Custom animated progress bar."""

    def __init__(self, master, progress=0, total=100, height=8, **kwargs):
        super().__init__(
            master,
            fg_color=theme.COLOR_BG_SECONDARY,
            corner_radius=4,
            height=height,
            **kwargs
        )
        self.pack_propagate(False)
        self.progress = progress
        self.total = total
        self._create_widgets()

    def _create_widgets(self):
        self.bg = ctk.CTkFrame(self, fg_color="transparent", height=8)
        self.bg.pack(fill="x", padx=0, pady=0)
        
        self.fg = ctk.CTkFrame(
            self.bg,
            fg_color=theme.COLOR_PRIMARY,
            height=8,
            corner_radius=4,
        )
        self.fg.pack(fill="x", padx=0, pady=0)
        self.fg.pack_propagate(False)
        self.update_width()

    def update_width(self):
        percentage = max(0, min(100, (self.progress / self.total) * 100))
        width_px = int(self.winfo_width() * percentage / 100) if self.winfo_width() else 0
        self.fg.configure(width=max(width_px, 2))

    def set_progress(self, value):
        self.progress = value
        self.update_width()


class IconLabel(ctk.CTkLabel):
    """Label with an icon/emoji prefix."""

    def __init__(self, master, text, icon="✨", text_color=theme.COLOR_TEXT_PRIMARY, **kwargs):
        super().__init__(
            master,
            text=f"{icon}  {text}",
            text_color=text_color,
            font=theme.font_body(),
            anchor="w",
            **kwargs
        )


class Badge(ctk.CTkFrame):
    """Small colored badge for status indicators."""

    def __init__(self, master, text, color=theme.COLOR_PRIMARY, **kwargs):
        super().__init__(
            master,
            fg_color=color + "20",
            corner_radius=12,
            **kwargs
        )
        self.pack_propagate(False)
        label = ctk.CTkLabel(
            self,
            text=text,
            text_color=color,
            font=theme.font_small_bold(),
        )
        label.pack(padx=10, pady=4)

