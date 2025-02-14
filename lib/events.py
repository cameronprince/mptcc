"""
MicroPython Tesla Coil Controller (MPTCC)
by Cameron Prince
teslauniverse.com

lib/events.py
The events system.
"""

class Events:
    def __init__(self):
        self.listeners = {}

    def subscribe(self, event, callback):
        if event not in self.listeners:
            self.listeners[event] = []
        self.listeners[event].append(callback)

    def emit(self, event, *args, **kwargs):
        print('emit')
        if event in self.listeners:
            for callback in self.listeners[event]:
                callback(*args, **kwargs)

# Global event system.
events = Events()
