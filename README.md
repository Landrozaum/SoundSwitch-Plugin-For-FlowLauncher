# SoundSwitch Plugin for Flow Launcher 🎧🎙️

Seamlessly switch audio playback devices, microphones, profiles, and toggle microphone mute directly from **[Flow Launcher](https://www.flowlauncher.com/)** using **[SoundSwitch](https://soundswitch.aaflalo.me/)**.

<p align="center">
  <img src="Images/icon.png" alt="SoundSwitch Plugin Icon" width="96" height="96" />
</p>

---

## ⚡ Features

- **Direct Target Switching**: Click on any connected playback or recording device to switch directly to it. If the device is already active, it safely remains without unnecessary cycling.
- **Active Connected Devices Only**: Dynamically detects and lists only currently connected and operational audio devices (filters out offline TVs or paired inactive Bluetooth gear).
- **Fast Playback Cycling**: Cycle through configured audio outputs (headphones, speakers, monitors) with a single keystroke.
- **Microphone Management**: Switch recording inputs and toggle microphone mute status with real-time visual feedback.
- **Audio Profiles**: Quickly activate predefined SoundSwitch sound profiles.
- **Zero Latency**: Instant query response with non-blocking background caching.
- **Bilingual Interface**: Automatic localization for English and Portuguese based on Flow Launcher system settings.

---

## ⌨️ Usage

The default trigger keyword is **`ss`**.

Press <kbd>Alt</kbd> + <kbd>Space</kbd>, type `ss`, and press <kbd>Enter</kbd> to cycle your primary audio device immediately, or pick any connected device from the list.

### Commands

| Command | Action |
|---|---|
| `ss` | Shows real-time audio status and action list |
| `ss play` | Lists connected playback devices and output cycling |
| `ss rec` | Lists connected microphones and input cycling |
| `ss mute` | Toggles microphone mute state |
| `ss profile` | Lists and activates configured audio profiles |
| `ss devices` | Displays all connected input and output devices |
| `ss settings` | Opens SoundSwitch settings window |

You can also filter by device name directly (e.g. `ss fifine`, `ss usb`, `ss speakers`).

---

## 📦 Requirements

- **[Flow Launcher](https://www.flowlauncher.com/)** (v1.10+)
- **[SoundSwitch](https://soundswitch.aaflalo.me/)** (v6.0+) installed on Windows
- **Python 3.8+** installed

---

## 🛠️ Installation

### Manual Installation
1. Download or clone this repository.
2. Copy the plugin folder to your Flow Launcher plugins directory:
   ```text
   %APPDATA%\FlowLauncher\Plugins\SoundSwitch
   ```
3. Restart Flow Launcher or run `rpd` (Reload Plugin Data).

---

## 📂 Project Structure

```text
SoundSwitch-Plugin-For-FlowLauncher/
├── plugin.json              # Flow Launcher manifest
├── main.py                  # Plugin entry point & JSON-RPC handler
├── soundswitch_client.py    # SoundSwitch CLI client interface
├── requirements.txt         # Dependency specification
├── README.md                # Documentation
├── LICENSE                  # MIT License
├── Images/                  # High-resolution icons
│   ├── icon.png
│   ├── playback.png
│   ├── recording.png
│   ├── mute.png
│   ├── unmute.png
│   ├── profile.png
│   ├── settings.png
│   └── device.png
└── lib/
    └── flowlauncher/        # Embedded JSON-RPC base library
```

---

## 📄 License

Distributed under the [MIT License](LICENSE).
