# Carousell 自动上传工具

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

这是一个用于 Carousell 平台的自动化商品上传工具，支持批量上传商品图片和自动填写商品信息。

## ✨ 核心特性

### 🚀 自动化功能
- 🚀 **自动启动指纹浏览器** - 支持多账号管理
- 📁 **批量上传图片文件** - 支持多种图片格式
- 📝 **自动填写商品信息** - 智能表单填写
- 🔄 **商品状态管理** - 自动激活和发布
- 🎯 **命令行接口支持** - 简单易用的CLI

### 🌍 多地域支持
- 🇭🇰 **香港 (HK)** - 支持香港Carousell平台
- 🇸🇬 **新加坡 (SG)** - 支持新加坡Carousell平台  
- 🇲🇾 **马来西亚 (MY)** - 支持马来西亚Carousell平台

### 🏗️ 架构设计
- 🏗️ **模块化架构** - 按地域和类目组织代码
- 🔧 **工厂模式** - 动态创建上传器实例
- 📦 **清晰依赖管理** - 完整的依赖体系
- 🛡️ **错误处理** - 完善的异常处理机制
- 📊 **日志系统** - 详细的运行日志

### 📊 数据处理
- 📊 **Excel批量管理** - 支持Excel文件批量上传
- 👥 **多账号串行上传** - 支持多账号顺序上传
- 🔗 **动态BrowserID映射** - 自动映射浏览器ID
- 📈 **上传结果统计** - 详细的成功/失败统计

## 🚀 快速开始

### 📋 系统要求

- **Python**: 3.8+ (推荐 3.10+)
- **操作系统**: Windows, macOS, Linux
- **内存**: 至少 4GB RAM
- **存储**: 至少 1GB 可用空间

### 🎯 一键部署 (推荐)

```bash
# 克隆项目
git clone https://github.com/maxliu9403/carousell_upload.git
cd carousell_upload

# 运行统一部署脚本 (自动检测最佳方式)
./deploy.sh

# 或指定部署模式
./deploy.sh --mode=local     # 本地开发部署
./deploy.sh --mode=system    # 系统级部署
./deploy.sh --mode=docker    # Docker部署
```

### 📦 其他安装方式

#### 方式一：一键安装脚本 (推荐)

```bash
# 一键安装 (自动检测系统并安装)
curl -fsSL https://raw.githubusercontent.com/maxliu9403/carousell_upload/main/install.sh | bash

# 或者分步执行
curl -fsSL https://raw.githubusercontent.com/maxliu9403/carousell_upload/main/install.sh -o install.sh
chmod +x install.sh
sudo ./install.sh
```

#### 方式二：使用 pip 安装

```bash
# 克隆项目
git clone https://github.com/maxliu9403/carousell_upload.git
cd carousell_upload

# 创建虚拟环境 (推荐)
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt

# 安装 Playwright 浏览器
playwright install chromium
```

#### 方式三：使用 setup.py 安装

```bash
# 开发模式安装
pip install -e .

# 或直接安装
python setup.py install
```

#### 方式三：使用 pyproject.toml 安装

```bash
# 安装基础版本
pip install -e .

# 安装开发版本 (包含测试工具)
pip install -e ".[dev]"

# 安装完整版本 (包含文档工具)
pip install -e ".[dev,docs,types]"
```

### 🔧 开发环境设置

```bash
# 安装开发依赖
pip install -r requirements-dev.txt

# 或使用 pyproject.toml
pip install -e ".[dev]"

# 安装 pre-commit 钩子
pre-commit install

# 运行代码格式化
black .

# 运行代码检查
flake8 .

# 运行类型检查
mypy .

# 运行测试
pytest
```

## 🚀 快速部署指南

### 🐳 Docker 部署 (推荐)

```bash
# 构建镜像
docker build -t carousell_upload .

# 运行容器
docker run -it --rm \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/data:/app/data \
  carousell_upload
```

### 🖥️ 本地快速部署

```bash
# 1. 克隆项目
git clone https://github.com/maxliu9403/carousell_upload.git
cd carousell_upload

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows

# 3. 安装依赖
pip install -r requirements.txt
playwright install chromium

# 4. 配置设置
cp config/settings.example.yaml config/settings.yaml
# 编辑 config/settings.yaml 文件

# 5. 运行程序
python -m cli.main
```

### ☁️ 云服务器部署

```bash
# Ubuntu/Debian 系统
sudo apt update
sudo apt install python3 python3-pip python3-venv git

# 克隆项目
git clone https://github.com/maxliu9403/carousell_upload.git
cd carousell_upload

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
playwright install chromium

# 配置系统服务 (可选)
sudo cp carousell-uploader.service /etc/systemd/system/
sudo systemctl enable carousell-uploader
sudo systemctl start carousell-uploader
```

### 🐍 虚拟环境管理

```bash
# 使用 conda
conda create -n carousell python=3.10
conda activate carousell
pip install -r requirements.txt

# 使用 poetry
poetry install
poetry shell

# 使用 pipenv
pipenv install
pipenv shell
```

## ⚙️ 配置说明

### 📝 基础配置

1. 复制示例配置文件：
```bash
cp config/settings.example.yaml config/settings.yaml
```

2. 编辑 `config/settings.yaml` 文件：

```yaml
browser:
  api_key: "your_api_key"
  api_port: 54345  # 用于获取浏览器窗口列表的端口

upload:
  image_extensions: [".jpg", ".jpeg", ".png", ".gif", ".webp"]

# 商品信息配置
product:
  descriptions:
    - "高品质商品，适合日常使用"
    - "全新商品，包装完好"
    - "优质材料制作，经久耐用"
    # ... 更多描述选项
  
  # 男性尺码：40-45
  male_sizes: ["40", "41", "42", "43", "44", "45"]
  
  # 女性尺码：36-40
  female_sizes: ["36", "37", "38", "39", "40"]
  
  # 面交地点
  meetup_locations:
    - "MTR"
    - "Central"
    - "Orchard"
    # ... 更多地点选项

# 页面操作配置
actions:
  default_timeout: 8000    # 默认超时时间（毫秒）
  retry_times: 3           # 重试次数
  retry_delay: 1.0         # 每次重试间隔（秒）
```

## 🎯 使用方法

### 方法一：使用默认配置运行

```bash
python -m cli.main
```

### 方法二：使用命令行参数

```bash
python -m cli.cli --title "Asics 运动鞋" --price "60" --category "sneakers" --brand "Asics" --gender "male"
```

### 方法三：Excel 批量多账号上传

```bash
python -m cli.main
```

程序会提示您：
1. 输入 Excel 文件路径
2. 选择上传地域 (HK/MY/SG)

### 方法四：使用浏览器窗口管理接口

```python
from browser.browser import fetch_all_browser_windows

# 获取所有浏览器窗口信息
api_port = 54347
token = "your_api_key"
browser_windows = fetch_all_browser_windows(api_port, token)

# 打印结果
for seq, window_info in browser_windows.items():
    print(f"序号 {seq}: ID = {window_info['id']}")
```

## 📊 Excel 文件格式

Excel 文件需要包含以下列：

| 列名 | 说明 | 示例 |
|------|------|------|
| URL | 商品链接 | https://example.com/product1 |
| SKU | 商品SKU | SKU001 |
| BrowserID | 浏览器ID（对应browser_window_map中的seq） | 1 |
| ProductNameCn | 中文商品名称 | 耐克运动鞋 |
| ProductNameEn | 英文商品名称 | Nike Sneakers |
| GenderEn | 英文性别 | Male/Female |
| HKPrice | 香港价格 | 500 |
| SGPrice | 新加坡价格 | 80 |
| MYPrice | 马来西亚价格 | 250 |
| Brand | 品牌 | Nike |
| Folder | 图片文件夹路径 | /path/to/images |

### 🔗 BrowserID 映射说明

- **BrowserID**: Excel中C列的值，对应指纹浏览器系统中的`seq`字段
- **动态映射**: 程序会自动调用`/browser/list`接口获取所有浏览器窗口信息
- **profile_id获取**: 通过BrowserID匹配`browser_window_map`中的`seq`，提取对应的`id`作为`profile_id`
- **自动启动**: 使用动态获取的`profile_id`启动对应的浏览器实例

### 📁 动态配置说明

- **profile_id**: 已从配置文件中移除，现在通过BrowserID动态获取
- **folder**: 已从配置文件中移除，现在从Excel文件的L列（Folder列）中读取
- **图片路径**: 每个商品的图片路径在Excel中单独指定，支持不同商品使用不同图片文件夹
- **api_url**: 已从配置文件中移除，现在通过`api_port`自动拼接为`http://127.0.0.1:{api_port}/browser/open`

### 创建示例 Excel 文件

```bash
python create_example_excel.py
```


## 📁 项目结构

```
carousell_upload/
├── core/                     # 核心功能模块
│   ├── __init__.py
│   ├── config.py             # 配置管理
│   ├── models.py             # 数据模型
│   └── logger.py             # 日志系统
├── browser/                  # 浏览器操作模块
│   ├── __init__.py
│   ├── browser.py            # 浏览器管理
│   └── actions.py            # 页面操作
├── data/                     # 数据处理模块
│   ├── __init__.py
│   ├── excel_parser.py       # Excel解析器
│   └── record_manager.py     # 记录管理
├── uploader/                 # 上传功能模块
│   ├── __init__.py
│   ├── core/                 # 核心功能
│   │   ├── __init__.py
│   │   ├── base_uploader.py  # 基础上传器
│   │   └── carousell_uploader.py # 工厂包装器
│   ├── actions/              # 安全操作
│   │   ├── __init__.py
│   │   └── enhanced_safe_actions.py # 增强安全操作
│   ├── config/               # 配置管理
│   │   ├── __init__.py
│   │   ├── enhanced_css_selector_manager.py # CSS选择器管理
│   │   └── regional_config_loader.py # 地域配置加载器
│   ├── factory/              # 工厂模式
│   │   ├── __init__.py
│   │   └── uploader_factory.py # 上传器工厂
│   ├── multi/                # 多账号功能
│   │   ├── __init__.py
│   │   └── multi_account_uploader.py # 多账号上传器
│   ├── utils/                # 工具函数
│   │   ├── __init__.py
│   │   └── utils.py          # 工具函数
│   └── regions/              # 地域特定上传器
│       ├── sg/               # 新加坡
│       │   ├── sneakers/     # 运动鞋
│       │   ├── bags/         # 包包
│       │   └── clothes/      # 服装
│       ├── hk/               # 香港
│       │   ├── sneakers/     # 运动鞋
│       │   ├── bags/         # 包包
│       │   └── clothes/      # 服装
│       └── my/               # 马来西亚
│           ├── sneakers/     # 运动鞋
│           ├── bags/         # 包包
│           └── clothes/      # 服装
├── cli/                      # 命令行接口
│   ├── __init__.py
│   ├── main.py               # 主程序入口
│   └── cli.py                # CLI接口
├── config/                   # 配置文件
│   ├── settings.yaml         # 主配置文件
│   └── settings.example.yaml # 配置示例文件
├── scripts/                  # 部署脚本
│   ├── quick-deploy.sh       # 快速部署脚本
│   └── docker-deploy.sh      # Docker部署脚本
├── logs/                     # 日志文件目录
├── requirements.txt          # 生产依赖
├── requirements-dev.txt      # 开发依赖
├── setup.py                  # 安装配置
├── pyproject.toml           # 现代Python项目配置
├── install.sh               # 系统级安装脚本
├── deploy.sh                # 统一部署脚本
└── README.md                # 项目说明
```

### 🏗️ 模块说明

- **core/**: 核心功能模块，包含配置管理、数据模型和日志系统
- **browser/**: 浏览器操作模块，负责浏览器控制和页面操作
- **data/**: 数据处理模块，处理Excel解析和记录管理
- **uploader/**: 上传功能模块，采用模块化架构设计
  - **core/**: 核心上传器，包含基础上传器和工厂包装器
  - **actions/**: 安全操作模块，提供增强的安全操作功能
  - **config/**: 配置管理模块，管理CSS选择器和地域配置
  - **factory/**: 工厂模式模块，负责创建上传器实例
  - **multi/**: 多账号功能模块，支持多账号并发上传
  - **utils/**: 工具函数模块，提供通用工具函数
  - **regions/**: 地域特定上传器，按地域和类目组织
- **cli/**: 命令行接口模块，提供主程序入口和CLI接口
- **config/**: 配置文件目录，存放YAML配置文件
- **scripts/**: 部署脚本目录，包含各种部署方式
- **logs/**: 日志文件目录，存放运行日志

### 🎯 架构优势

**模块化设计**:
- **职责清晰**: 每个模块都有明确的职责和用途
- **易于维护**: 相关功能集中在一起，便于维护和调试
- **可读性强**: 目录结构直观，一目了然
- **扩展性好**: 新增功能可以轻松归类到对应模块
- **解耦合**: 模块间依赖关系清晰，降低耦合度

**uploader模块架构**:
- **core/**: 核心业务逻辑，包含基础上传器和工厂包装器
- **actions/**: 安全操作封装，提供统一的操作接口
- **config/**: 配置管理，支持地域特定的CSS选择器配置
- **factory/**: 工厂模式，动态创建地域特定上传器
- **multi/**: 多账号支持，实现并发上传
- **utils/**: 工具函数，提供通用功能
- **regions/**: 地域特定实现，支持不同地区的业务逻辑

## 🛠️ 技术栈

### 核心依赖
- **playwright>=1.40.0** - 浏览器自动化框架
- **requests>=2.31.0** - HTTP请求库
- **PyYAML>=6.0.1** - YAML配置文件解析
- **pandas>=2.0.0** - 数据处理和分析
- **openpyxl>=3.1.0** - Excel文件读写
- **pyautogui>=0.9.54** - 图形用户界面自动化
- **pyperclip>=1.8.2** - 剪贴板操作

### 开发工具
- **pytest>=7.0.0** - 测试框架
- **black>=23.0.0** - 代码格式化
- **flake8>=6.0.0** - 代码检查
- **mypy>=1.0.0** - 类型检查
- **pre-commit>=3.0.0** - Git钩子

### 文档工具
- **sphinx>=6.0.0** - 文档生成
- **sphinx-rtd-theme>=1.2.0** - 主题

## 🚀 部署方式

### 统一部署脚本 (推荐)
```bash
# 自动检测最佳部署方式
./deploy.sh

# 指定部署模式
./deploy.sh --mode=local     # 本地开发部署
./deploy.sh --mode=system    # 本地部署 (推荐)
./deploy.sh --mode=docker    # Docker部署
```

### 本地部署 (推荐)
```bash
# 1. 克隆项目
git clone https://github.com/maxliu9403/carousell_upload.git
cd carousell_upload

# 2. 运行本地安装脚本
./install.sh
```

### 本地开发部署
```bash
# 快速部署
./scripts/quick-deploy.sh
```

### Docker部署
```bash
# Docker部署
./scripts/docker-deploy.sh
```

## 🛠️ 故障排除

### 常见问题

#### 1. 依赖安装失败
```bash
# 升级pip
pip install --upgrade pip

# 使用国内镜像
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# 清理缓存
pip cache purge
```

#### 2. Playwright安装失败
```bash
# 安装系统依赖
playwright install --with-deps chromium

# 或设置环境变量
PLAYWRIGHT_BROWSERS_PATH=0 playwright install chromium
```

#### 3. 权限问题
```bash
# 修复权限
sudo chown -R $USER:$USER /path/to/project
chmod +x scripts/*.sh
```

#### 4. 端口占用
```bash
# 检查端口占用
lsof -i :54345
netstat -tulpn | grep 54345

# 杀死占用进程
kill -9 <PID>
```

### 调试模式
```bash
# 启用调试模式
export DEBUG=1
export LOG_LEVEL=DEBUG
python -m cli.main
```

## 📊 性能优化

### 系统优化
```bash
# 增加文件描述符限制
echo "* soft nofile 65536" >> /etc/security/limits.conf
echo "* hard nofile 65536" >> /etc/security/limits.conf

# 优化内核参数
echo "vm.max_map_count=262144" >> /etc/sysctl.conf
sysctl -p
```

### 应用优化
```yaml
# config/settings.yaml
actions:
  default_timeout: 5000    # 减少超时时间
  retry_times: 2          # 减少重试次数
  retry_delay: 0.5        # 减少重试间隔

browser:
  headless: true          # 使用无头模式
  slow_mo: 0             # 禁用慢动作
  devtools: false         # 禁用开发者工具
```

## 🔧 高级配置

### 🎯 环境变量配置

```bash
# 设置环境变量
export CAROUSELL_API_KEY="your_api_key"
export CAROUSELL_API_PORT="54345"
export CAROUSELL_REGION="SG"
export CAROUSELL_CATEGORY="sneakers"

# 或在 .env 文件中设置
echo "CAROUSELL_API_KEY=your_api_key" > .env
echo "CAROUSELL_API_PORT=54345" >> .env
```


## 📚 开发指南

### 🧪 测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_uploader.py

# 运行测试并生成覆盖率报告
pytest --cov=. --cov-report=html

# 运行测试并生成报告
pytest --html=report.html --self-contained-html
```

### 🔧 代码质量

```bash
# 代码格式化
black .

# 代码检查
flake8 .

# 类型检查
mypy .

# 导入排序
isort .
```

### 📖 文档生成

```bash
# 生成API文档
sphinx-build -b html docs docs/_build/html

# 或使用make
make docs
```

## 🤝 贡献指南

### 📝 提交规范

```bash
# 提交信息格式
git commit -m "feat: 添加新功能"
git commit -m "fix: 修复bug"
git commit -m "docs: 更新文档"
git commit -m "style: 代码格式化"
git commit -m "refactor: 代码重构"
git commit -m "test: 添加测试"
```

### 🔄 工作流程

1. Fork 项目
2. 创建功能分支: `git checkout -b feature/amazing-feature`
3. 提交更改: `git commit -m 'Add amazing feature'`
4. 推送分支: `git push origin feature/amazing-feature`
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [Playwright](https://playwright.dev/) - 浏览器自动化框架
- [Pandas](https://pandas.pydata.org/) - 数据处理库
- [Requests](https://requests.readthedocs.io/) - HTTP库
- [PyYAML](https://pyyaml.org/) - YAML解析库

## 📝 更新日志

### 🔧 最新修正 (v1.0.0)

#### 系统级部署指令优化
- **修正前**: 使用curl直接下载install.sh脚本
- **修正后**: 先克隆项目，再运行install.sh脚本
- **原因**: install.sh脚本假设项目文件已经存在，没有包含git clone命令

#### GitHub链接和路径修正
- ✅ 统一项目名称为 `carousell_upload`
- ✅ 修正所有GitHub链接指向正确仓库
- ✅ 更新Docker镜像名称为 `carousell_upload`
- ✅ 修正系统服务文件中的路径
- ✅ 更新联系信息和文档链接

#### 部署方式整合
- ✅ 创建统一部署脚本 `deploy.sh`
- ✅ 支持自动检测最佳部署方式
- ✅ 整合所有部署脚本到统一入口

## 📞 支持

- 📧 邮箱: support@carousell-upload.com
- 🐛 问题反馈: [GitHub Issues](https://github.com/maxliu9403/carousell_upload/issues)
- 📖 文档: [项目文档](https://carousell-upload.readthedocs.io/)
- 💬 讨论: [GitHub Discussions](https://github.com/maxliu9403/carousell_upload/discussions)

---

<div align="center">

**⭐ 如果这个项目对您有帮助，请给我们一个星标！⭐**

Made with ❤️ by Carousell Uploader Team

</div>

### 商品信息配置

在 `config/settings.yaml` 中可以设置默认商品信息：

```yaml
product_defaults:
  title: "默认商品标题"
  price: "50"
  description: "默认商品描述"
  category: "others"
  brand: ""
  size: ""
  condition: "new"
  gender: "unisex"
  location: "All of Singapore"
  meetup_location: "MTR"
  multi_quantity: false
```

### 日志配置

日志文件会自动保存在 `logs/` 目录下，按日期命名。

## 🔍 健康检查功能

项目启动时会自动检查浏览器API的健康状态：

- **检查时机**: 在加载配置后、开始上传前
- **检查内容**: 向 `/health` 端点发送GET请求
- **检查结果**: 
  - ✅ 通过：继续执行程序
  - ❌ 失败：显示错误信息并退出程序

## 📝 成功记录功能

项目支持本地JSON文件记录所有执行成功的记录，实现断点续传功能：

### 功能特点

- **智能跳过**: 自动跳过已成功的BrowserID，避免重复上传
- **唯一标识**: 基于Excel文件路径、地域、日期的唯一标识
- **时间窗口**: 同一天内的修改被认为是同一批次，支持文件内容变化
- **断点续传**: 支持中断后继续执行，只处理未完成的账号
- **记录管理**: 提供完整的记录查询、统计和清理功能

### 记录文件结构

```json
{
  "created_at": "2025-09-21T22:20:48",
  "updated_at": "2025-09-21T22:25:30",
  "records": {
    "/path/to/products.xlsx_HK_2025-09-21": {
      "excel_path": "/path/to/products.xlsx",
      "region": "HK",
      "date": "2025-09-21",
      "created_at": "2025-09-21T22:20:48",
      "updated_at": "2025-09-21T22:25:30",
      "browser_records": {
        "123": ["SKU001", "SKU002"],
        "456": ["SKU003", "SKU004", "SKU005"]
      }
    }
  }
}
```

### 使用说明

1. **自动记录**: 每次成功上传商品后自动记录
2. **智能跳过**: 启动时自动跳过已成功的BrowserID
3. **记录摘要**: 显示历史记录统计信息
4. **文件位置**: 记录文件默认保存在项目根目录的 `success_records.json`

### 优化逻辑

系统采用高效的过滤机制，避免不必要的资源消耗：

1. **提前过滤**: 在拉取浏览器数据前，先根据成功记录过滤商品
2. **精确获取**: 只获取需要处理的BrowserID对应的浏览器窗口数据
3. **智能判断**: 如果所有商品都已成功，直接返回成功状态
4. **性能优化**: 减少API调用次数，提高执行效率

**执行流程**:
```
解析Excel → 获取成功记录 → 过滤商品 → 提取需要的BrowserID → 获取浏览器数据 → 执行上传
```

### 健康检查失败时的提示信息

```
❌ 浏览器API健康检查失败，程序退出
请检查以下项目:
1. 浏览器服务是否已启动
2. API端口是否正确
3. API密钥是否正确
```

## ⚠️ 注意事项

- 确保指纹浏览器服务正在运行
- 图片文件夹路径必须存在且包含有效图片
- 建议在测试环境中先验证功能
- 遵守 Carousell 平台的使用条款
- 建议设置合理的上传间隔，避免被平台限制

## 🐛 故障排除

### 常见问题

1. **浏览器启动失败**
   - 检查指纹浏览器服务是否运行
   - 验证 API 密钥和配置文件 ID

2. **图片上传失败**
   - 检查图片文件夹路径是否正确
   - 确认图片格式是否支持

3. **页面元素找不到**
   - 网站可能更新了页面结构
   - 检查网络连接是否正常

4. **模块导入失败**
   - 确保所有依赖包已正确安装
   - 检查Python路径设置
   - 验证模块文件是否存在

5. **配置文件问题**
   - 确保 `config/settings.yaml` 文件存在
   - 检查YAML文件格式是否正确
   - 验证配置项是否完整

### 模块化架构优势

新的模块化设计提供了以下优势：

- **清晰的职责分离**: 每个模块都有明确的职责范围
- **更好的可维护性**: 代码结构更清晰，便于维护和扩展
- **灵活的依赖管理**: 使用延迟导入避免循环依赖
- **向后兼容性**: 保持了原有的API接口
- **易于测试**: 模块化设计便于单元测试

### 日志查看

查看 `logs/` 目录下的日志文件获取详细错误信息。

## 📄 许可证

本项目仅供学习和研究使用，请遵守相关法律法规和平台条款。
