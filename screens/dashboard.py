import customtkinter as ctk
import theme
from widgets import HeaderBar, AccentButton, SecondaryButton, Card


class DashboardScreen(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=theme.COLOR_BG)
        self.app = app
        self._built = False

    def build(self):
        HeaderBar(self, right_label="Settings",
                   right_command=lambda: self.app.show_screen("settings")).pack(fill="x")

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=20, pady=20)

        self.welcome_label = ctk.CTkLabel(
            body, text="Welcome, User",
            font=theme.font_title(), text_color=theme.COLOR_TEXT_PRIMARY,
        )
        self.welcome_label.pack(anchor="w", pady=(0, 16))

        # System status card
        status_card = Card(body)
        status_card.pack(fill="x", pady=(0, 16))
        status_row = ctk.CTkFrame(status_card, fg_color="transparent")
        status_row.pack(fill="x", padx=16, pady=14)
        ctk.CTkLabel(status_row, text="System Status:", font=theme.font_body_bold(),
                     text_color=theme.COLOR_TEXT_PRIMARY).pack(side="left")
        ctk.CTkLabel(status_row, text="●  ACTIVE", font=theme.font_body_bold(),
                     text_color=theme.COLOR_SUCCESS).pack(side="left", padx=(8, 0))

        # Last scan card
        last_scan_card = Card(body)
        last_scan_card.pack(fill="x", pady=(0, 24))
        inner = ctk.CTkFrame(last_scan_card, fg_color="transparent")
        inner.pack(fill="x", padx=16, pady=14)

        self.last_scan_label = ctk.CTkLabel(
            inner, text="Last Scan: —", font=theme.font_body(),
            text_color=theme.COLOR_TEXT_SECONDARY, anchor="w", justify="left",
        )
        self.last_scan_label.pack(fill="x")

        self.last_risk_label = ctk.CTkLabel(
            inner, text="Last Risk Level: —", font=theme.font_body_bold(),
            text_color=theme.COLOR_TEXT_PRIMARY, anchor="w", justify="left",
        )
        self.last_risk_label.pack(fill="x", pady=(4, 0))

        # Nav buttons
        AccentButton(
            body, text="START NEW SCAN",
            command=lambda: self.app.show_screen("scan"),
        ).pack(fill="x", pady=(0, 12))

        SecondaryButton(
            body, text="VIEW SCAN HISTORY",
            command=lambda: self.app.show_screen("history"),
        ).pack(fill="x")

        self._built = True

    def on_show(self):
        if not self._built:
            self.build()
        s = self.app.app_state
        self.welcome_label.configure(text=f"Welcome, {s.get('user_name', 'User')}")
        
        from data.repository import get_last_scan
        last_scan = get_last_scan()
        if last_scan:
            self.last_scan_label.configure(
                text=f"Last Scan: {last_scan['date']}   {last_scan['time']}"
            )
            self.last_risk_label.configure(text=f"Last Risk Level: {last_scan['risk']}")
        else:
            self.last_scan_label.configure(text="Last Scan: None")
            self.last_risk_label.configure(text="Last Risk Level: —")
