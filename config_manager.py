import json
import os

class ConfigManager:
    def __init__(self, config_path='config.json'):
        self.config_path = config_path
        self.default_config = {
            "groups": {
                "默认": {"key_mappings": {}}
            },
            "active_group": "默认",
            "volume": 0.7,
            "auto_start": False
        }
        self.config = self.load_config()
    
    def load_config(self):
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return self.default_config.copy()
        except Exception as e:
            print(f"Error loading config: {e}")
            return self.default_config.copy()
    
    def save_config(self):
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def get_groups(self):
        return self.config.get('groups', {})
    
    def get_group_names(self):
        return list(self.config.get('groups', {}).keys())
    
    def get_active_group(self):
        return self.config.get('active_group', '默认')
    
    def set_active_group(self, group_name):
        if group_name in self.config.get('groups', {}):
            self.config['active_group'] = group_name
            return self.save_config()
        return False
    
    def add_group(self, group_name):
        if group_name not in self.config.get('groups', {}):
            self.config['groups'][group_name] = {"key_mappings": {}}
            return self.save_config()
        return False
    
    def remove_group(self, group_name):
        if group_name in self.config.get('groups', {}):
            del self.config['groups'][group_name]
            if self.config.get('active_group') == group_name:
                groups = list(self.config['groups'].keys())
                self.config['active_group'] = groups[0] if groups else '默认'
            return self.save_config()
        return False
    
    def rename_group(self, old_name, new_name):
        if old_name in self.config.get('groups', {}) and new_name not in self.config['groups']:
            self.config['groups'][new_name] = self.config['groups'][old_name]
            del self.config['groups'][old_name]
            if self.config.get('active_group') == old_name:
                self.config['active_group'] = new_name
            return self.save_config()
        return False
    
    def get_key_mappings(self, group_name=None):
        if group_name is None:
            group_name = self.get_active_group()
        return self.config.get('groups', {}).get(group_name, {}).get('key_mappings', {})
    
    def set_key_mapping(self, key, file_path, group_name=None):
        if group_name is None:
            group_name = self.get_active_group()
        
        if group_name not in self.config.get('groups', {}):
            return False
        
        self.config['groups'][group_name]['key_mappings'][key] = file_path
        return self.save_config()
    
    def remove_key_mapping(self, key, group_name=None):
        if group_name is None:
            group_name = self.get_active_group()
        
        group = self.config.get('groups', {}).get(group_name, {})
        key_mappings = group.get('key_mappings', {})
        
        if key in key_mappings:
            del key_mappings[key]
            return self.save_config()
        return False
    
    def batch_import_mappings(self, mappings, group_name=None):
        if group_name is None:
            group_name = self.get_active_group()
        
        if group_name not in self.config.get('groups', {}):
            return False
        
        key_mappings = self.config['groups'][group_name]['key_mappings']
        key_mappings.update(mappings)
        return self.save_config()
    
    def clear_all_mappings(self, group_name=None):
        if group_name is None:
            group_name = self.get_active_group()
        
        if group_name in self.config.get('groups', {}):
            self.config['groups'][group_name]['key_mappings'] = {}
            return self.save_config()
        return False
    
    def get_volume(self):
        return self.config.get('volume', 0.7)
    
    def set_volume(self, volume):
        self.config['volume'] = max(0.0, min(1.0, volume))
        return self.save_config()
    
    def get_auto_start(self):
        return self.config.get('auto_start', False)
    
    def set_auto_start(self, auto_start):
        self.config['auto_start'] = auto_start
        return self.save_config()