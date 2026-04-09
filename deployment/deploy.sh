#!/bin/bash
# payment-system-integration - 部署脚本

set -e

echo "🚀 开始部署 payment-system-integration..."

# 构建Docker镜像
echo "📦 构建Docker镜像..."
docker build -t payment-system-integration:latest -f Dockerfile.production .

# 启动服务
echo "🚀 启动服务..."
docker-compose -f docker-compose.production.yml up -d

# 健康检查
echo "🏥 执行健康检查..."
sleep 10
if curl -s http://localhost:8000/health | grep -q "healthy"; then
    echo "✅ 部署成功!"
    echo "📊 服务地址: http://localhost:8000"
    echo "📊 健康检查: http://localhost:8000/health"
    echo "📊 API文档: http://localhost:8000/docs"
else
    echo "❌ 部署失败，请检查日志"
    docker-compose -f docker-compose.production.yml logs
    exit 1
fi
