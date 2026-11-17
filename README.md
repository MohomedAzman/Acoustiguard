# AcoustiGuard
### Acoustic Side-Channel Attack Risk Alerting and Protection System for Remote Workers

AcoustiGuard is a Windows desktop application designed to help remote workers identify potential acoustic side-channel risks in their working environment.

It captures ambient audio, extracts acoustic characteristics, evaluates potential exposure using a rule-based risk assessment engine, and provides recommendations to help users reduce acoustic security risks. It also includes an acoustic masking feature and SQLite-based scan history.

## Features

- **Ambient Audio Capture** — Captures microphone input using Python's `sounddevice` library.
- **Audio Preprocessing** — Validates and preprocesses captured audio, including DC offset removal, optional noise gating and normalization.
- **Acoustic Feature Extraction** — Extracts acoustic characteristics using `librosa` and NumPy.
- **Risk Assessment** — Evaluates acoustic conditions and assigns a risk score and risk level.
- **Contextual Recommendations** — Provides recommendations based on the assessed risk level and contributing acoustic factors.
- **Acoustic Masking** — Plays a bundled audio file in a continuous loop to introduce additional ambient sound.
- **Scan History** — Stores scan results and related information in a local SQLite database.
- **Settings Management** — Persists application settings locally.
- **Windows Desktop Interface** — Provides a graphical interface built with CustomTkinter.

## How It Works

AcoustiGuard follows a processing pipeline:

1. **Audio Capture:** Captures ambient microphone audio for analysis.
2. **Preprocessing:** Validates the captured signal and applies preprocessing operations.
3. **Feature Extraction:** Extracts acoustic characteristics from the processed audio.
4. **Frequency Analysis:** Examines frequency distribution and identifies dominant frequency information.
5. **Risk Assessment:** Calculates a composite risk score using the extracted acoustic information.
6. **Recommendation Generation:** Produces recommendations according to the resulting risk level.
7. **Database Storage:** Saves scan results and associated information in SQLite.

## Risk Assessment Methodology

AcoustiGuard uses a heuristic-based assessment model rather than a trained machine learning classifier.

The composite score is calculated using three primary components:

| Component | Weight |
|---|---:|
| Energy Risk | 35% |
| Frequency Risk | 40% |
| Clarity Risk | 25% |

Additional score modifiers are applied for certain acoustic conditions, and the final score is constrained to the range of 0–100.

### Risk Levels

| Risk Level | Score Range |
|---|---:|
| Low | 0–29 |
| Medium | 30–59 |
| High | 60–79 |
| Critical | 80–100 |

The application uses these levels to determine the recommendations presented to the user.

**Important:** The risk score is an indicative assessment of acoustic conditions. It is not proof that a keyboard acoustic side-channel attack is occurring, nor does it guarantee protection against such attacks.

## Acoustic Masking

The acoustic masking component provides an additional protective measure by playing a supplied audio file through the system's audio output.

- Uses the bundled `masking audio.mpeg` file.
- Supports continuous looping during playback.
- Provides volume control.
- Runs playback separately from the main interface using a background thread.

Masking is a separate application function and is not automatically activated by the scan process.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core application development |
| CustomTkinter | Desktop graphical interface |
| NumPy | Numerical and signal processing |
| SciPy | Scientific computing |
| Librosa | Acoustic feature extraction |
| SoundDevice | Audio input and output |
| SoundFile | Audio file loading |
| SQLite | Local data persistence |
| PyInstaller | Windows executable packaging |
| Inno Setup | Windows installer creation |

## Project Structure

```text
AcoustiGuard/
│
├── assets/
│   ├── AcoustiGuard logo.png
│   └── AcoustiGuard.ico
│
├── core/
│   ├── audio_capture.py
│   ├── audio_processor.py
│   ├── feature_extractor.py
│   ├── risk_engine.py
│   └── masking_engine.py
│
├── data/
│   ├── database.py
│   ├── models.py
│   └── repository.py
│
├── screens/
│   ├── dashboard_screen.py
│   ├── scan_screen.py
│   ├── risk_result_screen.py
│   ├── masking_screen.py
│   ├── history_screen.py
│   └── settings_screen.py
│
├── services/
│   └── scan_service.py
│
├── utils/
│
├── app.py
├── main.py
├── theme.py
├── requirements.txt
├── AcoustiGuard.spec
└── AcoustiGuard-Installer.iss
```

*The structure above highlights the main application components; additional supporting files may be present.*

## Installation and Execution

### Requirements

- Windows
- Python installed
- A working microphone
- Audio output device for acoustic masking

### 1. Clone the repository

```powershell
git clone https://github.com/MohomedAzman/AcoustiGuard.git
cd AcoustiGuard
```

### 2. Create a virtual environment

```powershell
python -m venv venv
```

### 3. Activate the environment

```powershell
.\venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```powershell
pip install -r requirements.txt
```

### 5. Run the application

```powershell
python main.py
```

## Windows Executable and Installer

AcoustiGuard includes a PyInstaller specification and an Inno Setup installer script.

- `AcoustiGuard.spec` defines the executable packaging configuration and required application resources.
- `AcoustiGuard-Installer.iss` defines the Windows installer configuration.
- The installer is configured to install the application under the user's local application directory without requiring administrator privileges.

The bundled application uses a separate local application-data directory for its SQLite database when running as a frozen executable.

## Data and Privacy

AcoustiGuard is designed around local audio processing.

- Ambient audio is captured for analysis.
- The database stores scan metadata, selected acoustic features, recommendations and application settings.
- The database implementation does not save raw audio recordings.
- In a packaged Windows build, the SQLite database is stored under `%LOCALAPPDATA%\AcoustiGuard`.

The application's privacy and network behavior should be evaluated against the complete source code and deployment environment before making broader security guarantees.

## Current Limitations

- Risk assessment is heuristic-based and is not a machine learning prediction model.
- Acoustic conditions can vary significantly between rooms, microphones, keyboards and recording devices.
- A risk score does not identify a specific keyboard key or prove that an attack has taken place.
- Acoustic masking is an additional measure, not a guarantee against acoustic side-channel attacks.

## Future Development

Potential areas for further development include:

- Collecting and evaluating larger acoustic keyboard datasets.
- Investigating machine learning approaches for keyboard acoustic pattern recognition.
- Improving risk assessment through broader environmental testing.
- Evaluating masking effectiveness under different acoustic conditions.
- Conducting systematic performance and usability testing.

## Disclaimer

AcoustiGuard is an academic computing project intended to raise awareness of acoustic side-channel security risks and explore possible protective measures. It should not be considered a replacement for established organizational security controls or a guarantee against acoustic attacks.

---

**Project:** AcoustiGuard  
