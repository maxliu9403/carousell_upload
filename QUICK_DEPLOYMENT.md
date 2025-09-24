# 🚀 快速部署指南

## 📋 部署方式对比

| 部署方式 | 适用场景 | 复杂度 | 推荐度 |
|---------|---------|--------|--------|
| 🖥️ 本地部署 | 开发测试 | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| 🐳 Docker部署 | 生产环境 | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| ☁️ 云服务器 | 远程部署 | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| 🏭 CI/CD | 自动化部署 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |

## 🖥️ 本地快速部署

### 一键部署脚本

```bash
# 下载并运行快速部署脚本
curl -fsSL https://raw.githubusercontent.com/your-org/carousell-uploader/main/scripts/quick-deploy.sh | bash

# 或手动运行
chmod +x scripts/quick-deploy.sh
./scripts/quick-deploy.sh
```

### 手动部署步骤

```bash
# 1. 克隆项目
git clone https://github.com/your-org/carousell-uploader.git
cd carousell-uploader

# 2. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows

# 3. 安装依赖
pip install -r requirements.txt
playwright install chromium

# 4. 配置设置
cp config/settings.example.yaml config/settings.yaml
# 编辑 config/settings.yaml

# 5. 运行程序
python -m cli.main
```

## 🐳 Docker 部署

### 一键Docker部署

```bash
# 运行Docker部署脚本
chmod +x scripts/docker-deploy.sh
./scripts/docker-deploy.sh
```

### 手动Docker部署

```bash
# 1. 构建镜像
docker build -t carousell-uploader .

# 2. 运行容器
docker run -it --rm \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  -e CAROUSELL_API_KEY="your_api_key" \
  -e CAROUSELL_API_PORT="54345" \
  carousell-uploader
```

### Docker Compose 部署

```bash
# 1. 创建环境变量文件
echo "CAROUSELL_API_KEY=your_api_key" > .env
echo "CAROUSELL_API_PORT=54345" >> .env

# 2. 启动服务
docker-compose up -d

# 3. 查看日志
docker-compose logs -f

# 4. 停止服务
docker-compose down
```

## ☁️ 云服务器部署

### Ubuntu/Debian 系统

```bash
# 1. 更新系统
sudo apt update && sudo apt upgrade -y

# 2. 安装必要软件
sudo apt install -y python3 python3-pip python3-venv git curl wget

# 3. 克隆项目
git clone https://github.com/your-org/carousell-uploader.git
cd carousell-uploader

# 4. 运行部署脚本
chmod +x scripts/quick-deploy.sh
./scripts/quick-deploy.sh

# 5. 配置系统服务
sudo cp carousell-uploader.service /etc/systemd/system/
sudo systemctl enable carousell-uploader
sudo systemctl start carousell-uploader
```

### CentOS/RHEL 系统

```bash
# 1. 更新系统
sudo yum update -y

# 2. 安装必要软件
sudo yum install -y python3 python3-pip git curl wget

# 3. 克隆项目
git clone https://github.com/your-org/carousell-uploader.git
cd carousell-uploader

# 4. 运行部署脚本
chmod +x scripts/quick-deploy.sh
./scripts/quick-deploy.sh
```

## 🏭 CI/CD 自动化部署

### GitHub Actions

创建 `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        playwright install chromium
    
    - name: Run tests
      run: pytest
    
    - name: Deploy to server
      run: |
        # 部署到服务器的命令
        echo "Deploying to production..."
```

### GitLab CI

创建 `.gitlab-ci.yml`:

```yaml
stages:
  - test
  - deploy

test:
  stage: test
  image: python:3.10
  script:
    - pip install -r requirements.txt
    - playwright install chromium
    - pytest

deploy:
  stage: deploy
  script:
    - echo "Deploying to production..."
  only:
    - main
```

## 🔧 环境配置

### 环境变量

```bash
# 必需的环境变量
export CAROUSELL_API_KEY="your_api_key"
export CAROUSELL_API_PORT="54345"

# 可选的环境变量
export CAROUSELL_REGION="SG"
export CAROUSELL_CATEGORY="sneakers"
export DEBUG="false"
export LOG_LEVEL="INFO"
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

## 📊 监控和日志

### 日志配置

```bash
# 查看实时日志
tail -f logs/carousell_uploader.log

# 查看Docker日志
docker-compose logs -f carousell-uploader

# 查看系统服务日志
sudo journalctl -u carousell-uploader -f
```

### 性能监控

```bash
# 监控资源使用
htop

# 监控Docker容器
docker stats carousell-uploader

# 监控磁盘使用
df -h
```

## 🛠️ 故障排除

### 常见问题

#### 1. 端口占用
```bash
# 检查端口占用
lsof -i :54345
netstat -tulpn | grep 54345

# 杀死占用进程
kill -9 <PID>
```

#### 2. 权限问题
```bash
# 修复权限
sudo chown -R $USER:$USER /path/to/project
chmod +x scripts/*.sh
```

#### 3. 依赖问题
```bash
# 重新安装依赖
pip install --upgrade pip
pip install --no-cache-dir -r requirements.txt
playwright install --with-deps chromium
```

#### 4. Docker问题
```bash
# 清理Docker
docker system prune -a

# 重新构建
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### 调试模式

```bash
# 启用调试模式
export DEBUG=1
export LOG_LEVEL=DEBUG
python -m cli.main

# Docker调试
docker run -it --rm \
  -e DEBUG=1 \
  -e LOG_LEVEL=DEBUG \
  carousell-uploader
```

## 📈 性能优化

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

## 🔒 安全配置

### 防火墙设置

```bash
# Ubuntu/Debian
sudo ufw allow 22
sudo ufw allow 54345
sudo ufw enable

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=22/tcp
sudo firewall-cmd --permanent --add-port=54345/tcp
sudo firewall-cmd --reload
```

### SSL/TLS 配置

```bash
# 使用Let's Encrypt
sudo apt install certbot
sudo certbot --nginx -d your-domain.com
```

## 📚 最佳实践

### 1. 版本控制
- 使用Git标签标记版本
- 保持主分支稳定
- 使用功能分支开发

### 2. 备份策略
- 定期备份配置文件
- 备份数据库和日志
- 使用版本控制管理配置

### 3. 监控告警
- 设置系统监控
- 配置日志告警
- 监控资源使用

### 4. 安全更新
- 定期更新依赖包
- 监控安全漏洞
- 及时应用安全补丁

---

## 🎯 快速开始检查清单

- [ ] 系统要求检查 (Python 3.8+, 4GB RAM)
- [ ] 克隆项目代码
- [ ] 创建虚拟环境
- [ ] 安装Python依赖
- [ ] 安装Playwright浏览器
- [ ] 配置设置文件
- [ ] 测试程序运行
- [ ] 配置日志记录
- [ ] 设置监控告警
- [ ] 备份重要数据

**🎉 完成以上步骤后，您就可以开始使用Carousell自动上传工具了！**
