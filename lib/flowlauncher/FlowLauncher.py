# -*- coding: utf-8 -*-
import inspect
import sys
import json

if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass


class FlowLauncher:
    """
    Flow.Launcher Python plugin base class.
    Handles JSON-RPC communication between Flow Launcher and Python plugin.
    """

    def __init__(self):
        # Default JSON-RPC request for fallback or direct execution
        self.rpc_request = {'method': 'query', 'parameters': ['']}
        self.debugMessage = ""

        if len(sys.argv) > 1:
            try:
                self.rpc_request = json.loads(sys.argv[1])
            except Exception as e:
                self.debug(f"Failed to parse JSON-RPC args: {e}")

        request_method_name = self.rpc_request.get("method", "query")
        request_parameters = self.rpc_request.get("parameters", [])

        methods = dict(inspect.getmembers(self, predicate=inspect.ismethod))
        
        if request_method_name in methods:
            request_method = methods[request_method_name]
            results = request_method(*request_parameters)

            if request_method_name in ("query", "context_menu"):
                response = {
                    "result": results if results is not None else [],
                    "debugMessage": self.debugMessage
                }
                print(json.dumps(response, ensure_ascii=False))
        else:
            self.debug(f"Method '{request_method_name}' not found")
            if request_method_name in ("query", "context_menu"):
                print(json.dumps({"result": [], "debugMessage": self.debugMessage}))

    def query(self, param: str = '') -> list:
        """
        Subclasses should override this method to handle user search queries.
        """
        return []

    def context_menu(self, data) -> list:
        """
        Optional context menu entries for a selected result.
        """
        return []

    def debug(self, msg: str):
        """
        Sets a debug message to be sent to Flow Launcher.
        """
        self.debugMessage = str(msg)
