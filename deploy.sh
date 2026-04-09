#!/bin/bash
# payment-system-integration 部署脚本

set -e

echo "🚀 开始部署 payment-system-integration..."

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装，请先安装Docker"
    exit 1
fi

# 检查docker-compose是否安装
if ! command -v docker-compose &> /dev/null; then
    echo "⚠️  docker-compose未安装，尝试使用docker compose"
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE="docker-compose"
fi

# 构建镜像
echo "📦 构建Docker镜像..."
$DOCKER_COMPOSE build

# 启动容器
echo "🚀 启动容器..."
$DOCKER_COMPOSE up -d

# 检查状态
echo "🔍 检查容器状态..."
sleep 3
docker ps | grep payment-system-integration

# 显示日志
echo "📋 容器日志:"
docker logs payment-system-integration --tail 10

echo "✅ payment-system-integration 部署完成!"
echo "🌐 访问地址: http://localhost:8080"
