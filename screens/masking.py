import customtkinter as ctk
import theme
from widgets import HeaderBar, Card
from core.masking_engine import MaskingEngine


class MaskingScreen(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=theme.COLOR_BG)
        self.app = app
        self._built = False
        self._seconds = 0
        self._running = False
        self._engine = MaskingEngine()

    def build(self):
        HeaderBar(self, right_label="Back",
                   right_command=self._stop_and_back).pack(fill="x")

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(body, text="Acoustic Masking", font=theme.font_title(),
                     text_color=theme.COLOR_TEXT_PRIMARY).pack(anchor="w", pady=(0, 16))

        card = Card(body)
        card.pack(fill="x", pady=(0, 24))
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=16, pady=16)

        self.status_label = ctk.CTkLabel(
            inner, text="Status: Active", font=theme.font_body_bold(),
            text_color=theme.COLOR_SUCCESS,
        )
        self.status_label.pack(anchor="w")

        ctk.CTkLabel(inner, text="Fake Keystroke Sound", font=theme.font_subheader(),
                     text_color=theme.COLOR_PRIMARY).pack(anchor="w", pady=(4, 2))
        ctk.CTkLabel(inner, text="Looping at 44.1kHz  (66.27 seconds)", font=theme.font_small(),
                     text_color=theme.COLOR_TEXT_MUTED).pack(anchor="w", pady=(0, 12))
        ctk.CTkLabel(inner, text="Synthetic Keystrokes & Noise", font=theme.font_body(),
                     text_color=theme.COLOR_TEXT_PRIMARY).pack(anchor="w", pady=(10, 0))
        ctk.CTkLabel(inner, text="Playing through speakers", font=theme.font_body(),
                     text_color=theme.COLOR_TEXT_SECONDARY).pack(anchor="w")

        ctk.CTkLabel(inner, text="Volume Control:", font=theme.font_body_bold(),
                     text_color=theme.COLOR_TEXT_PRIMARY).pack(anchor="w", pady=(20, 6))

        vol_row = ctk.CTkFrame(inner, fg_color="transparent")
        vol_row.pack(fill="x")
        self.volume_slider = ctk.CTkSlider(vol_row, from_=0, to=100, command=self._on_volume_change)
        
        # Read from settings DB if available, mostly hardcode 65 for now since App Settings isnt wired fully yet
        from data.repository import SettingsRepository
        default_vol = int(SettingsRepository.get_setting("masking_default_volume", "65"))
        
        self.volume_slider.set(default_vol)
        self.volume_slider.pack(side="left", fill="x", expand=True)
        self.volume_pct_label = ctk.CTkLabel(vol_row, text=f"{default_vol}%", font=theme.font_body(),
                                              text_color=theme.COLOR_TEXT_SECONDARY, width=44)
        self.volume_pct_label.pack(side="left", padx=(8, 0))

        self.duration_label = ctk.CTkLabel(
            inner, text="Masking Duration: 00:00:00", font=theme.font_body_bold(),
            text_color=theme.COLOR_TEXT_PRIMARY,
        )
        self.duration_label.pack(anchor="w", pady=(20, 0))

        self.stop_button = ctk.CTkButton(
            body, text="STOP MASKING",
            fg_color=theme.COLOR_DANGER, hover_color=theme.COLOR_DANGER_DIM,
            text_color="white", font=theme.font_button(),
            corner_radius=theme.CORNER_RADIUS, height=44,
            command=self._toggle,
        )
        self.stop_button.pack(fill="x")

        self._built = True

    def _on_volume_change(self, value):
        self.volume_pct_label.configure(text=f"{int(value)}%")
        self._engine.set_volume(value / 100.0)

    def on_show(self):
        if not self._built:
            self.build()
        self._seconds = 0
        self._running = True
        self.status_label.configure(text="Status: Active", text_color=theme.COLOR_SUCCESS)
        self.stop_button.configure(text="STOP MASKING", fg_color=theme.COLOR_DANGER, hover_color=theme.COLOR_DANGER_DIM)
        
        self._engine.set_volume(self.volume_slider.get() / 100.0)
        self._engine.start_masking()
        
        self._tick()

    def _tick(self):
        if not self._running:
            return
        self._seconds += 1
        h, rem = divmod(self._seconds, 3600)
        m, s = divmod(rem, 60)
        self.duration_label.configure(text=f"Masking Duration: {h:02}:{m:02}:{s:02}")
        self.after(1000, self._tick)

    def _toggle(self):
        if self._running:
            self._running = False
            self._engine.stop_masking()
            self.status_label.configure(text="Status: Stopped", text_color=theme.COLOR_TEXT_SECONDARY)
            self.stop_button.configure(text="START MASKING", fg_color=theme.COLOR_PRIMARY, hover_color=theme.COLOR_PRIMARY_HOVER)
        else:
            self._running = True
            self._engine.start_masking()
            self.status_label.configure(text="Status: Active", text_color=theme.COLOR_SUCCESS)
            self.stop_button.configure(text="STOP MASKING", fg_color=theme.COLOR_DANGER, hover_color=theme.COLOR_DANGER_DIM)
            self._tick()

    def _stop_and_back(self):
        self._running = False
        self._engine.stop_masking()
        # Should we go back to risk_result or dashboard?
        # Specification flow says Risk Result -> Enable Masking -> ...
        # If we go back, dashboard is safer as the risk result is already stored.
        self.app.show_screen("dashboard")
