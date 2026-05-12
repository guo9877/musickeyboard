import os
import ctypes
import threading
import time

class AudioPlayer:
    def __init__(self):
        self.volume = 0.7
        self.players = {}
        self.last_error = None
        self.winmm = ctypes.WinDLL('winmm.dll')
        self._stop_event = threading.Event()
        self._play_thread = None
    
    def set_volume(self, volume):
        self.volume = max(0.0, min(1.0, volume))
    
    def get_last_error(self):
        return self.last_error
    
    def play_sound(self, key):
        self.last_error = None
        if key not in self.players:
            self.last_error = f"按键未配置: {key}"
            print(self.last_error)
            return False
        
        file_path = self.players[key]
        if not os.path.exists(file_path):
            self.last_error = f"音频文件不存在: {file_path}"
            print(self.last_error)
            return False
        
        self._stop_playback()
        
        self._stop_event.clear()
        self._play_thread = threading.Thread(target=self._play_audio, args=(file_path,))
        self._play_thread.daemon = True
        self._play_thread.start()
        return True
    
    def _stop_playback(self):
        self._stop_event.set()
        
        self.winmm.mciSendStringA(b'stop sound_player', None, 0, 0)
        self.winmm.mciSendStringA(b'close sound_player', None, 0, 0)
        
        if self._play_thread and self._play_thread.is_alive():
            self._play_thread.join(timeout=0.5)
    
    def _play_audio(self, file_path):
        alias = "sound_player"
        
        try:
            file_path = os.path.abspath(file_path).replace('/', '\\')
            
            open_cmd = f'open "{file_path}" type MPEGVideo alias {alias}'.encode('gbk')
            result = self.winmm.mciSendStringA(open_cmd, None, 0, 0)
            if result != 0:
                self.last_error = f"打开文件失败: {result}"
                print(self.last_error)
                return
            
            volume = int(self.volume * 1000)
            vol_cmd = f'setaudio {alias} volume to {volume}'.encode('gbk')
            self.winmm.mciSendStringA(vol_cmd, None, 0, 0)
            
            play_cmd = f'play {alias}'.encode('gbk')
            result = self.winmm.mciSendStringA(play_cmd, None, 0, 0)
            if result != 0:
                self.last_error = f"播放失败: {result}"
                print(self.last_error)
                self.winmm.mciSendStringA(b'close sound_player', None, 0, 0)
                return
            
            while not self._stop_event.is_set():
                buf = ctypes.create_string_buffer(16)
                status_cmd = f'status {alias} mode'.encode('gbk')
                self.winmm.mciSendStringA(status_cmd, buf, 16, 0)
                mode = buf.value.decode('gbk', errors='ignore').strip()
                if mode != 'playing':
                    break
                time.sleep(0.05)
            
            self.winmm.mciSendStringA(b'close sound_player', None, 0, 0)
            
        except Exception as e:
            self.last_error = f"播放错误: {str(e)}"
            print(self.last_error)
            self.winmm.mciSendStringA(b'close sound_player', None, 0, 0)
    
    def load_sound(self, key, file_path):
        if os.path.exists(file_path):
            self.players[key] = file_path
            return True, "加载成功"
        else:
            return False, f"文件不存在: {file_path}"
    
    def load_all_sounds(self, key_mappings):
        self.players.clear()
        missing_files = []
        for key, file_path in key_mappings.items():
            if os.path.exists(file_path):
                self.players[key] = file_path
            else:
                missing_files.append(file_path)
        
        if missing_files:
            print(f"警告: 以下音频文件不存在: {', '.join(missing_files)}")
        
        return missing_files
    
    def stop_all(self):
        self._stop_playback()
    
    def quit(self):
        self._stop_playback()