# -*- coding: utf-8 -*-
"""
SoundSwitch Plugin for Flow Launcher
Author: landrozaum
Repository: https://github.com/landrozaum/SoundSwitch-Plugin-For-FlowLauncher
"""

import sys
import os
import time
import json
import threading
import webbrowser

# Force UTF-8 for standard output on Windows
if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

if sys.stderr.encoding.lower() != 'utf-8':
    try:
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        import codecs
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add local lib directory to path to ensure flowlauncher dependency is always resolved
current_dir = os.path.dirname(os.path.abspath(__file__))
lib_path = os.path.join(current_dir, "lib")
if lib_path not in sys.path:
    sys.path.insert(0, lib_path)

try:
    from flowlauncher import FlowLauncher, FlowLauncherAPI
except ImportError:
    from lib.flowlauncher import FlowLauncher, FlowLauncherAPI

from soundswitch_client import SoundSwitchClient

# Bilingual localization strings (English & Portuguese)
TRANSLATIONS = {
    "en": {
        "not_found_title": "SoundSwitch not found",
        "not_found_sub": "SoundSwitch.CLI.exe was not detected. Click here to download SoundSwitch.",
        "switch_playback_title": "Switch Playback",
        "switch_playback_sub": "Press Enter to switch to the next audio output device",
        "switch_recording_title": "Switch Recording",
        "switch_recording_sub": "Press Enter to switch to the next microphone",
        "mic_muted_title": "Microphone: MUTED",
        "mic_muted_sub": "Press Enter to UNMUTE the microphone",
        "mic_active_title": "Microphone: ACTIVE",
        "mic_active_sub": "Press Enter to MUTE the microphone",
        "mic_toggle_title": "Toggle Microphone Mute",
        "mic_toggle_sub": "Press Enter to toggle mute state",
        "output_prefix": "Output",
        "input_prefix": "Input",
        "active_badge": "Active",
        "device_active_sub": "Currently in use. Press Enter to stay on this device.",
        "device_switch_playback_sub": "Press Enter to switch directly to this audio device.",
        "device_switch_recording_sub": "Press Enter to switch directly to this microphone.",
        "profile_title": "Profile",
        "profile_active_sub": "Currently active audio profile.",
        "profile_switch_sub": "Press Enter to activate this audio profile.",
        "no_profiles_title": "Audio Profiles: No profiles found",
        "no_profiles_sub": "Open SoundSwitch settings to create custom profiles.",
        "settings_title": "SoundSwitch Settings",
        "settings_sub": "Open SoundSwitch preferences, profiles and shortcuts.",
        "no_results_title": "No results for '{query}'",
        "no_results_sub": "Try 'ss play', 'ss rec', 'ss mute', 'ss profile', 'ss devices' or device name.",
        "already_active_msg": "{device} is already active!",
        "playback_changed_msg": "Audio switched to: {device}",
        "recording_changed_msg": "Microphone switched to: {device}",
        "profile_activated_msg": "Profile activated: {profile}",
        "mic_muted_msg": "Microphone MUTED 🔇",
        "mic_unmuted_msg": "Microphone ACTIVE 🎙️"
    },
    "pt": {
        "not_found_title": "SoundSwitch não encontrado",
        "not_found_sub": "SoundSwitch.CLI.exe não foi detectado no sistema. Clique para baixar o SoundSwitch.",
        "switch_playback_title": "Alternar Reprodução",
        "switch_playback_sub": "Pressione Enter para alternar para o próximo som",
        "switch_recording_title": "Alternar Gravação",
        "switch_recording_sub": "Pressione Enter para alternar para o próximo microfone",
        "mic_muted_title": "Microfone: MUTADO",
        "mic_muted_sub": "Pressione Enter para DESMUTAR o microfone",
        "mic_active_title": "Microfone: ATIVO",
        "mic_active_sub": "Pressione Enter para MUTAR o microfone",
        "mic_toggle_title": "Alternar Mudo do Microfone",
        "mic_toggle_sub": "Pressione Enter para alternar o mudo (Mute/Unmute)",
        "output_prefix": "Saída",
        "input_prefix": "Entrada",
        "active_badge": "Ativo",
        "device_active_sub": "Dispositivo atualmente em uso. Pressione Enter para permanecer.",
        "device_switch_playback_sub": "Pressione Enter para mudar diretamente para este dispositivo de som.",
        "device_switch_recording_sub": "Pressione Enter para mudar diretamente para este microfone.",
        "profile_title": "Perfil",
        "profile_active_sub": "Perfil de áudio atualmente ativo.",
        "profile_switch_sub": "Pressione Enter para ativar este perfil de áudio.",
        "no_profiles_title": "Perfis de Áudio: Nenhum perfil cadastrado",
        "no_profiles_sub": "Abra as configurações do SoundSwitch para criar perfis personalizados.",
        "settings_title": "Configurações do SoundSwitch",
        "settings_sub": "Abrir o painel de preferências, perfis e atalhos do SoundSwitch.",
        "no_results_title": "Nenhuma opção para '{query}'",
        "no_results_sub": "Tente 'ss play', 'ss rec', 'ss mute', 'ss profile', 'ss devices' ou o nome do seu fone/mic.",
        "already_active_msg": "{device} já é o dispositivo ativo!",
        "playback_changed_msg": "Áudio alterado para: {device}",
        "recording_changed_msg": "Microfone alterado para: {device}",
        "profile_activated_msg": "Perfil ativado: {profile}",
        "mic_muted_msg": "Microfone MUTADO 🔇",
        "mic_unmuted_msg": "Microfone DESMUTADO 🎙️"
    }
}

def detect_language() -> str:
    """Detect language from Flow Launcher preferences or Windows locale."""
    flow_settings = os.path.expandvars(r"%APPDATA%\FlowLauncher\Settings\Settings.json")
    if os.path.isfile(flow_settings):
        try:
            with open(flow_settings, "r", encoding="utf-8", errors="ignore") as f:
                data = json.load(f)
                lang = str(data.get("Language", "")).lower()
                if lang.startswith("pt"):
                    return "pt"
                if lang.startswith("en"):
                    return "en"
        except Exception:
            pass

    try:
        import locale
        loc = (locale.getlocale()[0] or locale.getdefaultlocale()[0] or "").lower()
        if loc.startswith("pt") or "brazil" in loc or "portuguese" in loc:
            return "pt"
    except Exception:
        pass

    return "en"


class SoundSwitchPlugin(FlowLauncher):

    def __init__(self):
        self.client = SoundSwitchClient()
        self.lang = detect_language()
        self.t = TRANSLATIONS.get(self.lang, TRANSLATIONS["en"])
        super().__init__()

    def _background_refresh(self):
        """Fetch fresh state and connected devices from SoundSwitch CLI in background."""
        try:
            status = self.client.get_status()
            devices = self.client.get_devices()
            profiles = self.client.get_profiles()
            mute = self.client.get_mute_state()

            cache_data = {
                "timestamp": time.time(),
                "playbackDevice": status.get("playbackDevice"),
                "recordingDevice": status.get("recordingDevice"),
                "activeProfile": status.get("activeProfile"),
                "playbackDevices": devices.get("playbackDevices", []),
                "recordingDevices": devices.get("recordingDevices", []),
                "profiles": profiles,
                "isMuted": mute.get("isMuted", False),
                "muteDevice": mute.get("deviceName")
            }
            self.client.save_cached_status(cache_data)
        except Exception:
            pass

    def query(self, query: str = "") -> list:
        q = (query or "").strip().lower()

        # Check if SoundSwitch is installed
        if not self.client.is_installed():
            return [
                {
                    "Title": self.t["not_found_title"],
                    "SubTitle": self.t["not_found_sub"],
                    "IcoPath": "Images/icon.png",
                    "JsonRPCAction": {
                        "method": "open_url",
                        "parameters": ["https://soundswitch.aaflalo.me/"],
                        "dontHideAfterAction": False
                    }
                }
            ]

        # 1. Instant Cache (< 1ms, zero blocking)
        cached = self.client.get_cached_status()

        now = time.time()
        last_time = cached.get("timestamp", 0)

        # Trigger background refresh if cache is older than 20 seconds or missing
        if now - last_time > 20 or not cached:
            threading.Thread(target=self._background_refresh, daemon=True).start()

        current_playback = cached.get("playbackDevice")
        current_recording = cached.get("recordingDevice")
        active_profile = cached.get("activeProfile")
        is_muted = cached.get("isMuted")

        # ONLY CONNECTED DEVICES (from SoundSwitch devices CLI, never disconnected/offline devices)
        pb_devs = cached.get("playbackDevices", [])
        rec_devs = cached.get("recordingDevices", [])
        profiles = cached.get("profiles", [])

        # Format labels
        pb_label = f" ({current_playback})" if current_playback else ""
        rec_label = f" ({current_recording})" if current_recording else ""

        results = []

        # 1. Playback Switch Item (Cycles to next sound)
        results.append({
            "Title": f"{self.t['switch_playback_title']}{pb_label}",
            "SubTitle": self.t["switch_playback_sub"],
            "IcoPath": "Images/playback.png",
            "Score": 100,
            "category": "playback",
            "JsonRPCAction": {
                "method": "switch_playback",
                "parameters": [],
                "dontHideAfterAction": False
            }
        })

        # 2. Recording Switch Item (Cycles to next mic)
        results.append({
            "Title": f"{self.t['switch_recording_title']}{rec_label}",
            "SubTitle": self.t["switch_recording_sub"],
            "IcoPath": "Images/recording.png",
            "Score": 95,
            "category": "recording",
            "JsonRPCAction": {
                "method": "switch_recording",
                "parameters": [],
                "dontHideAfterAction": False
            }
        })

        # 3. Mute Toggle Item
        if is_muted is True:
            mute_title = self.t["mic_muted_title"]
            mute_sub = self.t["mic_muted_sub"]
            mute_ico = "Images/mute.png"
        elif is_muted is False:
            mute_title = self.t["mic_active_title"]
            mute_sub = self.t["mic_active_sub"]
            mute_ico = "Images/unmute.png"
        else:
            mute_title = self.t["mic_toggle_title"]
            mute_sub = self.t["mic_toggle_sub"]
            mute_ico = "Images/mute.png"

        results.append({
            "Title": mute_title,
            "SubTitle": mute_sub,
            "IcoPath": mute_ico,
            "Score": 90,
            "category": "mute",
            "JsonRPCAction": {
                "method": "toggle_mute",
                "parameters": [],
                "dontHideAfterAction": False
            }
        })

        # 4. Connected Playback Devices (Direct Target Switch)
        for dev in pb_devs:
            is_curr = bool(current_playback and (dev.lower() == current_playback.lower() or dev.lower() in current_playback.lower()))
            if is_curr:
                dev_title = f"{self.t['output_prefix']}: {dev} ✓ {self.t['active_badge']}"
                dev_sub = self.t["device_active_sub"]
            else:
                dev_title = f"{self.t['output_prefix']}: {dev}"
                dev_sub = self.t["device_switch_playback_sub"]

            results.append({
                "Title": dev_title,
                "SubTitle": dev_sub,
                "IcoPath": "Images/playback.png" if is_curr else "Images/device.png",
                "Score": 88 if is_curr else 82,
                "category": "playback_device",
                "JsonRPCAction": {
                    "method": "select_playback_device",
                    "parameters": [dev],
                    "dontHideAfterAction": False
                }
            })

        # 5. Connected Recording Devices (Direct Target Switch)
        for dev in rec_devs:
            is_curr = bool(current_recording and (dev.lower() == current_recording.lower() or dev.lower() in current_recording.lower()))
            if is_curr:
                dev_title = f"{self.t['input_prefix']}: {dev} ✓ {self.t['active_badge']}"
                dev_sub = self.t["device_active_sub"]
            else:
                dev_title = f"{self.t['input_prefix']}: {dev}"
                dev_sub = self.t["device_switch_recording_sub"]

            results.append({
                "Title": dev_title,
                "SubTitle": dev_sub,
                "IcoPath": "Images/recording.png" if is_curr else "Images/device.png",
                "Score": 86 if is_curr else 80,
                "category": "recording_device",
                "JsonRPCAction": {
                    "method": "select_recording_device",
                    "parameters": [dev],
                    "dontHideAfterAction": False
                }
            })

        # 6. Audio Profiles
        if profiles:
            for p_name in profiles:
                is_this_active = bool(active_profile and active_profile.lower() == p_name.lower())
                p_title = f"{self.t['profile_title']}: {p_name}" + (f" [{self.t['active_badge'].upper()}]" if is_this_active else "")
                p_subtitle = self.t["profile_active_sub"] if is_this_active else self.t["profile_switch_sub"]
                results.append({
                    "Title": p_title,
                    "SubTitle": p_subtitle,
                    "IcoPath": "Images/profile.png",
                    "Score": 76 if is_this_active else 75,
                    "category": "profile",
                    "JsonRPCAction": {
                        "method": "switch_profile",
                        "parameters": [p_name],
                        "dontHideAfterAction": False
                    }
                })
        else:
            results.append({
                "Title": self.t["no_profiles_title"],
                "SubTitle": self.t["no_profiles_sub"],
                "IcoPath": "Images/profile.png",
                "Score": 75,
                "category": "profile",
                "JsonRPCAction": {
                    "method": "open_settings",
                    "parameters": [],
                    "dontHideAfterAction": False
                }
            })

        # 7. Settings Item
        results.append({
            "Title": self.t["settings_title"],
            "SubTitle": self.t["settings_sub"],
            "IcoPath": "Images/settings.png",
            "Score": 60,
            "category": "settings",
            "JsonRPCAction": {
                "method": "open_settings",
                "parameters": [],
                "dontHideAfterAction": False
            }
        })

        # If user typed a query, filter or match subcommands
        if not q:
            return results

        # Fast Subcommand Shortcuts (English commands as primary, with friendly PT aliases)
        if q in ("play", "playback", "output", "saida", "som", "audio"):
            return [r for r in results if r.get("category") in ("playback", "playback_device")]

        if q in ("rec", "recording", "input", "mic", "microfone", "gravacao"):
            return [r for r in results if r.get("category") in ("recording", "recording_device")]

        if q in ("mute", "unmute", "toggle", "mudo", "desmutar"):
            return [r for r in results if r.get("category") == "mute"]

        if q in ("profile", "profiles", "p", "perfil", "perfis"):
            return [r for r in results if r.get("category") == "profile"]

        if q in ("devices", "dev", "dispositivos"):
            return [r for r in results if r.get("category") in ("playback_device", "recording_device")]

        if q in ("settings", "set", "config", "configuracoes"):
            return [r for r in results if r.get("category") == "settings"]

        # Text search (e.g., 'ss fifine' will find and prioritize the device)
        filtered = []
        tokens = q.split()
        for item in results:
            text_to_search = f"{item.get('Title', '')} {item.get('SubTitle', '')} {item.get('category', '')}".lower()
            if all(token in text_to_search for token in tokens):
                filtered.append(item)

        if not filtered:
            filtered.append({
                "Title": self.t["no_results_title"].format(query=query),
                "SubTitle": self.t["no_results_sub"],
                "IcoPath": "Images/icon.png"
            })

        return filtered

    # Action Methods called via Flow Launcher JSON-RPC
    def select_playback_device(self, target_device: str):
        """Switch directly to target device, or stay if already on it."""
        status = self.client.get_status()
        current = status.get("playbackDevice", "")

        # Check if already active
        if target_device.lower() in current.lower() or current.lower() in target_device.lower():
            msg = self.t["already_active_msg"].format(device=target_device)
            FlowLauncherAPI.show_msg("SoundSwitch", msg, "Images/playback.png")
            return

        success = self.client.switch_to_playback_device(target_device)
        new_status = self.client.get_status()
        new_current = new_status.get("playbackDevice", target_device)

        # Update cache immediately
        cached = self.client.get_cached_status()
        cached["playbackDevice"] = new_current
        cached["timestamp"] = time.time()
        self.client.save_cached_status(cached)

        msg = self.t["playback_changed_msg"].format(device=new_current)
        FlowLauncherAPI.show_msg("SoundSwitch", msg, "Images/playback.png")

    def select_recording_device(self, target_device: str):
        """Switch directly to target microphone, or stay if already on it."""
        status = self.client.get_status()
        current = status.get("recordingDevice", "")

        # Check if already active
        if target_device.lower() in current.lower() or current.lower() in target_device.lower():
            msg = self.t["already_active_msg"].format(device=target_device)
            FlowLauncherAPI.show_msg("SoundSwitch", msg, "Images/recording.png")
            return

        success = self.client.switch_to_recording_device(target_device)
        new_status = self.client.get_status()
        new_current = new_status.get("recordingDevice", target_device)

        # Update cache immediately
        cached = self.client.get_cached_status()
        cached["recordingDevice"] = new_current
        cached["timestamp"] = time.time()
        self.client.save_cached_status(cached)

        msg = self.t["recording_changed_msg"].format(device=new_current)
        FlowLauncherAPI.show_msg("SoundSwitch", msg, "Images/recording.png")

    def switch_playback(self):
        """Cycle to next playback device."""
        self.client.switch_playback()
        try:
            new_status = self.client.get_status()
            current = new_status.get("playbackDevice", "Audio device")
            cached = self.client.get_cached_status()
            cached["playbackDevice"] = current
            cached["timestamp"] = time.time()
            self.client.save_cached_status(cached)
            msg = self.t["playback_changed_msg"].format(device=current)
            FlowLauncherAPI.show_msg("SoundSwitch", msg, "Images/playback.png")
        except Exception:
            FlowLauncherAPI.show_msg("SoundSwitch", "Audio device switched!", "Images/playback.png")

    def switch_recording(self):
        """Cycle to next recording device."""
        self.client.switch_recording()
        try:
            new_status = self.client.get_status()
            current = new_status.get("recordingDevice", "Microphone")
            cached = self.client.get_cached_status()
            cached["recordingDevice"] = current
            cached["timestamp"] = time.time()
            self.client.save_cached_status(cached)
            msg = self.t["recording_changed_msg"].format(device=current)
            FlowLauncherAPI.show_msg("SoundSwitch", msg, "Images/recording.png")
        except Exception:
            FlowLauncherAPI.show_msg("SoundSwitch", "Microphone switched!", "Images/recording.png")

    def switch_profile(self, profile_name: str):
        success = self.client.switch_profile(profile_name)
        if success:
            cached = self.client.get_cached_status()
            cached["activeProfile"] = profile_name
            cached["timestamp"] = time.time()
            self.client.save_cached_status(cached)
            msg = self.t["profile_activated_msg"].format(profile=profile_name)
            FlowLauncherAPI.show_msg("SoundSwitch", msg, "Images/profile.png")
        else:
            FlowLauncherAPI.show_msg("SoundSwitch", f"Failed to activate profile: {profile_name}", "Images/icon.png")

    def toggle_mute(self):
        res = self.client.toggle_mute()
        is_muted = res.get("isMuted", False)
        cached = self.client.get_cached_status()
        cached["isMuted"] = is_muted
        cached["timestamp"] = time.time()
        self.client.save_cached_status(cached)
        msg = self.t["mic_muted_msg"] if is_muted else self.t["mic_unmuted_msg"]
        icon = "Images/mute.png" if is_muted else "Images/unmute.png"
        FlowLauncherAPI.show_msg("SoundSwitch", msg, icon)

    def open_settings(self):
        self.client.open_settings()

    def open_url(self, url: str):
        webbrowser.open(url)

if __name__ == "__main__":
    SoundSwitchPlugin()
