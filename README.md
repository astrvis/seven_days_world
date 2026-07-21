# 阿星的小助手

一款基于 Flet 框架开发的《七日世界》游戏辅助工具，提供自动化钓鱼、徽章挑战和忘却副本功能。

## 功能特性

### 🎣 钓鱼模块
- 自动识别鱼竿状态和鱼类型
- 支持多种鱼竿键位配置
- 自动处理鱼的拉扯力度
- 实时显示钓鱼成功率

### 🛡️ 徽章模块
- 自动完成徽章挑战
- 支持普通徽章和混沌试炼
- 自动领取奖励
- 多页面徽章识别

### 🏰 忘却模块
- 自动挑战忘却副本
- 自动拾取宝箱奖励
- 支持自动使用食物恢复体力
- 自动跳过动画和重新挑战

## 技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.11+ | 开发语言 |
| Flet | 0.85.3+ | 桌面 UI 框架 |
| RapidOCR | 3.9.1+ | OCR 文字识别 |
| OpenCV | 5.0+ | 图像模板匹配 |
| mss | 10.2+ | 屏幕截图 |
| PyDirectInput | 1.0+ | 模拟键盘鼠标操作 |
| PyTorch | 2.13+ | OCR 推理引擎 |

## 前置要求

- **操作系统**: Windows 10/11
- **屏幕分辨率**: 1920x1080（所有识别区域坐标基于此分辨率）
- **游戏窗口**: 游戏标题必须为「七日世界」
- **Python**: 3.11 及以上版本
- **CUDA**: 推荐安装 NVIDIA CUDA 12.6（用于加速 OCR 推理）

## 安装指南

### 使用 uv（推荐）

```bash
# 安装依赖
uv sync

# 运行程序
uv run python src/main.py
```

### 使用 pip

```bash
# 创建虚拟环境
python -m venv .venv
.venv\Scripts\activate

# 安装依赖
pip install -e .

# 运行程序
python src/main.py
```

## 使用说明

1. 确保游戏《七日世界》已启动并处于窗口化或全屏模式
2. 运行程序，等待 OCR 初始化完成（约 2-3 分钟）
3. 根据需要选择「钓鱼」「徽章」「忘却」标签页
4. 配置相应参数后点击开始按钮

### 注意事项

- 运行期间请勿遮挡游戏窗口
- 切换标签页会自动停止当前任务
- OCR 初始化可能需要较长时间，请耐心等待

## 配置文件

`settings.json` 包含可自定义的运行参数：

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| GAME_WINDOW_KEY | string | 七日世界 | 游戏窗口名称 |
| KEYWORD_FISH | array | ['4','5','6','7','8'] | 鱼竿键位 |
| MAX_THRESHOLD | float | 1.4 | 钓鱼最大压力阈值 |
| MIN_THRESHOLD | float | 1.0 | 钓鱼最小压力阈值 |
| LEVEL_TYPE | string | ordinary | 徽章类型（ordinary/chaos） |
| FOOD_TAGS | array | ['8','9','0','-','7'] | 食物快捷键 |
| FOOD_INTERVAL | int | 60 | 自动进食间隔（秒） |
| IS_FOOD | bool | true | 是否启用自动进食 |
| WQZZ_TYPE | int | 1 | 忘却副本类型 |

## 项目结构

```
seven_days_world/
├── src/
│   ├── ui/              # UI 组件
│   │   ├── layout.py    # 主布局
│   │   ├── fish.py      # 钓鱼页面
│   │   ├── badge.py     # 徽章页面
│   │   ├── wqzz.py      # 忘却页面
│   │   └── log_box.py   # 日志组件
│   ├── tasks/           # 任务逻辑
│   │   ├── fish_task.py
│   │   ├── badge_task.py
│   │   └── wqzz_task.py
│   ├── utils/           # 工具函数
│   │   ├── rapid_ocr.py # OCR 识别
│   │   ├── template_match.py # 模板匹配
│   │   ├── mouse_operate.py  # 鼠标操作
│   │   ├── screenshot.py     # 屏幕截图
│   │   ├── window_control.py # 窗口控制
│   │   ├── setting.py   # 配置加载
│   │   ├── consts.py    # 全局状态
│   │   └── error_log.py # 错误日志
│   ├── res/             # 资源图片
│   ├── public/          # 静态资源
│   ├── config.py        # 默认配置
│   ├── settings.json    # 运行时配置
│   └── main.py          # 入口文件
├── build.spec           # PyInstaller 打包配置
├── pyproject.toml       # 项目依赖配置
└── uv.lock              # uv 依赖锁文件
```

## 打包发布

使用 PyInstaller 打包为可执行文件：

```bash
# 安装打包依赖
uv add pyinstaller flet-desktop

# 执行打包
pyinstaller build.spec

# 打包产物位于 dist/阿星的小助手/ 目录
# 分发时需包含整个目录
```

## 免责声明

⚠️ **重要提示**

本工具仅供学习和研究目的使用。使用游戏辅助工具可能违反游戏服务条款，请谨慎使用。作者不对因使用本工具导致的任何游戏账号问题或其他后果承担责任。

使用本工具即表示您同意自行承担所有风险。

## 许可证

MIT License