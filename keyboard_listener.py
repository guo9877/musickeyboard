import keyboard
import threading
import time

class KeyboardListener:
    def __init__(self, callback):
        self.callback = callback
        self.running = False
        self.listener_thread = None
        self.special_keys = [
            'space', 'enter', 'backspace', 'tab', 'caps lock', 'shift', 'ctrl', 'alt',
            'left', 'right', 'up', 'down',
            'escape', 'delete', 'insert', 'home', 'end', 'page up', 'page down',
            'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10', 'f11', 'f12'
        ]
    
    def on_key_event(self, event):
        if event.event_type == keyboard.KEY_DOWN and self.running:
            key = event.name
            
            if key == ' ':
                key = 'space'
            
            self.callback(key)
    
    def start(self):
        if not self.running:
            self.running = True
            keyboard.on_press(self.on_key_event)
    
    def stop(self):
        self.running = False
        keyboard.unhook_all()
    
    def is_running(self):
        return self.running