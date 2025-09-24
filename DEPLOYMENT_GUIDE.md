# 🚀 Carousell Uploader 快速部署指南

## 📋 项目信息

- **项目地址**: https://github.com/maxliu9403/carousell_upload
- **项目名称**: Carousell Uploader
- **部署脚本**: `carousell-uploader/install.sh`

## 🎯 一键部署

### 方式一：使用安装脚本 (推荐)

```bash
# 下载并运行一键安装脚本
curl -fsSL https://raw.githubusercontent.com/maxliu9403/carousell_upload/main/install.sh | bash
```

### 方式二：手动部署

```bash
# 1. 克隆项目
git clone https://github.com/maxliu9403/carousell_upload.git
cd carousell_upload

# 2. 运行快速部署脚本
chmod +x scripts/quick-deploy.sh
./scripts/quick-deploy.sh
```

### 方式三：Docker部署

```bash
# 1. 克隆项目
git clone https://github.com/maxliu9403/carousell_upload.git
cd carousell_upload

# 2. 运行Docker部署脚本
chmod +x scripts/docker-deploy.sh
./scripts/docker-deploy.sh
```

## 🖥️ 系统要求

### 最低要求
- **Python**: 3.8+ (推荐 3.10+)
- **内存**: 4GB RAM
- **存储**: 1GB 可用空间
- **操作系统**: Windows, macOS, Linux

### 推荐配置
- **Python**: 3.10+
- **内存**: 8GB RAM
- **存储**: 5GB 可用空间
- **CPU**: 4核心以上

## 📦 安装步骤详解

### 1. 环境准备

#### Ubuntu/Debian 系统
```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装必要软件
sudo apt install -y python3 python3-pip python3-venv git curl wget
```

#### CentOS/RHEL 系统
```bash
# 更新系统
sudo yum update -y

# 安装必要软件
sudo yum install -y python3 python3-pip git curl wget
```

#### macOS 系统
```bash
# 安装Homebrew (如果未安装)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安装Python
brew install python3
```

#### Windows 系统
```powershell
# 使用Chocolatey安装Python
choco install python3

# 或从官网下载安装
# https://python.org/downloads/
```

### 2. 项目部署

```bash
# 克隆项目
git clone https://github.com/maxliu9403/carousell_upload.git
cd carousell_upload

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 安装Playwright浏览器
playwright install chromium
```

### 3. 配置设置

```bash
# 复制配置文件
cp config/settings.example.yaml config/settings.yaml

# 编辑配置文件
nano config/settings.yaml
```

### 4. 运行程序

```bash
# 运行主程序
python -m cli.main

# 或使用命令行参数
python -m cli.cli --help
```

## 🐳 Docker 部署

### 使用Docker Compose

```bash
# 1. 克隆项目
git clone https://github.com/maxliu9403/carousell_upload.git
cd carousell_upload

# 2. 创建环境变量文件
cat > .env << EOF
CAROUSELL_API_KEY=your_api_key
CAROUSELL_API_PORT=54345
CAROUSELL_REGION=SG
CAROUSELL_CATEGORY=sneakers
EOF

# 3. 启动服务
docker-compose up -d

# 4. 查看日志
docker-compose logs -f
```

### 手动Docker部署

```bash
# 构建镜像
docker build -t carousell-uploader .

# 运行容器
docker run -it --rm \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  -e CAROUSELL_API_KEY="your_api_key" \
  -e CAROUSELL_API_PORT="54345" \
  carousell-uploader
```

## ☁️ 云服务器部署

### 阿里云/腾讯云/华为云

```bash
# 1. 连接服务器
ssh root@your-server-ip

# 2. 更新系统
apt update && apt upgrade -y

# 3. 安装必要软件
apt install -y python3 python3-pip python3-venv git curl wget

# 4. 克隆项目
git clone https://github.com/maxliu9403/carousell_upload.git
cd carousell_upload

# 5. 运行部署脚本
chmod +x scripts/quick-deploy.sh
./scripts/quick-deploy.sh

# 6. 配置系统服务
sudo cp carousell-uploader.service /etc/systemd/system/
sudo systemctl enable carousell-uploader
sudo systemctl start carousell-uploader
```

### AWS EC2

```bash
# 1. 连接EC2实例
ssh -i your-key.pem ec2-user@your-ec2-ip

# 2. 安装Python
sudo yum install -y python3 python3-pip git

# 3. 克隆项目
git clone https://github.com/maxliu9403/carousell_upload.git
cd carousell_upload

# 4. 运行部署脚本
chmod +x scripts/quick-deploy.sh
./scripts/quick-deploy.sh
```

## 🔧 配置说明

### 环境变量

```bash
# 必需配置
export CAROUSELL_API_KEY="your_api_key"
export CAROUSELL_API_PORT="54345"

# 可选配置
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

## 🛠️ 故障排除

### 常见问题

#### 1. Python版本问题
```bash
# 检查Python版本
python3 --version

# 如果版本过低，升级Python
# Ubuntu/Debian
sudo apt install python3.10

# CentOS/RHEL
sudo yum install python3.10
```

#### 2. 依赖安装失败
```bash
# 升级pip
pip install --upgrade pip

# 使用国内镜像
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# 清理缓存
pip cache purge
```

#### 3. Playwright安装失败
```bash
# 安装系统依赖
playwright install --with-deps chromium

# 或设置环境变量
PLAYWRIGHT_BROWSERS_PATH=0 playwright install chromium
```

#### 4. 权限问题
```bash
# 修复权限
sudo chown -R $USER:$USER /path/to/project
chmod +x scripts/*.sh
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

### SSL/TLS配置

```bash
# 使用Let's Encrypt
sudo apt install certbot
sudo certbot --nginx -d your-domain.com
```

## 📈 监控和维护

### 日志管理

```bash
# 查看实时日志
tail -f logs/carousell_uploader.log

# 查看Docker日志
docker-compose logs -f

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

## 🎯 快速检查清单

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

## 📞 技术支持

- 🐛 **问题反馈**: [GitHub Issues](https://github.com/maxliu9403/carousell_upload/issues)
- 💬 **讨论交流**: [GitHub Discussions](https://github.com/maxliu9403/carousell_upload/discussions)
- 📖 **项目文档**: [README.md](README.md)
- 🚀 **快速部署**: [QUICK_DEPLOYMENT.md](QUICK_DEPLOYMENT.md)

---

**🎉 完成以上步骤后，您就可以开始使用Carousell自动上传工具了！**
