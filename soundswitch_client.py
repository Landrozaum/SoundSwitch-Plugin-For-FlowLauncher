# -*- coding: utf-8 -*-
"""
SoundSwitch CLI Client
Provides a clean and robust Python interface to interact with SoundSwitch.CLI.exe.
"""

import os
import shutil
import subprocess
import json
from typing import Optional, Dict, Any, List

class SoundSwitchNotFoundError(Exception):
    """Raised when SoundSwitch.CLI.exe is not found on the system."""
    pass

class SoundSwitchClient:
    """Wrapper around SoundSwitch.CLI executable."""

    DEFAULT_PATHS = [
        r"C:\Program Files\SoundSwitch\SoundSwitch.CLI.exe",
        r"C:\Program Files (x86)\SoundSwitch\SoundSwitch.CLI.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\SoundSwitch\SoundSwitch.CLI.exe"),
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\SoundSwitch\SoundSwitch.CLI.exe"),
        os.path.expandvars(r"%PROGRAMFILES%\SoundSwitch\SoundSwitch.CLI.exe"),
    ]

    def __init__(self, cli_path: Optional[str] = None):
        self._cli_path = cli_path or self._find_cli_executable()
        self._config_file = os.path.expandvars(r"%APPDATA%\SoundSwitch\SoundSwitchConfiguration.json")
        self._cache_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".cache.json")

    def read_config_file(self) -> Dict[str, Any]:
        """Read SoundSwitchConfiguration.json directly from disk in < 1ms."""
        if os.path.isfile(self._config_file):
            try:
                with open(self._config_file, "r", encoding="utf-8", errors="ignore") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def get_cached_status(self) -> Dict[str, Any]:
        """Read cached state to avoid running slow CLI processes during search queries."""
        if os.path.isfile(self._cache_file):
            try:
                with open(self._cache_file, "r", encoding="utf-8", errors="ignore") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def save_cached_status(self, data: Dict[str, Any]):
        """Save status to fast cache file."""
        try:
            with open(self._cache_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False)
        except Exception:
            pass

    @property
    def cli_path(self) -> Optional[str]:
        if not self._cli_path or not os.path.isfile(self._cli_path):
            self._cli_path = self._find_cli_executable()
        return self._cli_path

    def is_installed(self) -> bool:
        """Check if SoundSwitch.CLI is available."""
        return self.cli_path is not None and os.path.isfile(self.cli_path)

    def _find_cli_executable(self) -> Optional[str]:
        # 1. Check in system PATH
        path_in_env = shutil.which("SoundSwitch.CLI.exe") or shutil.which("SoundSwitch.CLI")
        if path_in_env and os.path.isfile(path_in_env):
            return path_in_env

        # 2. Check in standard installation folders
        for path in self.DEFAULT_PATHS:
            if os.path.isfile(path):
                return path

        return None

    def _run_command(self, args: List[str], timeout: int = 5) -> subprocess.CompletedProcess:
        """Run a command using SoundSwitch.CLI without creating a console window."""
        if not self.is_installed():
            raise SoundSwitchNotFoundError(
                "SoundSwitch.CLI.exe não foi encontrado no sistema. "
                "Certifique-se de que o SoundSwitch está instalado em seu computador."
            )

        cmd = [self.cli_path] + args
        
        # Windows specific creation flags to prevent flashing black command prompts
        creationflags = 0
        if os.name == 'nt':
            creationflags = getattr(subprocess, 'CREATE_NO_WINDOW', 0x08000000)

        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=False, # We decode manually to handle Windows codepages (UTF-8, CP1252, etc.)
                timeout=timeout,
                creationflags=creationflags,
                startupinfo=startupinfo
            )
            return result
        except subprocess.TimeoutExpired:
            raise TimeoutError(f"SoundSwitch CLI timed out after {timeout} seconds.")

    def _decode_output(self, raw_bytes: bytes) -> str:
        """Robust multi-encoding decoding for Windows console output."""
        for encoding in ("utf-8", "utf-8-sig", "cp1252", "latin-1", "ascii"):
            try:
                return raw_bytes.decode(encoding)
            except UnicodeDecodeError:
                continue
        return raw_bytes.decode("utf-8", errors="replace")

    def _run_json_command(self, args: List[str]) -> Any:
        """Execute command and parse JSON output."""
        full_args = list(args)
        if "--json" not in full_args:
            full_args.append("--json")

        proc = self._run_command(full_args)
        stdout_str = self._decode_output(proc.stdout).strip()

        if not stdout_str:
            return None

        try:
            return json.loads(stdout_str)
        except json.JSONDecodeError:
            # Fallback if there are preamble logs before JSON
            start_bracket = stdout_str.find("{")
            start_array = stdout_str.find("[")
            start_idx = -1
            if start_bracket != -1 and start_array != -1:
                start_idx = min(start_bracket, start_array)
            elif start_bracket != -1:
                start_idx = start_bracket
            elif start_array != -1:
                start_idx = start_array

            if start_idx != -1:
                clean_json = stdout_str[start_idx:]
                return json.loads(clean_json)
            raise

    def get_status(self) -> Dict[str, Any]:
        """
        Get active profile and current audio devices.
        Returns:
            {
                "activeProfile": str or None,
                "playbackDevice": str,
                "recordingDevice": str,
                "playbackCommunicationDevice": str,
                "recordingCommunicationDevice": str
            }
        """
        data = self._run_json_command(["status"])
        return data or {}

    def get_devices(self) -> Dict[str, List[str]]:
        """
        List devices configured for switching.
        Returns:
            {
                "playbackDevices": [str, ...],
                "recordingDevices": [str, ...]
            }
        """
        data = self._run_json_command(["devices"])
        if not data:
            return {"playbackDevices": [], "recordingDevices": []}
        return {
            "playbackDevices": data.get("playbackDevices", []),
            "recordingDevices": data.get("recordingDevices", [])
        }

    def get_profiles(self) -> List[str]:
        """
        List configured audio profiles.
        Returns list of profile names.
        """
        data = self._run_json_command(["profile", "--list"])
        if isinstance(data, list):
            return data
        return []

    def get_mute_state(self) -> Dict[str, Any]:
        """
        Get microphone mute state.
        Returns:
            {
                "deviceName": str,
                "isMuted": bool
            }
        """
        data = self._run_json_command(["mute"])
        return data or {"deviceName": "Desconhecido", "isMuted": False}

    def switch_playback(self) -> bool:
        """Switch to the next playback device."""
        try:
            res = self._run_json_command(["switch", "--type", "Playback"])
            return bool(res.get("success", True) if isinstance(res, dict) else True)
        except Exception:
            return False

    def switch_recording(self) -> bool:
        """Switch to the next recording/microphone device."""
        try:
            res = self._run_json_command(["switch", "--type", "Recording"])
            return bool(res.get("success", True) if isinstance(res, dict) else True)
        except Exception:
            return False

    def switch_profile(self, profile_name: str) -> bool:
        """Activate an audio profile by name."""
        try:
            # profile --name "name"
            proc = self._run_command(["profile", "--name", profile_name])
            return proc.returncode == 0
        except Exception:
            return False

    def toggle_mute(self) -> Dict[str, Any]:
        """Toggle microphone mute status."""
        try:
            res = self._run_json_command(["mute", "--toggle"])
            return res or {}
        except Exception:
            return {}

    def set_mute(self, state: bool) -> Dict[str, Any]:
        """Set microphone mute status explicitly."""
        try:
            res = self._run_json_command(["mute", "--state", "true" if state else "false"])
            return res or {}
        except Exception:
            return {}

    def open_settings(self) -> bool:
        """Open SoundSwitch GUI settings."""
        try:
            # settings executes without blocking or with --json
            proc = self._run_command(["settings"], timeout=3)
            return proc.returncode == 0
        except Exception:
            return False
