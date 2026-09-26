# -*- coding: utf-8 -*-
import json

class FlowLauncherAPI:
    """
    Public APIs provided by Flow.Launcher for plugins.
    Prints JSON-RPC actions to stdout.
    """

    @classmethod
    def change_query(cls, query: str, requery: bool = False):
        """
        Change Flow Launcher's search box query.
        """
        print(json.dumps({
            "method": "Flow.Launcher.ChangeQuery",
            "parameters": [query, requery]
        }, ensure_ascii=False))

    @classmethod
    def shell_run(cls, cmd: str):
        """
        Run shell command via Flow Launcher.
        """
        print(json.dumps({
            "method": "Flow.Launcher.ShellRun",
            "parameters": [cmd]
        }, ensure_ascii=False))

    @classmethod
    def close_app(cls):
        """
        Close Flow Launcher window.
        """
        print(json.dumps({
            "method": "Flow.Launcher.CloseApp",
            "parameters": []
        }, ensure_ascii=False))

    @classmethod
    def hide_app(cls):
        """
        Hide Flow Launcher window.
        """
        print(json.dumps({
            "method": "Flow.Launcher.HideApp",
            "parameters": []
        }, ensure_ascii=False))

    @classmethod
    def show_app(cls):
        """
        Show Flow Launcher window.
        """
        print(json.dumps({
            "method": "Flow.Launcher.ShowApp",
            "parameters": []
        }, ensure_ascii=False))

    @classmethod
    def show_msg(cls, title: str, sub_title: str, ico_path: str = ""):
        """
        Display a notification message box in Flow Launcher / Windows.
        """
        print(json.dumps({
            "method": "Flow.Launcher.ShowMsg",
            "parameters": [title, sub_title, ico_path]
        }, ensure_ascii=False))

    @classmethod
    def open_setting_dialog(cls):
        """
        Open Flow Launcher settings dialog.
        """
        print(json.dumps({
            "method": "Flow.Launcher.OpenSettingDialog",
            "parameters": []
        }, ensure_ascii=False))

    @classmethod
    def start_loadingbar(cls):
        """
        Start loading bar animation.
        """
        print(json.dumps({
            "method": "Flow.Launcher.StartLoadingBar",
            "parameters": []
        }, ensure_ascii=False))

    @classmethod
    def stop_loadingbar(cls):
        """
        Stop loading bar animation.
        """
        print(json.dumps({
            "method": "Flow.Launcher.StopLoadingBar",
            "parameters": []
        }, ensure_ascii=False))

    @classmethod
    def reload_plugins(cls):
        """
        Reload all Flow Launcher plugins.
        """
        print(json.dumps({
            "method": "Flow.Launcher.ReloadPlugins",
            "parameters": []
        }, ensure_ascii=False))
