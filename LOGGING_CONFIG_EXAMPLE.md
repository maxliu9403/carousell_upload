# 日志配置使用示例

## 🎯 功能描述

支持从配置文件中获取日志等级，提供灵活的日志配置选项，包括控制台和文件日志的独立配置。

## 🔧 配置文件设置

### 在 `config/settings.yaml` 中添加日志配置

```yaml
# 日志配置
logging:
  level: "INFO"            # 日志等级: DEBUG, INFO, WARNING, ERROR, CRITICAL
  console_level: "INFO"   # 控制台日志等级
  file_level: "DEBUG"     # 文件日志等级
  enable_colors: true      # 是否启用彩色输出
  enable_file_logging: true # 是否启用文件日志
  log_rotation:
    when: "midnight"      # 轮转时间: midnight, daily, weekly, monthly
    interval: 1            # 轮转间隔
    backup_count: 5        # 保留备份文件数量
    days_to_keep: 5        # 保留天数
```

## 📝 使用示例

### 示例 1：基本使用

```python
from core.logger import setup_logger

# 使用默认配置（从配置文件读取）
logger = setup_logger()

# 记录日志
logger.info("这是一条信息日志")
logger.debug("这是一条调试日志")
logger.warning("这是一条警告日志")
logger.error("这是一条错误日志")
```

### 示例 2：自定义日志记录器

```python
from core.logger import setup_logger

# 创建自定义日志记录器
custom_logger = setup_logger("my_custom_logger")

# 记录日志
custom_logger.info("自定义日志记录器")
```

### 示例 3：强制指定日志等级

```python
import logging
from core.logger import setup_logger

# 强制使用DEBUG等级（忽略配置文件）
debug_logger = setup_logger("debug_logger", level=logging.DEBUG)

# 记录日志
debug_logger.debug("强制DEBUG等级")
```

## 🚀 配置选项详解

### 日志等级配置

| 配置项 | 说明 | 可选值 | 默认值 |
|--------|------|--------|--------|
| `level` | 全局日志等级 | DEBUG, INFO, WARNING, ERROR, CRITICAL | INFO |
| `console_level` | 控制台日志等级 | DEBUG, INFO, WARNING, ERROR, CRITICAL | INFO |
| `file_level` | 文件日志等级 | DEBUG, INFO, WARNING, ERROR, CRITICAL | DEBUG |

### 功能配置

| 配置项 | 说明 | 类型 | 默认值 |
|--------|------|------|--------|
| `enable_colors` | 是否启用彩色输出 | boolean | true |
| `enable_file_logging` | 是否启用文件日志 | boolean | true |

### 日志轮转配置

| 配置项 | 说明 | 可选值 | 默认值 |
|--------|------|--------|--------|
| `when` | 轮转时间 | midnight, daily, weekly, monthly | midnight |
| `interval` | 轮转间隔 | 整数 | 1 |
| `backup_count` | 保留备份文件数量 | 整数 | 5 |
| `days_to_keep` | 保留天数 | 整数 | 5 |

## 📊 配置示例

### 开发环境配置

```yaml
logging:
  level: "DEBUG"
  console_level: "DEBUG"
  file_level: "DEBUG"
  enable_colors: true
  enable_file_logging: true
  log_rotation:
    when: "midnight"
    interval: 1
    backup_count: 10
    days_to_keep: 7
```

### 生产环境配置

```yaml
logging:
  level: "INFO"
  console_level: "WARNING"
  file_level: "INFO"
  enable_colors: false
  enable_file_logging: true
  log_rotation:
    when: "midnight"
    interval: 1
    backup_count: 30
    days_to_keep: 30
```

### 调试配置

```yaml
logging:
  level: "DEBUG"
  console_level: "DEBUG"
  file_level: "DEBUG"
  enable_colors: true
  enable_file_logging: true
  log_rotation:
    when: "midnight"
    interval: 1
    backup_count: 5
    days_to_keep: 3
```

## 🎯 高级用法

### 动态配置加载

```python
from core.logger import load_logging_config, setup_logger

# 加载配置
config = load_logging_config()
print(f"当前日志等级: {config['level']}")
print(f"控制台日志等级: {config['console_level']}")
print(f"文件日志等级: {config['file_level']}")

# 使用配置创建日志记录器
logger = setup_logger()
```

### 条件日志记录

```python
from core.logger import setup_logger

logger = setup_logger()

# 根据配置决定是否记录调试信息
if logger.isEnabledFor(logging.DEBUG):
    logger.debug("详细的调试信息")

# 根据配置决定是否记录警告
if logger.isEnabledFor(logging.WARNING):
    logger.warning("警告信息")
```

### 自定义日志格式

```python
import logging
from core.logger import setup_logger

# 创建自定义格式的日志记录器
logger = setup_logger()

# 添加自定义处理器
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
```

## 🔄 配置优先级

1. **代码中指定的level参数**（最高优先级）
2. **配置文件中的level设置**
3. **默认配置**（最低优先级）

## 🚀 性能优化

### 生产环境优化

```yaml
logging:
  level: "INFO"              # 减少日志输出
  console_level: "WARNING"  # 控制台只显示警告和错误
  file_level: "INFO"        # 文件记录详细信息
  enable_colors: false      # 禁用彩色输出
  enable_file_logging: true # 启用文件日志
  log_rotation:
    when: "midnight"
    interval: 1
    backup_count: 30        # 保留更多备份
    days_to_keep: 30        # 保留更长时间
```

### 开发环境优化

```yaml
logging:
  level: "DEBUG"            # 显示所有日志
  console_level: "DEBUG"    # 控制台显示所有日志
  file_level: "DEBUG"       # 文件记录所有日志
  enable_colors: true       # 启用彩色输出
  enable_file_logging: true # 启用文件日志
  log_rotation:
    when: "midnight"
    interval: 1
    backup_count: 5         # 保留较少备份
    days_to_keep: 5         # 保留较短时间
```

## 🎯 最佳实践

### 1. 环境特定配置
- 开发环境：使用DEBUG等级，启用彩色输出
- 测试环境：使用INFO等级，启用文件日志
- 生产环境：使用WARNING等级，禁用彩色输出

### 2. 日志等级选择
- **DEBUG**：详细的调试信息
- **INFO**：一般信息记录
- **WARNING**：警告信息
- **ERROR**：错误信息
- **CRITICAL**：严重错误

### 3. 文件日志管理
- 定期清理旧日志文件
- 使用日志轮转避免文件过大
- 根据存储空间调整保留天数

### 4. 性能考虑
- 生产环境避免使用DEBUG等级
- 控制台日志等级可以高于文件日志等级
- 定期检查日志文件大小
