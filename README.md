# 音乐键盘 (MusicKeyboard)

一款桌面端键盘音效软件，按下键盘按键即可播放对应的音频文件，支持分组管理和批量配置。

## 功能特性

- **键盘触发音效**：按下任意键盘按键播放对应的 MP3/WAV/OGG 音频
- **分组管理**：支持创建多个音效分组（如钢琴、鼓点、音效），通过标签页切换
- **批量导入**：一次性导入多个音频文件，自动分配按键
- **音量调节**：实时调整播放音量
- **单音频播放**：同一时间只播放一个音效，新按键自动停止之前的播放

## 支持的按键

- 字母键：`a-z`
- 数字键：`0-9`
- 符号键：`` ` ~ ! @ # $ % ^ & * ( ) _ + - = [ ] { } | ; ' : " , . / < > ? ``
- 功能键：`space`, `enter`, `backspace`, `tab`, `caps lock`, `shift`, `ctrl`, `alt`
- 方向键：`left`, `right`, `up`, `down`
- 控制键：`escape`, `delete`, `insert`, `home`, `end`, `page up`, `page down`
- F键：`f1` - `f12`

## 快速开始

### 方式一：直接运行（推荐）

双击根目录下的 `MusicKeyboard.exe` 即可启动软件。

### 方式二：源码运行

```bash
# 安装依赖
pip install -r requirements.txt

# 运行程序
python main.py
```

## 使用说明

### 1. 配置音效

1. 选择左侧分组标签页（或创建新分组）
2. 在「按键」输入框中输入要绑定的按键名称
3. 点击「浏览」选择音频文件
4. 点击「添加/修改」保存配置

### 2. 批量导入

1. 切换到目标分组
2. 点击「批量导入」按钮
3. 选择多个音频文件
4. 系统自动按顺序分配可用按键

### 3. 开始播放

1. 点击「开始监听」按钮
2. 按下已配置的键盘按键即可播放对应音效
3. 点击「停止监听」关闭键盘监听

### 4. 分组管理

- **添加分组**：点击「添加分组」按钮，输入分组名称
- **重命名分组**：选中分组后点击「重命名分组」
- **删除分组**：选中分组后点击「删除分组」（至少保留一个分组）

## 项目结构

```
musickeyboard/
├── MusicKeyboard.exe    # 可执行文件
├── main.py              # 主程序入口
├── audio_player.py      # 音频播放模块
├── keyboard_listener.py # 键盘监听模块
├── config_manager.py    # 配置管理模块
├── config.json          # 配置文件（自动创建）
├── requirements.txt     # Python依赖
├── README.md            # 本文件
└── sounds/              # 音效文件目录（示例）
```

## 配置文件

软件会自动创建 `config.json` 文件保存配置，格式如下：

```json
{
    "groups": {
        "钢琴": {
            "key_mappings": {
                "a": "sounds/piano_c4.mp3",
                "s": "sounds/piano_d4.mp3"
            }
        }
    },
    "active_group": "钢琴",
    "volume": 0.7,
    "auto_start": false
}
```

## 注意事项

1. **管理员权限**：首次运行建议以管理员身份运行，以确保键盘监听功能正常工作
2. **音频格式**：支持 MP3、WAV、OGG 格式
3. **按键冲突**：避免将系统快捷键（如 Ctrl+C）配置为音效按键
4. **配置备份**：`config.json` 包含所有配置，建议定期备份

## 打包说明

如需重新打包可执行文件：

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name MusicKeyboard main.py
```

打包后的文件位于 `dist/MusicKeyboard.exe`。

## 技术栈

- Python 3.x
- Tkinter（GUI界面）
- keyboard（键盘监听）
- winmm.dll（音频播放）

## 许可证

MIT License