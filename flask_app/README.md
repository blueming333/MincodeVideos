# MincodeVideos Flask版本

现代化的AI短视频生成平台，基于Flask + Bootstrap 5 + Alpine.js 重构的Web界面版本。

## 🌟 特性亮点

- 🎨 **现代化UI设计** - 参考主流AI工具的用户体验设计
- 📱 **响应式界面** - 完美适配桌面和移动设备
- 🔧 **模块化架构** - 清晰的功能分离和页面布局
- ⚡ **高性能** - 基于Flask的轻量级Web框架
- 📦 **易于分发** - 支持压缩包分发，无需复杂部署

## 🚀 快速开始

### 系统要求

- Python 3.8+ 
- FFmpeg (视频处理)
- 8GB+ RAM (推荐)
- 10GB+ 磁盘空间

### 安装步骤

#### Linux/macOS
```bash
# 1. 进入flask_app目录
cd flask_app

# 2. 运行安装脚本
bash setup.sh

# 3. 启动应用
bash start.sh
```

#### Windows
```batch
# 1. 进入flask_app目录
cd flask_app

# 2. 运行安装脚本
setup.bat

# 3. 启动应用
start.bat
```

### 访问应用

安装完成后，浏览器访问: **http://127.0.0.1:5000**

## 📖 功能模块

### 🎯 核心功能

| 功能模块 | 访问路径 | 说明 |
|---------|---------|------|
| 首页 | `/` | 功能概览和快速导航 |
| AI视频生成 | `/video/generate` | 智能视频内容生成工作流 |
| 视频混剪 | `/mix/batch` | 批量视频混剪和合并 |
| 作品展示 | `/gallery/` | 现代化的视频作品管理 |
| 自动发布 | `/publish/batch` | 多平台批量发布管理 |
| 系统配置 | `/config/` | 统一的设置管理中心 |

### 🔧 配置管理

**分类清晰的配置界面：**
- **基础设置** - 语言和通用配置
- **大语言模型** - OpenAI、Moonshot、DeepSeek等
- **语音服务** - Azure、阿里云、本地TTS
- **资源服务** - Pexels、Pixabay、Stable Diffusion
- **发布配置** - 各大视频平台自动发布

### 🎬 AI视频生成工作流

**5步骤可视化流程：**
1. **内容生成** - AI自动创建视频脚本
2. **资源获取** - 智能匹配视频素材
3. **语音合成** - 多种音色的AI配音
4. **字幕生成** - 自动生成同步字幕
5. **视频合成** - 一键生成最终视频

## 🔄 从Streamlit迁移

### 主要改进

| 方面 | Streamlit版本 | Flask版本 |
|------|--------------|-----------|
| **界面设计** | 简单但受限 | 现代化、完全自定义 |
| **用户体验** | 页面刷新频繁 | 单页面应用体验 |
| **响应速度** | 较慢 | 快速响应 |
| **功能布局** | 垂直单栏 | 灵活的多栏布局 |
| **移动适配** | 基础适配 | 完美响应式设计 |
| **扩展性** | 受框架限制 | 高度可定制 |

### 功能对应关系

| Streamlit页面 | Flask页面 | 改进点 |
|--------------|-----------|--------|
| `gui.py` | `/config/` | 分类管理，界面更清晰 |
| `01_auto_video.py` | `/video/generate` | 步骤化工作流，进度可视化 |
| `02_mix_video.py` | `/mix/batch` | 批量操作界面优化 |
| `03_auto_publish.py` | `/publish/batch` | 平台管理更直观 |
| `04_video_gallery.py` | `/gallery/` | 现代化卡片布局 |

## 📁 项目结构

```
flask_app/
├── app/                    # Flask应用
│   ├── __init__.py        # 应用工厂
│   ├── routes/            # 路由模块
│   │   ├── main.py        # 主页路由
│   │   ├── config.py      # 配置管理
│   │   ├── video.py       # 视频生成
│   │   ├── gallery.py     # 作品展示
│   │   ├── mix.py         # 视频混剪
│   │   └── publish.py     # 自动发布
│   ├── templates/         # HTML模板
│   │   ├── base.html      # 基础模板
│   │   ├── index.html     # 首页
│   │   ├── config/        # 配置页面
│   │   ├── video/         # 视频页面
│   │   └── ...
│   └── static/            # 静态资源
│       ├── css/           # 样式文件
│       └── js/            # JavaScript
├── run.py                 # 应用启动
├── requirements.txt       # Python依赖
├── setup.sh/setup.bat     # 安装脚本
└── start.sh/start.bat     # 启动脚本
```

## 🎨 设计理念

### UI/UX 设计

- **现代化视觉** - 采用流行的渐变背景和圆角设计
- **直观导航** - 左侧边栏 + 功能模块化
- **响应式布局** - 适配各种屏幕尺寸
- **交互反馈** - 丰富的动画和状态提示

### 技术栈

- **后端**: Flask + Python 3.8+
- **前端**: Bootstrap 5 + Alpine.js
- **样式**: CSS3 + 响应式设计
- **图标**: Bootstrap Icons
- **字体**: Inter + 系统字体

## 🔧 开发说明

### 本地开发

```bash
# 激活虚拟环境
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows

# 安装开发依赖
pip install -r requirements.txt

# 设置环境变量
export FLASK_DEBUG=True
export FLASK_PORT=5000

# 启动开发服务器
python run.py
```

### 添加新功能

1. **创建路由** - 在 `app/routes/` 添加新的路由文件
2. **添加模板** - 在 `app/templates/` 创建对应的HTML模板
3. **注册蓝图** - 在 `app/__init__.py` 注册新的蓝图
4. **更新导航** - 在 `base.html` 添加菜单项

### 自定义样式

- 主要样式定义在 `base.html` 的 `<style>` 标签中
- 可以在 `app/static/css/` 添加额外的CSS文件
- 支持CSS变量，便于主题定制

## 📦 部署分发

### 创建分发包

```bash
# 1. 确保所有依赖已安装
pip freeze > requirements.txt

# 2. 创建分发目录
mkdir MincodeVideos-Flask-v2.0.0

# 3. 复制必要文件
cp -r flask_app/ MincodeVideos-Flask-v2.0.0/
cp -r services/ config/ tools/ MincodeVideos-Flask-v2.0.0/

# 4. 创建压缩包
tar -czf MincodeVideos-Flask-v2.0.0.tar.gz MincodeVideos-Flask-v2.0.0/
```

### 用户安装

用户只需:
1. 解压压缩包
2. 运行 `setup.sh` (Linux/macOS) 或 `setup.bat` (Windows)
3. 运行 `start.sh` 或 `start.bat`
4. 浏览器访问 http://127.0.0.1:5000

## 🤝 技术支持

### 常见问题

**Q: 端口被占用怎么办？**  
A: 修改 `run.py` 中的 `FLASK_PORT` 环境变量

**Q: 如何修改界面主题？**  
A: 修改 `base.html` 中的CSS变量 `--primary-color` 等

**Q: 如何添加新的语音服务？**  
A: 在 `config.py` 路由和对应模板中添加新的服务配置

**Q: 能否与原Streamlit版本共存？**  
A: 可以，Flask版本在独立的 `flask_app/` 目录中

### 版本信息

- **当前版本**: v2.0.0
- **基于原版**: MoneyPrinterPlus Streamlit (原作者项目)
- **重构日期**: 2024年8月
- **兼容性**: Python 3.8+ / 跨平台

---

## 📄 许可证

继承原项目的许可证条款。个人和教育用途免费，商业用途需要授权。

**开发团队**: 程序那些事  
**原作者项目地址**: https://github.com/ddean2009/MoneyPrinterPlus  
**技术支持**: flydean@163.com