import customtkinter as ctk
import theme
from widgets import HeaderBar, AccentButton, SecondaryButton, Card, RiskBadge


class RiskResultScreen(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=theme.COLOR_BG)
        self.app = app
        self._built = False

    def build(self):
        HeaderBar(self, right_label="Back",
                   right_command=lambda: self.app.show_screen("dashboard")).pack(fill="x")

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(body, text="Risk Assessment Result", font=theme.font_title(),
                     text_color=theme.COLOR_TEXT_PRIMARY).pack(anchor="w", pady=(0, 16))

        self.risk_card = Card(body)
        self.risk_card.pack(fill="x", pady=(0, 16))
        risk_inner = ctk.CTkFrame(self.risk_card, fg_color="transparent")
        risk_inner.pack(fill="x", padx=16, pady=16)

        ctk.CTkLabel(risk_inner, text="Risk Level", font=theme.font_body(),
                     text_color=theme.COLOR_TEXT_SECONDARY).pack(anchor="w")

        self.badge_holder = ctk.CTkFrame(risk_inner, fg_color="transparent")
        self.badge_holder.pack(anchor="w", pady=(6, 10))

        self.score_label = ctk.CTkLabel(
            risk_inner, text="Risk Score: —/100", font=theme.font_body_bold(),
            text_color=theme.COLOR_TEXT_PRIMARY,
        )
        self.score_label.pack(anchor="w")

        # Recommendations card
        rec_card = Card(body)
        rec_card.pack(fill="x", pady=(0, 24))
        rec_inner = ctk.CTkFrame(rec_card, fg_color="transparent")
        rec_inner.pack(fill="x", padx=16, pady=14)

        ctk.CTkLabel(rec_inner, text="Recommendations:", font=theme.font_body_bold(),
                     text_color=theme.COLOR_TEXT_PRIMARY).pack(anchor="w", pady=(0, 6))

        self.rec_list_frame = ctk.CTkFrame(rec_inner, fg_color="transparent")
        self.rec_list_frame.pack(fill="x")

        AccentButton(
            body, text="ENABLE MASKING",
            command=lambda: self.app.show_screen("masking"),
        ).pack(fill="x", pady=(0, 12))

        SecondaryButton(
            body, text="SAVE RESULT",
            command=self._save_result,
        ).pack(fill="x")

        self._built = True

    def on_show(self):
        if not self._built:
            self.build()
        scan_result = self.app.app_state.get("last_scan_result")
        if not scan_result:
            return

        risk = scan_result.risk_level
        score = scan_result.risk_score

        for w in self.badge_holder.winfo_children():
            w.destroy()
        RiskBadge(self.badge_holder, risk_level=risk).pack(anchor="w")

        self.score_label.configure(text=f"Risk Score: {score}/100")

        for w in self.rec_list_frame.winfo_children():
            w.destroy()
            
        for rec in scan_result.recommendations:
            # rec is a Recommendation object
            ctk.CTkLabel(
                self.rec_list_frame, text=f"•  {rec.recommendation_text}", font=theme.font_body(),
                text_color=theme.COLOR_TEXT_PRIMARY, anchor="w", justify="left",
                wraplength=350,
            ).pack(fill="x", pady=2)

    def _save_result(self):
        """ScanService already saves to the DB automatically. We just return to dashboard."""
        self.app.show_screen("dashboard")
