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
python -m uploader.main
```

### 方法二：使用命令行参数

```bash
python -m uploader.cli --title "Asics 运动鞋" --price "60" --category "sneakers" --brand "Asics" --gender "male"
```

### 方法三：Excel 批量多账号上传

```bash
python -m uploader.main
```

程序会提示您：
1. 输入 Excel 文件路径
2. 选择上传地域 (HK/MY/SG)

### 方法四：使用浏览器窗口管理接口

```python
from uploader.browser import fetch_all_browser_windows

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

```
carousell/
├── config/
│   ├── settings.yaml          # 主配置文件
│   └── settings.example.yaml  # 配置示例文件
├── uploader/
│   ├── __init__.py
│   ├── main.py               # 主程序入口
│   ├── cli.py                # 命令行接口
│   ├── carousell_uploader.py # 核心上传逻辑
│   ├── models.py             # 数据模型
│   ├── config.py             # 配置管理
│   ├── browser.py            # 浏览器管理
│   ├── actions.py            # 页面操作
│   ├── logger.py             # 日志系统
│   ├── utils.py              # 工具函数
│   ├── excel_parser.py       # Excel 解析器
│   └── multi_account_uploader.py # 多账号上传器
├── logs/                     # 日志文件目录
├── requirements.txt          # 依赖列表
└── README.md                # 项目说明
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

### 日志查看

查看 `logs/` 目录下的日志文件获取详细错误信息。

## 📄 许可证

本项目仅供学习和研究使用，请遵守相关法律法规和平台条款。
