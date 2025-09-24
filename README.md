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

### 📦 安装方式

#### 方式一：使用 pip 安装 (推荐)

```bash
# 克隆项目
git clone https://github.com/your-org/carousell-uploader.git
cd carousell-uploader

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

#### 方式二：使用 setup.py 安装

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
docker build -t carousell-uploader .

# 运行容器
docker run -it --rm \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/data:/app/data \
  carousell-uploader
```

### 🖥️ 本地快速部署

```bash
# 1. 克隆项目
git clone https://github.com/your-org/carousell-uploader.git
cd carousell-uploader

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
git clone https://github.com/your-org/carousell-uploader.git
cd carousell-uploader

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

项目采用模块化设计，按功能将代码分离到不同的模块中：

```
carousell/
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
│   ├── excel_parser.py       # Excel 解析器
│   └── record_manager.py     # 记录管理
├── uploader/                 # 上传功能模块
│   ├── __init__.py
│   ├── carousell_uploader_new.py # 核心上传逻辑（模块化）
│   ├── multi_account_uploader.py # 多账号上传器
│   └── utils.py              # 工具函数
├── cli/                      # 命令行接口
│   ├── __init__.py
│   ├── main.py               # 主程序入口
│   └── cli.py                # CLI接口
├── config/                   # 配置文件
│   ├── settings.yaml         # 主配置文件
│   └── settings.example.yaml # 配置示例文件
├── logs/                     # 日志文件目录
├── requirements.txt          # 依赖列表
└── README.md                # 项目说明
```

### 🏗️ 模块说明

- **core/**: 核心功能模块，包含配置管理、数据模型和日志系统
- **browser/**: 浏览器操作模块，负责浏览器控制和页面操作
- **data/**: 数据处理模块，处理Excel解析和记录管理
- **uploader/**: 上传功能模块，包含Carousell上传器和多账号上传器
- **cli/**: 命令行接口模块，提供主程序入口和CLI接口
- **config/**: 配置文件目录，存放YAML配置文件
- **logs/**: 日志文件目录，存放运行日志

### 📦 模块导入示例

```python
# 导入核心功能
from core import ProductInfo, UploadConfig, logger
from core.config import create_upload_config

# 导入浏览器功能
from browser import start_browser, check_browser_api_health
from browser.actions import click_with_wait, smart_goto

# 导入数据处理
from data import ExcelProductParser, SuccessRecordManager

# 导入上传功能
from uploader import CarousellUploader, MultiAccountUploader
from uploader.utils import enrich_product_info

# 导入CLI接口
from cli import run, cli_main
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

### 🐳 Docker 配置

创建 `Dockerfile`:

```dockerfile
FROM python:3.10-slim

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 安装Playwright浏览器
RUN playwright install chromium

# 复制项目文件
COPY . .

# 设置入口点
ENTRYPOINT ["python", "-m", "cli.main"]
```

创建 `docker-compose.yml`:

```yaml
version: '3.8'
services:
  carousell-uploader:
    build: .
    volumes:
      - ./config:/app/config
      - ./data:/app/data
      - ./logs:/app/logs
    environment:
      - CAROUSELL_API_KEY=${CAROUSELL_API_KEY}
      - CAROUSELL_API_PORT=${CAROUSELL_API_PORT}
    restart: unless-stopped
```

## 🛠️ 故障排除

### ❌ 常见问题

#### 1. 依赖安装失败
```bash
# 问题：pip install 失败
# 解决方案：
pip install --upgrade pip
pip install --no-cache-dir -r requirements.txt

# 或使用国内镜像
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
```

#### 2. Playwright 浏览器安装失败
```bash
# 问题：playwright install 失败
# 解决方案：
playwright install --with-deps chromium
# 或
PLAYWRIGHT_BROWSERS_PATH=0 playwright install chromium
```

#### 3. 权限问题
```bash
# 问题：权限不足
# 解决方案：
sudo chown -R $USER:$USER /path/to/project
chmod +x scripts/*.sh
```

#### 4. 端口占用
```bash
# 问题：端口被占用
# 解决方案：
# 检查端口占用
lsof -i :54345
# 或
netstat -tulpn | grep 54345

# 杀死占用进程
kill -9 <PID>
```

### 🔍 调试模式

```bash
# 启用详细日志
export CAROUSELL_DEBUG=1
python -m cli.main

# 或使用环境变量
DEBUG=1 python -m cli.main
```

### 📊 性能优化

#### 1. 内存优化
```bash
# 设置Python内存限制
export PYTHONMALLOC=malloc
export MALLOC_TRIM_THRESHOLD_=131072
```

#### 2. 并发优化
```yaml
# config/settings.yaml
actions:
  default_timeout: 5000    # 减少超时时间
  retry_times: 2          # 减少重试次数
  retry_delay: 0.5        # 减少重试间隔
```

#### 3. 浏览器优化
```yaml
browser:
  headless: true          # 使用无头模式
  slow_mo: 0             # 禁用慢动作
  devtools: false         # 禁用开发者工具
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

## 📞 支持

- 📧 邮箱: support@carousell-uploader.com
- 🐛 问题反馈: [GitHub Issues](https://github.com/your-org/carousell-uploader/issues)
- 📖 文档: [项目文档](https://carousell-uploader.readthedocs.io/)
- 💬 讨论: [GitHub Discussions](https://github.com/your-org/carousell-uploader/discussions)

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
