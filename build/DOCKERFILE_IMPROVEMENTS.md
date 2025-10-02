# Dockerfile.windows 改进说明

## 问题描述

原始的Dockerfile.windows只构建了可执行文件，没有包含必要的配置文件，导致用户需要手动创建配置文件。

## 解决方案

修改后的Dockerfile.windows现在包含以下改进：

### 1. 完整的配置文件结构

构建后的镜像包含以下目录结构：

```
C:\output\
├── CarousellUploader.exe          # 主程序
├── config\                        # 配置文件目录
│   ├── settings.yaml             # 主配置文件
│   └── settings.example.yaml     # 配置示例文件
├── uploader\                      # 上传器模块
│   └── regions\                   # 地域配置
│       ├── hk\                   # 香港配置
│       │   └── sneakers\         # 运动鞋类目
│       │       └── css_selectors.yaml
│       └── sg\                   # 新加坡配置
│           └── sneakers\         # 运动鞋类目
│               └── css_selectors.yaml
├── data\                          # 数据处理模块
├── examples\                      # 示例文件
│   └── sample.csv                # 示例Excel文件
└── README.txt                    # 使用说明
```

### 2. 新增的Dockerfile功能

#### 配置文件复制
```dockerfile
# 复制配置文件到输出目录
RUN mkdir C:\\output\\config
RUN copy config\\settings.yaml C:\\output\\config\\
RUN copy config\\settings.example.yaml C:\\output\\config\\
```

#### CSS选择器配置复制
```dockerfile
# 复制CSS选择器配置文件，保留地域文件夹结构
RUN xcopy uploader\\regions C:\\output\\uploader\\regions\\ /E /I /Y
```

#### 数据目录复制
```dockerfile
# 复制数据目录
RUN xcopy data C:\\output\\data\\ /E /I /Y
```

#### 示例文件创建
```dockerfile
# 创建示例Excel文件目录
RUN mkdir C:\\output\\examples
RUN echo "SKU,Title,Price,Description,Images" > C:\\output\\examples\\sample.csv
RUN echo "F36980,Test Product,100,Test Description,image1.jpg" >> C:\\output\\examples\\sample.csv
```

#### 使用说明文档
```dockerfile
# 创建README文件
RUN echo "Carousell Uploader - Windows Executable" > C:\\output\\README.txt
RUN echo "" >> C:\\output\\README.txt
RUN echo "Files included:" >> C:\\output\\README.txt
RUN echo "- CarousellUploader.exe: Main executable" >> C:\\output\\README.txt
RUN echo "- config/: Configuration files" >> C:\\output\\README.txt
RUN echo "- css_selectors/: CSS selector configurations" >> C:\\output\\README.txt
RUN echo "- data/: Data processing modules" >> C:\\output\\README.txt
RUN echo "- examples/: Sample Excel files" >> C:\\output\\README.txt
RUN echo "" >> C:\\output\\README.txt
RUN echo "Usage:" >> C:\\output\\README.txt
RUN echo "1. Configure settings.yaml with your browser API settings" >> C:\\output\\README.txt
RUN echo "2. Prepare your Excel file with product data" >> C:\\output\\README.txt
RUN echo "3. Run: CarousellUploader.exe" >> C:\\output\\README.txt
```

### 3. 配置文件说明

#### settings.yaml
主配置文件，包含：
- 浏览器API配置
- 域名配置
- 上传参数配置
- 产品详情配置

#### CSS选择器配置文件
- `uploader/regions/hk/sneakers/css_selectors.yaml`: 香港运动鞋CSS选择器
- `uploader/regions/sg/sneakers/css_selectors.yaml`: 新加坡运动鞋CSS选择器

#### 示例文件
- `sample.csv`: 示例Excel文件格式

### 4. 使用方法

#### 构建镜像
```bash
docker build -f build/Dockerfile.windows -t carousell-uploader .
```

#### 运行容器
```bash
docker run -it carousell-uploader
```

#### 复制文件到宿主机
```bash
docker cp <container_id>:/output ./carousell-uploader
```

### 5. 配置修改指南

用户可以通过以下方式修改配置：

#### 方法1：直接编辑配置文件
1. 编辑 `config/settings.yaml`
2. 修改浏览器API配置
3. 保存文件

#### 方法2：使用配置管理脚本
```python
from config_manager import ConfigManager

config_manager = ConfigManager()
config_manager.update_browser_config("IxBrowser", "api_key", "base_url")
```

### 6. 优势

1. **开箱即用**: 构建后包含所有必要配置文件
2. **完整结构**: 包含示例文件和说明文档
3. **易于配置**: 提供配置管理脚本
4. **用户友好**: 包含详细的使用说明

### 7. 注意事项

1. 确保所有必要的配置文件在构建时存在
2. CSS选择器配置文件需要根据实际项目结构调整路径
3. 示例文件格式需要与实际需求匹配

这样修改后，用户获得的不再是单一的可执行文件，而是一个完整的、可配置的应用程序包。
