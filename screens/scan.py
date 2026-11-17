import customtkinter as ctk
import threading
import theme
from widgets import HeaderBar, AccentButton, Card
from utils.audio_devices import check_microphone_available
from services.scan_service import ScanService, ScanServiceError


class ScanScreen(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=theme.COLOR_BG)
        self.app = app
        self._built = False
        self._scanning = False
        self._scan_service = ScanService()
        self._scan_thread = None

    def build(self):
        HeaderBar(self, right_label="Back",
                   right_command=lambda: self._go_back()).pack(fill="x")

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(body, text="Acoustic Environment Scan", font=theme.font_title(),
                     text_color=theme.COLOR_TEXT_PRIMARY).pack(anchor="w", pady=(0, 16))

        card = Card(body)
        card.pack(fill="x", pady=(0, 16))
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=16, pady=16)

        self.mic_status_label = ctk.CTkLabel(
            inner, text="Microphone: Checking...", font=theme.font_body_bold(),
            text_color=theme.COLOR_TEXT_SECONDARY,
        )
        self.mic_status_label.pack(anchor="w")

        self.capture_label = ctk.CTkLabel(
            inner, text="Press start to begin scanning", font=theme.font_body(),
            text_color=theme.COLOR_TEXT_SECONDARY,
        )
        self.capture_label.pack(anchor="w", pady=(8, 8))

        self.progress = ctk.CTkProgressBar(inner, height=14)
        self.progress.set(0)
        self.progress.pack(fill="x", pady=(0, 4))

        self.progress_pct_label = ctk.CTkLabel(
            inner, text="0%", font=theme.font_small(), text_color=theme.COLOR_TEXT_SECONDARY,
        )
        self.progress_pct_label.pack(anchor="e")

        # Live readouts
        readout_card = Card(body)
        readout_card.pack(fill="x", pady=(0, 16))
        readout_inner = ctk.CTkFrame(readout_card, fg_color="transparent")
        readout_inner.pack(fill="x", padx=16, pady=14)

        self.noise_row = self._make_readout_row(readout_inner, "Ambient Noise Level:", "---")
        self.clarity_row = self._make_readout_row(readout_inner, "Acoustic Clarity:", "---")
        self.exposure_row = self._make_readout_row(readout_inner, "Keyboard Exposure:", "---")

        # Info label
        self.info_label = ctk.CTkLabel(
            body, text="Please remain in your normal working environment during the scan.",
            font=theme.font_small(), text_color=theme.COLOR_TEXT_SECONDARY, wraplength=400,
        )
        self.info_label.pack(pady=(0, 16))

        self.scan_button = AccentButton(
            body, text="START NEW SCAN", command=self.start_scan,
        )
        self.scan_button.pack(fill="x")

        self._built = True

    def _make_readout_row(self, parent, label_text, value_text):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=4)
        ctk.CTkLabel(row, text=label_text, font=theme.font_body(),
                     text_color=theme.COLOR_TEXT_SECONDARY).pack(side="left")
        value_label = ctk.CTkLabel(row, text=value_text, font=theme.font_body_bold(),
                                    text_color=theme.COLOR_TEXT_PRIMARY)
        value_label.pack(side="right")
        return value_label

    def on_show(self):
        if not self._built:
            self.build()
        self._reset()
        self._check_microphone()

    def _go_back(self):
        if not self._scanning:
            self.app.show_screen("dashboard")

    def _check_microphone(self):
        try:
            available, message = check_microphone_available()
            if available:
                self.mic_status_label.configure(text="Microphone: Ready", text_color=theme.COLOR_SUCCESS)
                self.scan_button.configure(state="normal")
            else:
                self.mic_status_label.configure(text="Microphone: Unavailable", text_color=theme.COLOR_DANGER)
                self.scan_button.configure(state="disabled")
                self.capture_label.configure(text=message)
        except Exception:
            self.mic_status_label.configure(text="Microphone: Error", text_color=theme.COLOR_DANGER)
            self.scan_button.configure(state="disabled")

    def _reset(self):
        self._scanning = False
        self._scan_thread = None
        self.progress.set(0)
        self.progress_pct_label.configure(text="0%")
        self.capture_label.configure(text="Press start to begin scanning")
        self.noise_row.configure(text="---")
        self.clarity_row.configure(text="---")
        self.exposure_row.configure(text="---")
        self.scan_button.configure(text="START NEW SCAN", state="normal")
        self.info_label.configure(text="Please remain in your normal working environment during the scan.")

    def start_scan(self):
        if self._scanning:
            return
        
        self._scanning = True
        self.scan_button.configure(text="SCANNING...", state="disabled")
        self.mic_status_label.configure(text="Microphone: ACTIVE", text_color=theme.COLOR_PRIMARY)
        self.info_label.configure(text="Scanning in progress... Please remain in your normal working environment.")
        
        # Run scan in background thread to keep UI responsive
        self._scan_thread = threading.Thread(target=self._run_scan_worker, daemon=True)
        self._scan_thread.start()
        
        # Poll for completion
        self._check_scan_completion()
    
    def _run_scan_worker(self):
        """Background worker for the full scan pipeline."""
        try:
            self._scan_result = self._scan_service.run_scan(
                duration=10.0,
                progress_callback=self._on_progress,
                save_to_db=True
            )
            self._scan_error = None
        except ScanServiceError as e:
            self._scan_result = None
            self._scan_error = str(e)
        except Exception as e:
            self._scan_result = None
            self._scan_error = f"Unexpected error: {str(e)}"
    
    def _on_progress(self, percent, message):
        """Called from background thread - schedule UI update on main thread."""
        self.after(0, lambda p=percent, m=message: self._update_ui(p, m))
    
    def _update_ui(self, percent, message):
        """Update progress UI (main thread only)."""
        try:
            self.progress.set(percent / 100.0)
            self.progress_pct_label.configure(text=f"{int(percent)}%")
            self.capture_label.configure(text=message)
            
            # Update live readouts based on scan stage
            if percent < 30:
                self.noise_row.configure(text="Detecting...")
                self.clarity_row.configure(text="...")
                self.exposure_row.configure(text="...")
            elif percent < 60:
                self.noise_row.configure(text="Measuring...")
                self.clarity_row.configure(text="Analyzing...")
                self.exposure_row.configure(text="...")
            elif percent < 80:
                self.noise_row.configure(text="Measured")
                self.clarity_row.configure(text="Processing...")
                self.exposure_row.configure(text="Calculating...")
            elif percent < 100:
                self.noise_row.configure(text="Measured")
                self.clarity_row.configure(text="Assessed")
                self.exposure_row.configure(text="Scoring...")
        except Exception:
            pass  # Widget may have been destroyed
    
    def _check_scan_completion(self):
        """Poll for scan thread completion."""
        if self._scan_thread and self._scan_thread.is_alive():
            self.after(200, self._check_scan_completion)
            return
        
        # Scan complete
        self._scanning = False
        
        if hasattr(self, '_scan_error') and self._scan_error:
            self._handle_error(self._scan_error)
            return
        
        if hasattr(self, '_scan_result') and self._scan_result:
            result = self._scan_result
            
            # Update live readouts with final values
            rms = result.acoustic_features.rms_energy if result.acoustic_features else 0
            noise_level = "High" if rms > 0.3 else "Medium" if rms > 0.1 else "Low"
            self.noise_row.configure(text=noise_level)
            self.clarity_row.configure(text="Assessed")
            self.exposure_row.configure(text=result.risk_level)
            
            # Store result in app state
            self.app.app_state["current_risk_level"] = result.risk_level
            self.app.app_state["current_risk_score"] = result.risk_score
            self.app.app_state["last_scan_result"] = result
            self.app.app_state["last_scan_date"] = result.scan_date
            self.app.app_state["last_scan_time"] = result.scan_time
            self.app.app_state["last_risk_level"] = result.risk_level
            
            self.mic_status_label.configure(text="Microphone: Complete", text_color=theme.COLOR_SUCCESS)
            self.capture_label.configure(text="Scan complete - Displaying results...")
            
            # Navigate to risk result after brief delay
            self.after(800, lambda: self.app.show_screen("risk_result"))
        else:
            self._handle_error("Scan completed but no result returned")
    
    def _handle_error(self, error_message):
        """Handle scan error."""
        self.mic_status_label.configure(text="Microphone: Error", text_color=theme.COLOR_DANGER)
        self.capture_label.configure(text=f"Error: {error_message}")
        self.scan_button.configure(text="RETRY SCAN", state="normal")
        self.noise_row.configure(text="---")
        self.clarity_row.configure(text="---")
        self.exposure_row.configure(text="---")
