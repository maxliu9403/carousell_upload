# Carousell 自动上传工具

这是一个用于 Carousell 平台的自动化商品上传工具，支持批量上传商品图片和自动填写商品信息。

## 🚀 功能特性

- 🚀 自动启动指纹浏览器
- 📁 批量上传图片文件
- 📝 自动填写商品信息
- 🔄 商品状态管理
- ⚙️ 灵活的配置系统
- 📊 完整的日志记录
- 🎯 命令行接口支持
- 🛡️ 错误处理和重试机制
- 🌐 浏览器窗口管理接口
- 📊 Excel 批量商品管理
- 🌍 多地域支持 (HK/MY/SG)
- 👥 多账号串行上传
- 🔗 动态BrowserID到profile_id映射
- 🏗️ 模块化架构设计
- 🔧 延迟导入机制
- 📦 清晰的依赖管理

## 📦 安装依赖

```bash
# 安装 Python 依赖
pip install -r requirements.txt

# 安装 Playwright 浏览器
playwright install chromium
```

## ⚙️ 配置说明

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
| GenderCn | 中文性别 | 男/女 |
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
│   ├── carousell_uploader.py # 核心上传逻辑
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
