import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import os
import sys
from audio_player import AudioPlayer
from keyboard_listener import KeyboardListener
from config_manager import ConfigManager

class MusicKeyboardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("音乐键盘")
        self.root.geometry("850x600")
        self.root.resizable(True, True)
        
        self.config_manager = ConfigManager()
        self.audio_player = AudioPlayer()
        self.keyboard_listener = KeyboardListener(self.on_key_press)
        
        self.is_running = False
        self.selected_key = None
        
        self.init_ui()
        self.load_sounds()
    
    def init_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=5)
        
        self.start_button = ttk.Button(control_frame, text="开始监听", command=self.toggle_listener)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.volume_label = ttk.Label(control_frame, text="音量:")
        self.volume_label.pack(side=tk.LEFT, padx=5)
        
        self.volume_slider = ttk.Scale(control_frame, from_=0.0, to=1.0, value=self.config_manager.get_volume(), 
                                       command=self.on_volume_change)
        self.volume_slider.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        self.volume_value = ttk.Label(control_frame, text=f"{int(self.config_manager.get_volume() * 100)}%")
        self.volume_value.pack(side=tk.LEFT, padx=5)
        
        group_frame = ttk.LabelFrame(main_frame, text="音效分组", padding="10")
        group_frame.pack(fill=tk.X, pady=5)
        
        self.group_notebook = ttk.Notebook(group_frame)
        self.group_notebook.pack(fill=tk.BOTH, expand=True)
        
        self.group_tabs = {}
        self.group_mapping_lists = {}
        
        for group_name in self.config_manager.get_group_names():
            self.add_group_tab(group_name)
        
        group_buttons_frame = ttk.Frame(group_frame)
        group_buttons_frame.pack(fill=tk.X, pady=5)
        
        self.add_group_btn = ttk.Button(group_buttons_frame, text="添加分组", command=self.add_group)
        self.add_group_btn.pack(side=tk.LEFT, padx=5)
        
        self.rename_group_btn = ttk.Button(group_buttons_frame, text="重命名分组", command=self.rename_group)
        self.rename_group_btn.pack(side=tk.LEFT, padx=5)
        
        self.delete_group_btn = ttk.Button(group_buttons_frame, text="删除分组", command=self.delete_group)
        self.delete_group_btn.pack(side=tk.LEFT, padx=5)
        
        self.group_notebook.bind('<<NotebookTabChanged>>', self.on_group_switch)
        
        config_frame = ttk.LabelFrame(main_frame, text="按键配置", padding="10")
        config_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        key_frame = ttk.Frame(config_frame)
        key_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(key_frame, text="按键:").pack(side=tk.LEFT, padx=5)
        self.key_entry = ttk.Entry(key_frame, width=10)
        self.key_entry.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(key_frame, text="音频文件:").pack(side=tk.LEFT, padx=5)
        self.file_entry = ttk.Entry(key_frame, width=50)
        self.file_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        self.browse_button = ttk.Button(key_frame, text="浏览", command=self.browse_file)
        self.browse_button.pack(side=tk.LEFT, padx=5)
        
        action_frame = ttk.Frame(config_frame)
        action_frame.pack(fill=tk.X, pady=5)
        
        self.add_button = ttk.Button(action_frame, text="添加/修改", command=self.add_mapping)
        self.add_button.pack(side=tk.LEFT, padx=5)
        
        self.remove_button = ttk.Button(action_frame, text="删除选中", command=self.remove_mapping)
        self.remove_button.pack(side=tk.LEFT, padx=5)
        
        self.batch_import_btn = ttk.Button(action_frame, text="批量导入", command=self.batch_import)
        self.batch_import_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_all_btn = ttk.Button(action_frame, text="清空当前分组", command=self.clear_all_mappings)
        self.clear_all_btn.pack(side=tk.LEFT, padx=5)
        
        self.listbox_frame = ttk.Frame(config_frame)
        self.listbox_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.mapping_list = tk.Listbox(self.listbox_frame, selectmode=tk.MULTIPLE)
        self.mapping_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(self.listbox_frame, orient=tk.VERTICAL, command=self.mapping_list.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.mapping_list.config(yscrollcommand=scrollbar.set)
        
        self.mapping_list.bind('<<ListboxSelect>>', self.on_list_select)
        
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=5)
        
        self.status_label = ttk.Label(status_frame, text="状态: 已停止", foreground="red")
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        self.group_label = ttk.Label(status_frame, text=f"当前分组: {self.config_manager.get_active_group()}")
        self.group_label.pack(side=tk.RIGHT, padx=5)
        
        self.load_mapping_list()
    
    def add_group_tab(self, group_name):
        tab_frame = ttk.Frame(self.group_notebook)
        self.group_notebook.add(tab_frame, text=group_name)
        
        listbox = tk.Listbox(tab_frame, selectmode=tk.MULTIPLE)
        listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.group_tabs[group_name] = tab_frame
        self.group_mapping_lists[group_name] = listbox
        
        self.update_group_tab_content(group_name)
    
    def update_group_tab_content(self, group_name):
        if group_name not in self.group_mapping_lists:
            return
        
        listbox = self.group_mapping_lists[group_name]
        listbox.delete(0, tk.END)
        
        mappings = self.config_manager.get_key_mappings(group_name)
        for key, path in mappings.items():
            display_key = key if key != 'space' else 'Space'
            listbox.insert(tk.END, f"{display_key} -> {os.path.basename(path)}")
    
    def load_sounds(self):
        mappings = self.config_manager.get_key_mappings()
        self.audio_player.set_volume(self.config_manager.get_volume())
        self.audio_player.load_all_sounds(mappings)
    
    def load_mapping_list(self):
        self.mapping_list.delete(0, tk.END)
        mappings = self.config_manager.get_key_mappings()
        for key, path in mappings.items():
            display_key = key if key != 'space' else 'Space'
            self.mapping_list.insert(tk.END, f"{display_key} -> {os.path.basename(path)}")
        
        for group_name in self.config_manager.get_group_names():
            self.update_group_tab_content(group_name)
    
    def browse_file(self):
        file_path = filedialog.askopenfilename(
            title="选择音频文件",
            filetypes=[("音频文件", "*.mp3 *.wav *.ogg"), ("所有文件", "*.*")]
        )
        if file_path:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, file_path)
    
    def is_valid_key(self, key):
        if len(key) == 1:
            return True
        
        valid_special_keys = [
            'space', 'enter', 'backspace', 'tab', 'caps lock', 'shift', 'ctrl', 'alt',
            'left', 'right', 'up', 'down',
            'escape', 'delete', 'insert', 'home', 'end', 'page up', 'page down',
            'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10', 'f11', 'f12'
        ]
        return key in valid_special_keys
    
    def add_mapping(self):
        key = self.key_entry.get().strip().lower()
        file_path = self.file_entry.get().strip()
        
        if not key:
            messagebox.showwarning("警告", "请输入按键")
            return
        
        if not self.is_valid_key(key):
            messagebox.showwarning("警告", "无效的按键名称。支持的按键包括：\n- 单个字符：a-z, 0-9, `~!@#$%^&*()_+-=[]{}|;':\",./<>?\n- 特殊按键：space, enter, backspace, tab, caps lock, shift, ctrl, alt, left, right, up, down, escape, delete, insert, home, end, page up, page down, f1-f12")
            return
        
        if not file_path:
            messagebox.showwarning("警告", "请选择音频文件")
            return
        
        if not os.path.exists(file_path):
            messagebox.showwarning("警告", "文件不存在")
            return
        
        active_group = self.config_manager.get_active_group()
        if self.config_manager.set_key_mapping(key, file_path, active_group):
            self.audio_player.load_sound(key, file_path)
            self.load_mapping_list()
            self.key_entry.delete(0, tk.END)
            self.file_entry.delete(0, tk.END)
            messagebox.showinfo("成功", "配置已保存")
        else:
            messagebox.showerror("错误", "保存失败")
    
    def remove_mapping(self):
        selections = self.mapping_list.curselection()
        if not selections:
            messagebox.showwarning("警告", "请选中要删除的配置")
            return
        
        active_group = self.config_manager.get_active_group()
        mappings = self.config_manager.get_key_mappings(active_group)
        keys = list(mappings.keys())
        
        for index in reversed(selections):
            if index < len(keys):
                key = keys[index]
                self.config_manager.remove_key_mapping(key, active_group)
                if key in self.audio_player.players:
                    del self.audio_player.players[key]
        
        self.load_mapping_list()
        messagebox.showinfo("成功", "选中配置已删除")
    
    def clear_all_mappings(self):
        active_group = self.config_manager.get_active_group()
        if messagebox.askyesno("确认", f"确定要清空分组 '{active_group}' 的所有配置吗？"):
            self.config_manager.clear_all_mappings(active_group)
            self.audio_player.players.clear()
            self.load_mapping_list()
            messagebox.showinfo("成功", f"已清空分组 '{active_group}' 的所有配置")
    
    def get_all_keys(self):
        all_keys = [
            'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
            'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
            '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
            'space', 'enter', 'backspace', 'tab', 'caps lock', 'shift', 'ctrl', 'alt',
            'left', 'right', 'up', 'down',
            'escape', 'delete', 'insert', 'home', 'end', 'page up', 'page down',
            'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10', 'f11', 'f12',
            '`', '-', '=', '[', ']', '\\', ';', "'", ',', '.', '/',
            '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '_', '+',
            '{', '}', '|', ':', '"', '<', '>', '?'
        ]
        return all_keys
    
    def batch_import(self):
        files = filedialog.askopenfilenames(
            title="批量选择音频文件",
            filetypes=[("音频文件", "*.mp3 *.wav *.ogg"), ("所有文件", "*.*")]
        )
        
        if not files:
            return
        
        active_group = self.config_manager.get_active_group()
        key_order = self.get_all_keys()
        mappings = {}
        used_keys = set(self.config_manager.get_key_mappings(active_group).keys())
        
        available_keys = [k for k in key_order if k not in used_keys]
        
        for i, file_path in enumerate(files):
            if i < len(available_keys):
                key = available_keys[i]
                mappings[key] = file_path
            else:
                break
        
        if mappings:
            self.config_manager.batch_import_mappings(mappings, active_group)
            for key, file_path in mappings.items():
                self.audio_player.load_sound(key, file_path)
            self.load_mapping_list()
            messagebox.showinfo("成功", f"批量导入 {len(mappings)} 个音频文件到分组 '{active_group}'")
        else:
            messagebox.showwarning("警告", "没有可用的按键分配")
    
    def on_list_select(self, event):
        selections = self.mapping_list.curselection()
        if selections:
            index = selections[0]
            active_group = self.config_manager.get_active_group()
            mappings = self.config_manager.get_key_mappings(active_group)
            keys = list(mappings.keys())
            if index < len(keys):
                self.selected_key = keys[index]
                self.key_entry.delete(0, tk.END)
                self.key_entry.insert(0, self.selected_key)
                self.file_entry.delete(0, tk.END)
                self.file_entry.insert(0, mappings[self.selected_key])
    
    def on_group_switch(self, event):
        current_tab = self.group_notebook.index(self.group_notebook.select())
        group_names = self.config_manager.get_group_names()
        
        if current_tab < len(group_names):
            group_name = group_names[current_tab]
            if group_name != self.config_manager.get_active_group():
                self.config_manager.set_active_group(group_name)
                self.group_label.config(text=f"当前分组: {group_name}")
                self.load_mapping_list()
                self.load_sounds()
    
    def add_group(self):
        group_name = simpledialog.askstring("添加分组", "请输入分组名称:")
        if group_name and group_name.strip():
            group_name = group_name.strip()
            if self.config_manager.add_group(group_name):
                self.add_group_tab(group_name)
                messagebox.showinfo("成功", f"分组 '{group_name}' 已添加")
            else:
                messagebox.showwarning("警告", "分组名称已存在")
    
    def rename_group(self):
        current_tab = self.group_notebook.index(self.group_notebook.select())
        group_names = self.config_manager.get_group_names()
        
        if current_tab >= len(group_names):
            messagebox.showwarning("警告", "请选择一个分组")
            return
        
        old_name = group_names[current_tab]
        
        new_name = simpledialog.askstring("重命名分组", "请输入新名称:", initialvalue=old_name)
        if new_name and new_name.strip() and new_name != old_name:
            new_name = new_name.strip()
            if self.config_manager.rename_group(old_name, new_name):
                self.group_notebook.tab(current_tab, text=new_name)
                self.group_tabs[new_name] = self.group_tabs.pop(old_name)
                self.group_mapping_lists[new_name] = self.group_mapping_lists.pop(old_name)
                self.group_label.config(text=f"当前分组: {self.config_manager.get_active_group()}")
                messagebox.showinfo("成功", f"分组已重命名为 '{new_name}'")
            else:
                messagebox.showwarning("警告", "分组名称已存在")
    
    def delete_group(self):
        current_tab = self.group_notebook.index(self.group_notebook.select())
        group_names = self.config_manager.get_group_names()
        
        if current_tab >= len(group_names):
            messagebox.showwarning("警告", "请选择一个分组")
            return
        
        group_name = group_names[current_tab]
        
        if len(group_names) <= 1:
            messagebox.showwarning("警告", "至少保留一个分组")
            return
        
        if messagebox.askyesno("确认", f"确定要删除分组 '{group_name}' 吗？该分组下的所有配置将被删除。"):
            if self.config_manager.remove_group(group_name):
                self.group_notebook.forget(current_tab)
                del self.group_tabs[group_name]
                del self.group_mapping_lists[group_name]
                self.group_label.config(text=f"当前分组: {self.config_manager.get_active_group()}")
                self.load_mapping_list()
                self.load_sounds()
                messagebox.showinfo("成功", f"分组 '{group_name}' 已删除")
    
    def on_volume_change(self, value):
        volume = float(value)
        self.config_manager.set_volume(volume)
        self.audio_player.set_volume(volume)
        self.volume_value.config(text=f"{int(volume * 100)}%")
    
    def on_key_press(self, key):
        self.audio_player.play_sound(key)
    
    def toggle_listener(self):
        if self.is_running:
            self.keyboard_listener.stop()
            self.is_running = False
            self.start_button.config(text="开始监听")
            self.status_label.config(text="状态: 已停止", foreground="red")
        else:
            try:
                self.keyboard_listener.start()
                self.is_running = True
                self.start_button.config(text="停止监听")
                self.status_label.config(text="状态: 运行中", foreground="green")
            except Exception as e:
                messagebox.showerror("错误", f"启动失败: {e}")
    
    def on_close(self):
        self.keyboard_listener.stop()
        self.audio_player.quit()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = MusicKeyboardApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()