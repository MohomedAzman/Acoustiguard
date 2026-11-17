import customtkinter as ctk

# ---- Color Palette - Modern Dark Theme with Accents ----
# Primary brand colors
COLOR_BG = "#F5F6FA"              
COLOR_BG_SECONDARY = "#DCE1F6"    
COLOR_CARD = "#FFFFFF"            # Card background
COLOR_CARD_HOVER = "#E3E1E1"      # Card hover state
COLOR_HEADER = "#1F2937"          # Header bar
COLOR_HEADER_TEXT = "#FFFFFF"

# Accent colors
COLOR_PRIMARY = "#2563EB"         # Bright blue
COLOR_PRIMARY_HOVER = "#1D4ED8"
COLOR_PRIMARY_DIM = "#012894"     # For pressed states
COLOR_PRIMARY_GLOW = "#527EF8"  # Glow effect

COLOR_ACCENT = "#A371F7"          # Purple accent
COLOR_ACCENT_HOVER = "#D2A8FF"

# Semantic colors
COLOR_SUCCESS = "#3FB950"         # Green
COLOR_SUCCESS_DIM = "#16A34A"
COLOR_SUCCESS_GLOW = "#3FB95040"

COLOR_WARNING = "#D29922"         # Amber
COLOR_WARNING_DIM = "#9E6A03"
COLOR_WARNING_GLOW = "#D2992240"

COLOR_DANGER = "#F85149"          # Red
COLOR_DANGER_DIM = "#DA3633"
COLOR_DANGER_GLOW = "#F8514940"

COLOR_INFO = "#58A6FF"            # Info blue

# Text colors
COLOR_TEXT_PRIMARY = "#111827"
COLOR_TEXT_SECONDARY = "#313236"
COLOR_TEXT_MUTED = "#48494B"
COLOR_TEXT_ON_PRIMARY = "#111827"

# Border colors
COLOR_BORDER = "#E5E7EB"
COLOR_BORDER_LIGHT = "#C5C8CD"
COLOR_BORDER_FOCUS = "#E3ECFF"

# Risk level colors with glow
RISK_COLORS = {
    "Low": {"bg": COLOR_SUCCESS, "glow": COLOR_SUCCESS_GLOW, "text": COLOR_TEXT_ON_PRIMARY},
    "Medium": {"bg": COLOR_WARNING, "glow": COLOR_WARNING_GLOW, "text": COLOR_TEXT_ON_PRIMARY},
    "High": {"bg": COLOR_DANGER, "glow": COLOR_DANGER_GLOW, "text": COLOR_TEXT_ON_PRIMARY},
    "Critical": {"bg": "#FF3366", "glow": "#FF336640", "text": COLOR_TEXT_ON_PRIMARY},
}

# Gradient definitions (for future use)
GRADIENT_PRIMARY = ("#58A6FF", "#A371F7")
GRADIENT_SUCCESS = ("#3FB950", "#2EA043")
GRADIENT_DANGER = ("#F85149", "#DA3633")

# ---- Fonts ----
def font_display():
    return ctk.CTkFont(family="Segoe UI", size=28, weight="bold")

def font_title():
    return ctk.CTkFont(family="Segoe UI", size=22, weight="bold")

def font_header():
    return ctk.CTkFont(family="Segoe UI", size=18, weight="bold")

def font_subheader():
    return ctk.CTkFont(family="Segoe UI", size=15, weight="bold")

def font_body():
    return ctk.CTkFont(family="Segoe UI", size=13)

def font_body_bold():
    return ctk.CTkFont(family="Segoe UI", size=13, weight="bold")

def font_small():
    return ctk.CTkFont(family="Segoe UI", size=11)

def font_small_bold():
    return ctk.CTkFont(family="Segoe UI", size=11, weight="bold")

def font_button():
    return ctk.CTkFont(family="Segoe UI", size=13, weight="bold")

def font_button_large():
    return ctk.CTkFont(family="Segoe UI", size=15, weight="bold")

def font_mono():
    return ctk.CTkFont(family="Consolas", size=12)

# ---- Sizing ----
WINDOW_SIZE = "480x800"
MIN_WINDOW_SIZE = (400, 650)
CORNER_RADIUS_SM = 8
CORNER_RADIUS = 12
CORNER_RADIUS_LG = 16
CORNER_RADIUS_XL = 24

# Spacing
SPACING_XS = 4
SPACING_SM = 8
SPACING_MD = 16
SPACING_LG = 24
SPACING_XL = 32

# Animation durations (ms)
ANIM_FAST = 150
ANIM_NORMAL = 250
ANIM_SLOW = 350

# Shadow/Depth
SHADOW_SM = "0 1px 3px rgba(0,0,0,0.3)"
SHADOW_MD = "0 4px 12px rgba(0,0,0,0.4)"
SHADOW_LG = "0 8px 24px rgba(0,0,0,0.5)"
