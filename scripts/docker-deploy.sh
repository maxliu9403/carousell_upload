#!/bin/bash
# Carousell Uploader Docker 部署脚本

set -e

echo "🐳 Carousell Uploader Docker 部署脚本"
echo "===================================="

# 检查Docker是否安装
check_docker() {
    if command -v docker &> /dev/null; then
        DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | cut -d',' -f1)
        echo "✅ Docker版本: $DOCKER_VERSION"
    else
        echo "❌ 未找到Docker，请先安装Docker"
        exit 1
    fi
}

# 检查Docker Compose是否安装
check_docker_compose() {
    if command -v docker-compose &> /dev/null; then
        COMPOSE_VERSION=$(docker-compose --version | cut -d' ' -f3 | cut -d',' -f1)
        echo "✅ Docker Compose版本: $COMPOSE_VERSION"
    else
        echo "❌ 未找到Docker Compose，请先安装Docker Compose"
        exit 1
    fi
}

# 创建Dockerfile
create_dockerfile() {
    echo "📝 创建Dockerfile..."
    cat > Dockerfile << 'EOF'
FROM python:3.10-slim

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libxss1 \
    libxtst6 \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 安装Playwright浏览器
RUN playwright install chromium
RUN playwright install-deps chromium

# 复制项目文件
COPY . .

# 创建必要目录
RUN mkdir -p logs data screenshots

# 设置权限
RUN chmod +x scripts/*.sh

# 暴露端口
EXPOSE 8000

# 设置入口点
ENTRYPOINT ["python", "-m", "cli.main"]
EOF
    echo "✅ Dockerfile创建完成"
}

# 创建docker-compose.yml
create_docker_compose() {
    echo "📝 创建docker-compose.yml..."
    cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  carousell-uploader:
    build: .
    container_name: carousell-uploader
    volumes:
      - ./config:/app/config
      - ./data:/app/data
      - ./logs:/app/logs
      - ./screenshots:/app/screenshots
    environment:
      - CAROUSELL_API_KEY=${CAROUSELL_API_KEY:-your_api_key}
      - CAROUSELL_API_PORT=${CAROUSELL_API_PORT:-54345}
      - CAROUSELL_REGION=${CAROUSELL_REGION:-SG}
      - CAROUSELL_CATEGORY=${CAROUSELL_CATEGORY:-sneakers}
    restart: unless-stopped
    stdin_open: true
    tty: true

  # 可选：添加数据库服务
  # redis:
  #   image: redis:alpine
  #   container_name: carousell-redis
  #   ports:
  #     - "6379:6379"
  #   restart: unless-stopped
EOF
    echo "✅ docker-compose.yml创建完成"
}

# 创建.env文件
create_env() {
    echo "📝 创建.env文件..."
    if [ ! -f ".env" ]; then
        cat > .env << 'EOF'
# Carousell Uploader 环境变量
CAROUSELL_API_KEY=your_api_key
CAROUSELL_API_PORT=54345
CAROUSELL_REGION=SG
CAROUSELL_CATEGORY=sneakers

# 调试模式
DEBUG=false
LOG_LEVEL=INFO
EOF
        echo "✅ .env文件创建完成"
        echo "⚠️  请编辑 .env 文件配置您的设置"
    else
        echo "⚠️  .env文件已存在"
    fi
}

# 构建镜像
build_image() {
    echo "🔨 构建Docker镜像..."
    docker build -t carousell-uploader .
    echo "✅ Docker镜像构建完成"
}

# 运行容器
run_container() {
    echo "🚀 启动容器..."
    docker-compose up -d
    echo "✅ 容器启动完成"
}

# 显示状态
show_status() {
    echo ""
    echo "📊 容器状态:"
    docker-compose ps
    
    echo ""
    echo "📋 使用说明:"
    echo "1. 查看日志: docker-compose logs -f"
    echo "2. 进入容器: docker-compose exec carousell-uploader bash"
    echo "3. 停止容器: docker-compose down"
    echo "4. 重启容器: docker-compose restart"
    echo ""
}

# 主函数
main() {
    check_docker
    check_docker_compose
    create_dockerfile
    create_docker_compose
    create_env
    build_image
    run_container
    show_status
}

# 运行主函数
main "$@"
