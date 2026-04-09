#!/bin/bash
# payment-system-integration - 安全扫描脚本

set -e

echo "🔒 开始安全扫描 payment-system-integration..."

# 安装安全工具
echo "📦 安装安全工具..."
pip install safety bandit

# 依赖安全扫描
echo "📊 扫描依赖安全..."
safety check -r requirements.txt

# 代码安全扫描
echo "📊 扫描代码安全..."
bandit -r . -f json -o bandit_report.json
echo "✅ 代码安全扫描完成"

# 生成安全报告
echo "📋 生成安全报告..."
cat > security_report.md << EOF
# payment-system-integration 安全扫描报告
生成时间: $(date)

## 扫描结果
- 依赖安全扫描: ✅ 完成
- 代码安全扫描: ✅ 完成

## 建议
1. 定期更新依赖包
2. 修复发现的安全问题
3. 启用自动安全扫描

## 下一步
- 查看详细报告: bandit_report.json
- 修复安全问题
- 配置CI/CD安全扫描
EOF

echo "✅ 安全扫描完成"
