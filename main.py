# -*- coding: utf-8 -*-
"""
SoundSwitch Plugin for Flow Launcher
Author: landrozaum
Repository: https://github.com/landrozaum/SoundSwitch-Plugin-For-FlowLauncher
"""

import sys
import os
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

from soundswitch_client import SoundSwitchClient, SoundSwitchNotFoundError

class SoundSwitchPlugin(FlowLauncher):

    def __init__(self):
        self.client = SoundSwitchClient()
        super().__init__()

    def query(self, query: str = "") -> list:
        q = (query or "").strip().lower()

        # Check if SoundSwitch CLI is installed
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

        try:
            status = self.client.get_status()
            devices = self.client.get_devices()
            profiles = self.client.get_profiles()
            mute_state = self.client.get_mute_state()
        except Exception as e:
            return [
                {
                    "Title": "Erro ao comunicar com o SoundSwitch",
                    "SubTitle": f"Detalhe: {e}",
                    "IcoPath": "Images/icon.png"
                }
            ]

        results = []

        current_playback = status.get("playbackDevice") or "Desconhecido"
        current_recording = status.get("recordingDevice") or "Desconhecido"
        active_profile = status.get("activeProfile")
        is_muted = mute_state.get("isMuted", False)
        mute_device = mute_state.get("deviceName", current_recording)

        # 1. Playback Switch Item
        results.append({
            "Title": f"Reprodução: {current_playback}",
            "SubTitle": "Pressione Enter para alternar para o próximo dispositivo de saída de áudio",
            "IcoPath": "Images/playback.png",
            "Score": 100,
            "category": "playback",
            "JsonRPCAction": {
                "method": "switch_playback",
                "parameters": [],
                "dontHideAfterAction": False
            }
        })

        # 2. Recording Switch Item
        results.append({
            "Title": f"Gravação: {current_recording}",
            "SubTitle": "Pressione Enter para alternar para o próximo microfone / dispositivo de entrada",
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
        mute_title = "Microfone: MUTADO" if is_muted else "Microfone: ATIVO (Desmutado)"
        mute_subtitle = "Pressione Enter para DESMUTAR o microfone" if is_muted else "Pressione Enter para MUTAR o microfone"
        mute_icon = "Images/mute.png" if is_muted else "Images/unmute.png"
        results.append({
            "Title": mute_title,
            "SubTitle": f"{mute_subtitle} ({mute_device})",
            "IcoPath": mute_icon,
            "Score": 90,
            "category": "mute",
            "JsonRPCAction": {
                "method": "toggle_mute",
                "parameters": [],
                "dontHideAfterAction": False
            }
        })

        # 4. Audio Profiles
        if profiles:
            for p_name in profiles:
                is_this_active = (active_profile and active_profile.lower() == p_name.lower())
                p_title = f"Perfil: {p_name}" + (" [ATIVO]" if is_this_active else "")
                p_subtitle = "Perfil de áudio atualmente ativo" if is_this_active else "Pressione Enter para ativar este perfil de áudio"
                results.append({
                    "Title": p_title,
                    "SubTitle": p_subtitle,
                    "IcoPath": "Images/profile.png",
                    "Score": 85 if not is_this_active else 86,
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

        # 5. Configured Switching Devices List
        pb_devs = devices.get("playbackDevices", [])
        for dev in pb_devs:
            is_curr = (dev == current_playback)
            results.append({
                "Title": f"Saída: {dev}" + (" ✓ Ativo" if is_curr else ""),
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

        rec_devs = devices.get("recordingDevices", [])
        for dev in rec_devs:
            is_curr = (dev == current_recording)
            results.append({
                "Title": f"Entrada: {dev}" + (" ✓ Ativo" if is_curr else ""),
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
            "SubTitle": "Abrir o painel de configurações, perfis e atalhos do SoundSwitch",
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

        # Subcommand keyword shortcuts
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

        # General text filtering
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
            current = new_status.get("playbackDevice", "Novo dispositivo")
            FlowLauncherAPI.show_msg("SoundSwitch", f"Áudio alterado para: {current}", "Images/playback.png")
        except Exception:
            if success:
                FlowLauncherAPI.show_msg("SoundSwitch", "Dispositivo de reprodução alternado!", "Images/playback.png")
            else:
                FlowLauncherAPI.show_msg("SoundSwitch", "Falha ao alternar reprodução", "Images/icon.png")

    def switch_recording(self):
        success = self.client.switch_recording()
        try:
            new_status = self.client.get_status()
            current = new_status.get("recordingDevice", "Novo microfone")
            FlowLauncherAPI.show_msg("SoundSwitch", f"Microfone alterado para: {current}", "Images/recording.png")
        except Exception:
            if success:
                FlowLauncherAPI.show_msg("SoundSwitch", "Dispositivo de gravação alternado!", "Images/recording.png")
            else:
                FlowLauncherAPI.show_msg("SoundSwitch", "Falha ao alternar microfone", "Images/icon.png")

    def switch_profile(self, profile_name: str):
        success = self.client.switch_profile(profile_name)
        if success:
            FlowLauncherAPI.show_msg("SoundSwitch", f"Perfil ativado: {profile_name}", "Images/profile.png")
        else:
            FlowLauncherAPI.show_msg("SoundSwitch", f"Falha ao ativar perfil: {profile_name}", "Images/icon.png")

    def toggle_mute(self):
        res = self.client.toggle_mute()
        is_muted = res.get("isMuted", False)
        msg = "Microfone MUTADO 🔇" if is_muted else "Microfone DESMUTADO 🎙️"
        icon = "Images/mute.png" if is_muted else "Images/unmute.png"
        FlowLauncherAPI.show_msg("SoundSwitch", msg, icon)

    def open_settings(self):
        self.client.open_settings()

    def open_url(self, url: str):
        webbrowser.open(url)

if __name__ == "__main__":
    SoundSwitchPlugin()
