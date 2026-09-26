# -*- coding: utf-8 -*-
"""
SoundSwitch Plugin for Flow Launcher (Ultra-Fast Zero-Latency Edition)
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
        """Fetch fresh state from SoundSwitch CLI in background without blocking query."""
        try:
            status = self.client.get_status()
            mute = self.client.get_mute_state()
            cache_data = {
                "timestamp": time.time(),
                "playbackDevice": status.get("playbackDevice"),
                "recordingDevice": status.get("recordingDevice"),
                "activeProfile": status.get("activeProfile"),
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

        # 1. Instant Cache & Config Read (< 1ms, zero blocking)
        cached = self.client.get_cached_status()
        config = self.client.read_config_file()

        now = time.time()
        last_time = cached.get("timestamp", 0)

        # Trigger background refresh if cache is older than 20 seconds or missing
        if now - last_time > 20:
            threading.Thread(target=self._background_refresh, daemon=True).start()

        current_playback = cached.get("playbackDevice")
        current_recording = cached.get("recordingDevice")
        active_profile = cached.get("activeProfile")
        is_muted = cached.get("isMuted")

        # Fallback names if not yet cached
        pb_label = f" ({current_playback})" if current_playback else ""
        rec_label = f" ({current_recording})" if current_recording else ""

        results = []

        # 1. Playback Switch Item (Instant Enter!)
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

        # 2. Recording Switch Item (Instant Enter!)
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

        # 4. Audio Profiles from fast config file (< 0.5ms)
        raw_profiles = config.get("Profiles", [])
        if raw_profiles:
            for p in raw_profiles:
                p_name = p.get("Name") if isinstance(p, dict) else str(p)
                if not p_name:
                    continue
                is_this_active = (active_profile and active_profile.lower() == p_name.lower())
                p_title = f"Perfil: {p_name}" + (" [ATIVO]" if is_this_active else "")
                p_subtitle = "Perfil atualmente ativo" if is_this_active else "Pressione Enter para ativar este perfil"
                results.append({
                    "Title": p_title,
                    "SubTitle": p_subtitle,
                    "IcoPath": "Images/profile.png",
                    "Score": 86 if is_this_active else 85,
                    "category": "profile",
                    "JsonRPCAction": {
                        "method": "switch_profile",
                        "parameters": [p_name],
                        "dontHideAfterAction": False
                    }
                })
        else:
            results.append({
                "Title": "Perfis de Áudio: Nenhum perfil cadastrado",
                "SubTitle": "Abra as configurações do SoundSwitch para criar perfis personalizados",
                "IcoPath": "Images/profile.png",
                "Score": 75,
                "category": "profile",
                "JsonRPCAction": {
                    "method": "open_settings",
                    "parameters": [],
                    "dontHideAfterAction": False
                }
            })

        # 5. Devices configured in SoundSwitch (< 0.5ms)
        raw_devices = config.get("SelectedDevices", [])
        for dev in raw_devices:
            dev_name = dev.get("NameClean") or dev.get("Name")
            dev_type = dev.get("Type", 0) # 0 = Playback, 1 = Recording
            if not dev_name:
                continue

            if dev_type == 0:
                is_curr = (current_playback and dev_name.lower() in current_playback.lower())
                results.append({
                    "Title": f"Saída: {dev_name}" + (" ✓ Ativo" if is_curr else ""),
                    "SubTitle": "Dispositivo configurado no SoundSwitch para reprodução",
                    "IcoPath": "Images/device.png",
                    "Score": 70 if is_curr else 65,
                    "category": "devices",
                    "JsonRPCAction": {
                        "method": "switch_playback",
                        "parameters": [],
                        "dontHideAfterAction": False
                    }
                })
            else:
                is_curr = (current_recording and dev_name.lower() in current_recording.lower())
                results.append({
                    "Title": f"Entrada: {dev_name}" + (" ✓ Ativo" if is_curr else ""),
                    "SubTitle": "Dispositivo configurado no SoundSwitch para gravação",
                    "IcoPath": "Images/recording.png",
                    "Score": 68 if is_curr else 63,
                    "category": "devices",
                    "JsonRPCAction": {
                        "method": "switch_recording",
                        "parameters": [],
                        "dontHideAfterAction": False
                    }
                })

        # 6. Settings Item
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
            return [r for r in results if r.get("category") == "playback" or (r.get("category") == "devices" and "Saída" in r.get("Title", ""))]

        if q in ("rec", "recording", "mic", "microfone", "gravacao"):
            return [r for r in results if r.get("category") == "recording" or (r.get("category") == "devices" and "Entrada" in r.get("Title", ""))]

        if q in ("mute", "unmute", "mudo", "desmutar", "toggle"):
            return [r for r in results if r.get("category") == "mute"]

        if q in ("profile", "profiles", "p", "perfil", "perfis"):
            return [r for r in results if r.get("category") == "profile"]

        if q in ("devices", "dev", "dispositivos"):
            return [r for r in results if r.get("category") == "devices"]

        if q in ("settings", "set", "config", "configuracoes"):
            return [r for r in results if r.get("category") == "settings"]

        # Text search
        filtered = []
        tokens = q.split()
        for item in results:
            text_to_search = f"{item.get('Title', '')} {item.get('SubTitle', '')} {item.get('category', '')}".lower()
            if all(token in text_to_search for token in tokens):
                filtered.append(item)

        if not filtered:
            filtered.append({
                "Title": f"Nenhuma opção para '{query}'",
                "SubTitle": "Tente 'ss play', 'ss rec', 'ss mute', 'ss profile', 'ss devices' ou 'ss settings'",
                "IcoPath": "Images/icon.png"
            })

        return filtered

    # Action Methods called via Flow Launcher JSON-RPC
    def switch_playback(self):
        success = self.client.switch_playback()
        try:
            new_status = self.client.get_status()
            current = new_status.get("playbackDevice", "Próximo dispositivo")
            # Update cache immediately
            cached = self.client.get_cached_status()
            cached["playbackDevice"] = current
            cached["timestamp"] = time.time()
            self.client.save_cached_status(cached)
            FlowLauncherAPI.show_msg("SoundSwitch", f"Áudio alterado: {current}", "Images/playback.png")
        except Exception:
            FlowLauncherAPI.show_msg("SoundSwitch", "Dispositivo de áudio alternado!", "Images/playback.png")

    def switch_recording(self):
        success = self.client.switch_recording()
        try:
            new_status = self.client.get_status()
            current = new_status.get("recordingDevice", "Próximo microfone")
            # Update cache immediately
            cached = self.client.get_cached_status()
            cached["recordingDevice"] = current
            cached["timestamp"] = time.time()
            self.client.save_cached_status(cached)
            FlowLauncherAPI.show_msg("SoundSwitch", f"Microfone alterado: {current}", "Images/recording.png")
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
        # Update cache immediately
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
