import customtkinter as ctk
import theme

from screens.dashboard import DashboardScreen
from screens.scan import ScanScreen
from screens.risk_result import RiskResultScreen
from screens.masking import MaskingScreen
from screens.history import HistoryScreen
from screens.settings import SettingsScreen


class AcoustiGuardApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("AcoustiGuard")
        self.geometry(theme.WINDOW_SIZE)
        self.minsize(400, 650)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.configure(fg_color=theme.COLOR_BG)
        self.minsize(*theme.MIN_WINDOW_SIZE)

        # Initialize SQLite Database
        from data.database import init_database
        init_database()

        import getpass
        real_name = getpass.getuser().capitalize()

        # Shared in-memory state
        self.app_state = {
            "user_name": real_name,
            "last_scan_result": None,
        }

        # Container that all screens stack into
        container = ctk.CTkFrame(self, fg_color=theme.COLOR_BG)
        container.pack(fill="both", expand=True)
        self.container = container

        self.screens = {}
        self._register_screen("dashboard", DashboardScreen)
        self._register_screen("scan", ScanScreen)
        self._register_screen("risk_result", RiskResultScreen)
        self._register_screen("masking", MaskingScreen)
        self._register_screen("history", HistoryScreen)
        self._register_screen("settings", SettingsScreen)

        self.show_screen("dashboard")

    def _register_screen(self, name, screen_class):
        frame = screen_class(self.container, app=self)
        frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.screens[name] = frame

    def show_screen(self, name):
        """Raise the requested screen and let it refresh itself from app.app_state."""
        screen = self.screens[name]
        if hasattr(screen, "on_show"):
            screen.on_show()
        screen.tkraise()


