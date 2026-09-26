# -*- coding: utf-8 -*-
"""
SoundSwitch Plugin for Flow Launcher (v1.2.0 - Direct Target Switching)
Author: landrozaum
Repository: https://github.com/landrozaum/SoundSwitch-Plugin-For-FlowLauncher
"""

import sys
import os
import time
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

class SoundSwitchPlugin(FlowLauncher):

    def __init__(self):
        self.client = SoundSwitchClient()
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
                    "Title": "SoundSwitch não encontrado",
                    "SubTitle": "SoundSwitch.CLI.exe não foi detectado no sistema. Clique aqui para baixar o SoundSwitch.",
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

        # Fallback names if not yet cached
        pb_label = f" ({current_playback})" if current_playback else ""
        rec_label = f" ({current_recording})" if current_recording else ""

        results = []

        # 1. Playback Switch Item (Cycles to next sound)
        results.append({
            "Title": f"Alternar Reprodução{pb_label}",
            "SubTitle": "Pressione Enter para alternar para o próximo som",
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
            "Title": f"Alternar Gravação{rec_label}",
            "SubTitle": "Pressione Enter para alternar para o próximo microfone",
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
            mute_title = "Microfone: MUTADO"
            mute_sub = "Pressione Enter para DESMUTAR o microfone"
            mute_ico = "Images/mute.png"
        elif is_muted is False:
            mute_title = "Microfone: ATIVO"
            mute_sub = "Pressione Enter para MUTAR o microfone"
            mute_ico = "Images/unmute.png"
        else:
            mute_title = "Alternar Mudo do Microfone"
            mute_sub = "Pressione Enter para alternar o mudo (Mute/Unmute)"
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

        # 4. Connected Playback Devices (Direct Select!)
        for dev in pb_devs:
            is_curr = (current_playback and (dev.lower() == current_playback.lower() or dev.lower() in current_playback.lower()))
            if is_curr:
                dev_title = f"Saída: {dev} ✓ Ativo"
                dev_sub = "Dispositivo atualmente em uso. Pressione Enter para permanecer."
            else:
                dev_title = f"Saída: {dev}"
                dev_sub = "Pressione Enter para mudar diretamente para este dispositivo de som."

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

        # 5. Connected Recording Devices (Direct Select!)
        for dev in rec_devs:
            is_curr = (current_recording and (dev.lower() == current_recording.lower() or dev.lower() in current_recording.lower()))
            if is_curr:
                dev_title = f"Entrada: {dev} ✓ Ativo"
                dev_sub = "Microfone atualmente em uso. Pressione Enter para permanecer."
            else:
                dev_title = f"Entrada: {dev}"
                dev_sub = "Pressione Enter para mudar diretamente para este microfone."

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
                is_this_active = (active_profile and active_profile.lower() == p_name.lower())
                p_title = f"Perfil: {p_name}" + (" [ATIVO]" if is_this_active else "")
                p_subtitle = "Perfil atualmente ativo" if is_this_active else "Pressione Enter para ativar este perfil"
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

        # 7. Settings Item
        results.append({
            "Title": "Configurações do SoundSwitch",
            "SubTitle": "Abrir o painel de preferências, perfis e atalhos do SoundSwitch",
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

        # Fast Subcommand Shortcuts
        if q in ("play", "playback", "saida", "som", "audio"):
            return [r for r in results if r.get("category") in ("playback", "playback_device")]

        if q in ("rec", "recording", "mic", "microfone", "gravacao"):
            return [r for r in results if r.get("category") in ("recording", "recording_device")]

        if q in ("mute", "unmute", "mudo", "desmutar", "toggle"):
            return [r for r in results if r.get("category") == "mute"]

        if q in ("profile", "profiles", "p", "perfil", "perfis"):
            return [r for r in results if r.get("category") == "profile"]

        if q in ("devices", "dev", "dispositivos"):
            return [r for r in results if r.get("category") in ("playback_device", "recording_device")]

        if q in ("settings", "set", "config", "configuracoes"):
            return [r for r in results if r.get("category") == "settings"]

        # Text search (e.g., 'ss fifine' will find and prioritize the Fifine device directly)
        filtered = []
        tokens = q.split()
        for item in results:
            text_to_search = f"{item.get('Title', '')} {item.get('SubTitle', '')} {item.get('category', '')}".lower()
            if all(token in text_to_search for token in tokens):
                filtered.append(item)

        if not filtered:
            filtered.append({
                "Title": f"Nenhuma opção para '{query}'",
                "SubTitle": "Tente 'ss play', 'ss rec', 'ss mute', 'ss profile', 'ss devices' ou o nome do seu fone/mic",
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
            FlowLauncherAPI.show_msg("SoundSwitch", f"{target_device} já é o dispositivo ativo!", "Images/playback.png")
            return

        success = self.client.switch_to_playback_device(target_device)
        new_status = self.client.get_status()
        new_current = new_status.get("playbackDevice", target_device)

        # Update cache immediately
        cached = self.client.get_cached_status()
        cached["playbackDevice"] = new_current
        cached["timestamp"] = time.time()
        self.client.save_cached_status(cached)

        if success:
            FlowLauncherAPI.show_msg("SoundSwitch", f"Áudio alterado para: {new_current}", "Images/playback.png")
        else:
            FlowLauncherAPI.show_msg("SoundSwitch", f"Dispositivo selecionado: {new_current}", "Images/playback.png")

    def select_recording_device(self, target_device: str):
        """Switch directly to target microphone, or stay if already on it."""
        status = self.client.get_status()
        current = status.get("recordingDevice", "")

        # Check if already active
        if target_device.lower() in current.lower() or current.lower() in target_device.lower():
            FlowLauncherAPI.show_msg("SoundSwitch", f"{target_device} já é o microfone ativo!", "Images/recording.png")
            return

        success = self.client.switch_to_recording_device(target_device)
        new_status = self.client.get_status()
        new_current = new_status.get("recordingDevice", target_device)

        # Update cache immediately
        cached = self.client.get_cached_status()
        cached["recordingDevice"] = new_current
        cached["timestamp"] = time.time()
        self.client.save_cached_status(cached)

        if success:
            FlowLauncherAPI.show_msg("SoundSwitch", f"Microfone alterado para: {new_current}", "Images/recording.png")
        else:
            FlowLauncherAPI.show_msg("SoundSwitch", f"Microfone selecionado: {new_current}", "Images/recording.png")

    def switch_playback(self):
        """Cycle to next playback device."""
        self.client.switch_playback()
        try:
            new_status = self.client.get_status()
            current = new_status.get("playbackDevice", "Próximo som")
            cached = self.client.get_cached_status()
            cached["playbackDevice"] = current
            cached["timestamp"] = time.time()
            self.client.save_cached_status(cached)
            FlowLauncherAPI.show_msg("SoundSwitch", f"Áudio alternado para: {current}", "Images/playback.png")
        except Exception:
            FlowLauncherAPI.show_msg("SoundSwitch", "Dispositivo de reprodução alternado!", "Images/playback.png")

    def switch_recording(self):
        """Cycle to next recording device."""
        self.client.switch_recording()
        try:
            new_status = self.client.get_status()
            current = new_status.get("recordingDevice", "Próximo microfone")
            cached = self.client.get_cached_status()
            cached["recordingDevice"] = current
            cached["timestamp"] = time.time()
            self.client.save_cached_status(cached)
            FlowLauncherAPI.show_msg("SoundSwitch", f"Microfone alternado para: {current}", "Images/recording.png")
        except Exception:
            FlowLauncherAPI.show_msg("SoundSwitch", "Dispositivo de gravação alternado!", "Images/recording.png")

    def switch_profile(self, profile_name: str):
        success = self.client.switch_profile(profile_name)
        if success:
            cached = self.client.get_cached_status()
            cached["activeProfile"] = profile_name
            cached["timestamp"] = time.time()
            self.client.save_cached_status(cached)
            FlowLauncherAPI.show_msg("SoundSwitch", f"Perfil ativado: {profile_name}", "Images/profile.png")
        else:
            FlowLauncherAPI.show_msg("SoundSwitch", f"Falha ao ativar perfil: {profile_name}", "Images/icon.png")

    def toggle_mute(self):
        res = self.client.toggle_mute()
        is_muted = res.get("isMuted", False)
        cached = self.client.get_cached_status()
        cached["isMuted"] = is_muted
        cached["timestamp"] = time.time()
        self.client.save_cached_status(cached)
        msg = "Microfone MUTADO 🔇" if is_muted else "Microfone DESMUTADO 🎙️"
        icon = "Images/mute.png" if is_muted else "Images/unmute.png"
        FlowLauncherAPI.show_msg("SoundSwitch", msg, icon)

    def open_settings(self):
        self.client.open_settings()

    def open_url(self, url: str):
        webbrowser.open(url)

if __name__ == "__main__":
    SoundSwitchPlugin()
