# 🚀 统一部署指南

## 📋 部署脚本整合说明

### 🔍 脚本对比

| 脚本 | 功能 | 适用场景 | 特点 |
|------|------|----------|------|
| **install.sh** | 系统级安装 | 生产环境 | 创建系统用户、配置服务、完整权限管理 |
| **scripts/quick-deploy.sh** | 快速部署 | 开发环境 | 本地虚拟环境、快速配置 |
| **scripts/docker-deploy.sh** | Docker部署 | 容器化环境 | 容器化部署、环境隔离 |
| **deploy.sh** | 统一部署 | 所有场景 | 智能选择、统一入口 |

## 🎯 统一部署脚本 (deploy.sh)

### 使用方法

```bash
# 基本使用 (自动检测最佳方式)
./deploy.sh

# 指定部署模式
./deploy.sh --mode=local     # 本地开发部署
./deploy.sh --mode=system    # 系统级部署
./deploy.sh --mode=docker    # Docker部署
./deploy.sh --mode=auto      # 自动检测

# 查看帮助
./deploy.sh --help
```

### 自动检测逻辑

1. **root权限** → 系统级部署
2. **Docker环境** → 容器化部署
3. **Python环境** → 本地部署
4. **默认** → 本地部署

## 🚀 快速开始

### 1. 克隆项目
```bash
git clone https://github.com/maxliu9403/carousell_upload.git
cd carousell_upload
```

### 2. 运行统一部署脚本
```bash
# 自动检测最佳部署方式
./deploy.sh

# 或指定特定模式
./deploy.sh --mode=local
```

### 3. 配置和运行
```bash
# 编辑配置文件
nano config/settings.yaml

# 运行程序
python -m cli.main
```

## 📊 部署模式详解

### 🏠 本地开发部署 (local)
- **适用场景**: 开发测试、个人使用
- **特点**: 快速、简单、无权限要求
- **目录**: 当前项目目录
- **用户**: 当前用户

```bash
./deploy.sh --mode=local
```

### 🏭 系统级部署 (system)
- **适用场景**: 生产环境、服务器部署
- **特点**: 完整、安全、系统服务
- **目录**: `/opt/carousell_upload`
- **用户**: 专用系统用户

```bash
./deploy.sh --mode=system
```

### 🐳 Docker部署 (docker)
- **适用场景**: 容器化环境、云部署
- **特点**: 隔离、可移植、易管理
- **目录**: 容器内
- **用户**: 容器用户

```bash
./deploy.sh --mode=docker
```

## 🔧 高级配置

### 环境变量
```bash
# 设置部署模式
export DEPLOY_MODE=local

# 设置项目目录
export PROJECT_DIR=/opt/carousell_upload

# 设置用户
export DEPLOY_USER=carousell
```

### 配置文件
```yaml
# config/settings.yaml
browser:
  api_key: "your_api_key"
  api_port: 54345

upload:
  image_extensions: [".jpg", ".jpeg", ".png"]

product:
  categories:
    sneakers:
      name: "运动鞋"
      search_keyword: "sneakers"
```

## 🛠️ 故障排除

### 常见问题

#### 1. 权限问题
```bash
# 修复脚本权限
chmod +x deploy.sh
chmod +x scripts/*.sh
chmod +x install.sh
```

#### 2. 依赖问题
```bash
# 检查Python版本
python3 --version

# 检查依赖文件
ls -la requirements.txt
```

#### 3. 脚本问题
```bash
# 检查脚本完整性
./deploy.sh --help

# 手动运行子脚本
./scripts/quick-deploy.sh
```

### 调试模式
```bash
# 启用调试输出
set -x
./deploy.sh --mode=local
set +x
```

## 📈 性能优化

### 1. 本地部署优化
```bash
# 使用SSD存储
# 增加内存
# 优化Python环境
```

### 2. 系统部署优化
```bash
# 配置系统服务
# 设置自动启动
# 优化资源使用
```

### 3. Docker部署优化
```bash
# 使用多阶段构建
# 优化镜像大小
# 配置资源限制
```

## 🎯 最佳实践

### 1. 开发环境
- 使用 `--mode=local`
- 快速迭代和测试
- 本地虚拟环境

### 2. 测试环境
- 使用 `--mode=docker`
- 环境隔离
- 易于重置

### 3. 生产环境
- 使用 `--mode=system`
- 完整权限管理
- 系统服务配置

## 📚 相关文档

- **README.md** - 项目介绍
- **QUICK_DEPLOYMENT.md** - 快速部署指南
- **DEPLOYMENT_GUIDE.md** - 详细部署指南
- **SCRIPT_ANALYSIS.md** - 脚本分析报告

## 🔄 脚本维护

### 更新脚本
```bash
# 拉取最新代码
git pull origin main

# 更新脚本权限
chmod +x deploy.sh scripts/*.sh install.sh
```

### 添加新功能
1. 修改对应的子脚本
2. 更新统一部署脚本
3. 测试所有部署模式
4. 更新文档

---

**🎯 使用统一部署脚本，一个命令解决所有部署需求！**
