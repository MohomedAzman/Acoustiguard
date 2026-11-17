import customtkinter as ctk
import theme
from widgets import HeaderBar, SecondaryButton, Card


class HistoryScreen(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=theme.COLOR_BG)
        self.app = app
        self._built = False

    def build(self):
        HeaderBar(self, right_label="Back",
                   right_command=lambda: self.app.show_screen("dashboard")).pack(fill="x")

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(body, text="Scan History", font=theme.font_title(),
                     text_color=theme.COLOR_TEXT_PRIMARY).pack(anchor="w", pady=(0, 16))

        # Header row for the table
        header_card = Card(body)
        header_card.pack(fill="x")
        header_row = ctk.CTkFrame(header_card, fg_color="transparent")
        header_row.pack(fill="x", padx=16, pady=(10, 6))
        ctk.CTkLabel(header_row, text="Date", font=theme.font_body_bold(), width=90,
                     text_color=theme.COLOR_TEXT_SECONDARY, anchor="w").pack(side="left")
        ctk.CTkLabel(header_row, text="Time", font=theme.font_body_bold(), width=60,
                     text_color=theme.COLOR_TEXT_SECONDARY, anchor="w").pack(side="left")
        ctk.CTkLabel(header_row, text="Risk", font=theme.font_body_bold(),
                     text_color=theme.COLOR_TEXT_SECONDARY, anchor="w").pack(side="left")

        self.list_frame = ctk.CTkScrollableFrame(header_card, fg_color="transparent", height=340)
        self.list_frame.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        button_row = ctk.CTkFrame(body, fg_color="transparent")
        button_row.pack(fill="x", pady=(16, 0))

        SecondaryButton(body, text="VIEW DETAILS").pack(fill="x", pady=(0, 12))
        SecondaryButton(
            body, text="CLEAR HISTORY",
            command=self._clear_history,
        ).pack(fill="x")

        self._built = True

    def on_show(self):
        if not self._built:
            self.build()
        self._refresh_list()

    def _refresh_list(self):
        for w in self.list_frame.winfo_children():
            w.destroy()

        from data.repository import ScanRepository
        history = ScanRepository.get_all_scans(limit=50)
        
        if not history:
            ctk.CTkLabel(self.list_frame, text="No scans recorded yet.",
                         font=theme.font_body(), text_color=theme.COLOR_TEXT_SECONDARY).pack(pady=20)
            return

        for entry in history:
            row = ctk.CTkFrame(self.list_frame, fg_color="transparent")
            row.pack(fill="x", pady=4)
            ctk.CTkLabel(row, text=entry["date"], font=theme.font_body(), width=90,
                         text_color=theme.COLOR_TEXT_PRIMARY, anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=entry["time"], font=theme.font_body(), width=60,
                         text_color=theme.COLOR_TEXT_PRIMARY, anchor="w").pack(side="left")
            risk_color = theme.RISK_COLORS.get(entry["risk"], theme.RISK_COLORS["Medium"])["text"]
            ctk.CTkLabel(row, text=entry["risk"], font=theme.font_body_bold(),
                         text_color=risk_color, anchor="w").pack(side="left")

    def _clear_history(self):
        from data.repository import ScanRepository
        ScanRepository.clear_all_scans()
        self._refresh_list()
