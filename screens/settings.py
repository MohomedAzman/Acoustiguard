import customtkinter as ctk
import theme
from widgets import HeaderBar, AccentButton, Card
from data.repository import SettingsRepository
from data.models import Settings
from utils.audio_devices import get_microphone_names

class SettingsScreen(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=theme.COLOR_BG)
        self.app = app
        self._built = False
        self._settings = None

    def build(self):
        HeaderBar(self, right_label="Back",
                   right_command=lambda: self.app.show_screen("dashboard")).pack(fill="x")

        body = ctk.CTkScrollableFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(body, text="Settings", font=theme.font_title(),
                     text_color=theme.COLOR_TEXT_PRIMARY).pack(anchor="w", pady=(0, 16))

        # Microphone settings
        self._section_label(body, "Microphone Settings")
        mic_card = Card(body)
        mic_card.pack(fill="x", pady=(0, 16))
        mic_inner = ctk.CTkFrame(mic_card, fg_color="transparent")
        mic_inner.pack(fill="x", padx=16, pady=14)

        ctk.CTkLabel(mic_inner, text="Select Microphone", font=theme.font_body(),
                     text_color=theme.COLOR_TEXT_SECONDARY).pack(anchor="w")
        
        mic_names = get_microphone_names()
        
        self.mic_dropdown = ctk.CTkOptionMenu(
            mic_inner, values=mic_names,
        )
        self.mic_dropdown.pack(fill="x", pady=(6, 14))

        ctk.CTkLabel(mic_inner, text="Sensitivity", font=theme.font_body(),
                     text_color=theme.COLOR_TEXT_SECONDARY).pack(anchor="w")
        sens_row = ctk.CTkFrame(mic_inner, fg_color="transparent")
        sens_row.pack(fill="x")
        self.sensitivity_slider = ctk.CTkSlider(sens_row, from_=0, to=100,
                                                 command=self._on_sensitivity_change)
        self.sensitivity_slider.pack(side="left", fill="x", expand=True)
        self.sensitivity_pct = ctk.CTkLabel(sens_row, text="60%", font=theme.font_body(),
                                             text_color=theme.COLOR_TEXT_SECONDARY, width=44)
        self.sensitivity_pct.pack(side="left", padx=(8, 0))

        # Notification settings
        self._section_label(body, "Notification Settings")
        notif_card = Card(body)
        notif_card.pack(fill="x", pady=(0, 16))
        notif_inner = ctk.CTkFrame(notif_card, fg_color="transparent")
        notif_inner.pack(fill="x", padx=16, pady=14)

        self.alerts_switch = self._switch_row(notif_inner, "Enable Alerts")
        self.sound_switch = self._switch_row(notif_inner, "Alert Sound")

        # Scan history settings
        self._section_label(body, "Scan History Settings")
        history_card = Card(body)
        history_card.pack(fill="x", pady=(0, 24))
        history_inner = ctk.CTkFrame(history_card, fg_color="transparent")
        history_inner.pack(fill="x", padx=16, pady=14)

        ctk.CTkLabel(history_inner, text="Retain History", font=theme.font_body(),
                     text_color=theme.COLOR_TEXT_SECONDARY).pack(anchor="w")
        self.retain_dropdown = ctk.CTkOptionMenu(
            history_inner, values=["7", "30", "90", "999"],
        )
        self.retain_dropdown.pack(fill="x", pady=(6, 0))

        AccentButton(body, text="SAVE SETTINGS", command=self._save).pack(fill="x", pady=(0, 20))

        self._built = True

    def _section_label(self, parent, text):
        ctk.CTkLabel(parent, text=text, font=theme.font_body_bold(),
                     text_color=theme.COLOR_TEXT_PRIMARY).pack(anchor="w", pady=(0, 8))

    def _switch_row(self, parent, label_text):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=6)
        ctk.CTkLabel(row, text=label_text, font=theme.font_body(),
                     text_color=theme.COLOR_TEXT_PRIMARY).pack(side="left")
        switch = ctk.CTkSwitch(row, text="")
        switch.pack(side="right")
        return switch

    def _on_sensitivity_change(self, value):
        self.sensitivity_pct.configure(text=f"{int(value)}%")

    def on_show(self):
        if not self._built:
            self.build()
            
        self._settings = SettingsRepository.get_settings()
        
        # Load Mic dropdown
        if self._settings.microphone_device in self.mic_dropdown._values:
            self.mic_dropdown.set(self._settings.microphone_device)
        else:
            if self.mic_dropdown._values:
                self.mic_dropdown.set(self.mic_dropdown._values[0])
                
        # Load Sensitivity
        self.sensitivity_slider.set(self._settings.microphone_sensitivity)
        self.sensitivity_pct.configure(text=f"{int(self._settings.microphone_sensitivity)}%")
        
        # Load Switches
        if self._settings.enable_alerts:
            self.alerts_switch.select()
        else:
            self.alerts_switch.deselect()
            
        if self._settings.enable_alert_sound:
            self.sound_switch.select()
        else:
            self.sound_switch.deselect()
            
        # Load retention
        self.retain_dropdown.set(str(self._settings.history_retention_days))

    def _save(self):
        if not self._settings:
            return
            
        self._settings.microphone_device = self.mic_dropdown.get()
        self._settings.microphone_sensitivity = int(self.sensitivity_slider.get())
        self._settings.enable_alerts = bool(self.alerts_switch.get())
        self._settings.enable_alert_sound = bool(self.sound_switch.get())
        self._settings.history_retention_days = int(self.retain_dropdown.get())
        
        SettingsRepository.save_settings(self._settings)
        self.app.show_screen("dashboard")
