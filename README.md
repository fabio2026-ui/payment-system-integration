# payment-system-integration

支付集成 - 自动化部署

## 文件说明
## 📁 项目文件列表

- `24小时收入监控.py`
- `clean_simulated_data.py`
- `24小时收入监控仪表板.html`
- `测试真实Stripe连接.py`
- `checkout-server.py`
- `crypto_payment_page.html`
- `crypto_payment_page_professional.html`
- `optimized_payment_page.html`
- `download_instructions.html`
- `payment_integration.json`
- `simple_payment_hub.json`
- `ultimate_payment_link.json`
- `secure_payment_config.md`
- `namecheap_dns_config.md`
- `crypto_payment_integration.md`
- `正式支付系统配置完成.md`
- `统一支付中枢系统.py`
- `payment_hub_report.md`
- `accelerated_deliverables/crypto_payment_config.json`
- `accelerated_deliverables/crypto_payment_system.py`

这是一个自动化生成的GitHub仓库。

## 部署状态
- ✅ 仓库创建完成
- ⚡ 文件准备中
- 🚀 即将推送完整项目

## 联系
- GitHub: [fabio2026-ui](https://github.com/fabio2026-ui)
- Email: fufansong@gmail.com

## 🐳 Docker 部署
## 🧪 测试
## 📊 监控和告警

### 监控架构

项目使用完整的监控栈:
- **Prometheus**: 指标收集和存储
- **Grafana**: 数据可视化和仪表板
- **Node Exporter**: 系统指标收集
- **cAdvisor**: 容器指标收集
- **Alertmanager**: 告警管理

### 快速开始

```bash
# 启动所有服务（包括监控）
docker-compose up -d

# 访问监控界面
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3000 (admin/admin)
# cAdvisor: http://localhost:8080
```

### 关键指标

#### 服务健康
- **服务状态**: `up{job="payment-system-integration"}`
- **请求率**: `rate(http_requests_total[5m])`
- **错误率**: `rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])`
- **响应时间**: `histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))`

#### 资源使用
- **内存使用**: `container_memory_usage_bytes{container_label_com_docker_compose_service="payment-system-integration"}`
- **CPU使用**: `rate(container_cpu_usage_seconds_total{container_label_com_docker_compose_service="payment-system-integration"}[5m])`
- **磁盘空间**: `node_filesystem_avail_bytes{mountpoint="/"}`

### 告警规则

#### 关键告警
1. **服务宕机**: 服务停止超过1分钟
2. **高错误率**: 错误率超过5%持续2分钟
3. **高延迟**: 95th percentile延迟超过1秒
4. **高内存使用**: 内存使用超过80%限制
5. **高CPU使用**: CPU使用超过80%

#### 告警通知
告警通过以下渠道发送:
- **电子邮件**: 配置在Alertmanager中
- **Slack**: 集成Slack webhook
- **PagerDuty**: 集成PagerDuty
- **Webhook**: 自定义webhook端点

### Grafana仪表板

预配置的仪表板包含:
1. **服务概览**: 关键指标概览
2. **性能分析**: 详细的性能指标
3. **资源监控**: CPU、内存、磁盘使用
4. **业务指标**: 业务相关指标

### 性能优化

#### Nginx配置
- **Gzip压缩**: 减少传输大小
- **缓存控制**: 静态资源缓存
- **连接池**: 保持活动连接
- **超时设置**: 合理的超时配置

#### 数据库优化
- **连接池**: 最小5个，最大20个连接
- **查询超时**: 30秒查询超时
- **索引优化**: 自动索引建议

#### 缓存策略
- **Redis缓存**: 分布式缓存
- **默认TTL**: 5分钟缓存时间
- **缓存失效**: 智能缓存失效策略

### 性能测试

运行性能测试:
```bash
# 安装性能测试工具
pip install locust

# 运行性能测试
cd performance
python performance_test.py

# 使用Locust进行负载测试
locust -f performance/locustfile.py
```

### 监控最佳实践

1. **指标命名**: 使用一致的命名约定
2. **标签使用**: 使用有意义的标签
3. **告警阈值**: 设置合理的告警阈值
4. **仪表板设计**: 设计清晰的仪表板
5. **文档化**: 记录监控配置和告警规则

### 故障排除

#### 常见问题
1. **指标缺失**: 检查服务是否暴露/metrics端点
2. **告警不触发**: 检查Prometheus规则配置
3. **仪表板不显示数据**: 检查数据源配置
4. **高延迟**: 检查数据库查询和网络延迟

#### 调试命令
```bash
# 检查Prometheus目标
curl http://localhost:9090/api/v1/targets

# 检查告警规则
curl http://localhost:9090/api/v1/rules

# 检查Grafana数据源
curl -u admin:admin http://localhost:3000/api/datasources
```

### 扩展监控

#### 业务指标
- **收入指标**: 实时收入跟踪
- **用户指标**: 活跃用户、留存率
- **性能指标**: 关键业务路径性能

#### 安全监控
- **安全事件**: 登录失败、可疑活动
- **合规监控**: 数据保护合规性
- **漏洞扫描**: 定期安全扫描

#### 成本监控
- **云成本**: AWS/Azure/GCP成本
- **资源成本**: 计算、存储、网络成本
- **优化建议**: 成本优化建议


### 运行测试

```bash
# 安装测试依赖
pip install pytest pytest-cov

# 运行所有测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=src --cov-report=html

# 运行特定测试文件
pytest tests/test_payment_system_integration.py

# 运行集成测试
pytest tests/test_integration_payment_system_integration.py -v
```

### 测试覆盖率

项目使用pytest-cov进行测试覆盖率统计。目标覆盖率:

- **单元测试**: ≥80%
- **集成测试**: ≥70%
- **总体覆盖率**: ≥75%

### 测试类型

1. **单元测试**: 测试单个函数和类
2. **集成测试**: 测试组件之间的交互
3. **端到端测试**: 测试完整工作流程
4. **性能测试**: 测试系统性能
5. **安全测试**: 测试安全漏洞

### 持续集成

GitHub Actions自动运行测试:
- 每次推送到main分支
- 每次拉取请求
- 每天凌晨自动运行

### 测试报告

测试报告可在以下位置查看:
- **GitHub Actions**: 工作流运行详情
- **Codecov**: 代码覆盖率报告
- **测试产物**: HTML覆盖率报告

### 测试最佳实践

- 每个测试应该独立运行
- 使用fixture进行测试数据准备
- 模拟外部依赖
- 测试边界情况和错误场景
- 保持测试快速运行

## 📦 GitHub Container Registry

### 自动构建的容器镜像

每次推送到main分支时，GitHub Actions会自动构建并推送Docker镜像到GitHub Container Registry。

**镜像地址**: `ghcr.io/fabio2026-ui/payment-system-integration:latest`

### 拉取和使用镜像

```bash
# 拉取最新镜像
docker pull ghcr.io/fabio2026-ui/payment-system-integration:latest

# 运行容器
docker run -d -p 8080:8000 --name payment-system-integration ghcr.io/fabio2026-ui/payment-system-integration:latest

# 使用docker-compose
version: '3.8'
services:
  payment-system-integration:
    image: ghcr.io/fabio2026-ui/payment-system-integration:latest
    ports:
      - "8080:8000"
```

### 手动构建和推送

```bash
# 登录到GitHub Container Registry
echo ${{ secrets.GITHUB_TOKEN }} | docker login ghcr.io -u ${{ github.actor }} --password-stdin

# 构建镜像
docker build -t ghcr.io/fabio2026-ui/payment-system-integration:latest .

# 推送镜像
docker push ghcr.io/fabio2026-ui/payment-system-integration:latest
```


### 快速开始

1. **克隆仓库**
   ```bash
   git clone https://github.com/fabio2026-ui/payment-system-integration.git
   cd payment-system-integration
   ```

2. **使用Docker部署**
   ```bash
   # 方法1: 使用部署脚本
   ./deploy.sh
   
   # 方法2: 手动部署
   docker-compose build
   docker-compose up -d
   ```

3. **访问应用**
   - 本地访问: http://localhost:8080
   - 容器状态: `docker ps | grep payment-system-integration`
   - 查看日志: `docker logs payment-system-integration`

### 管理命令

```bash
# 停止容器
docker-compose down

# 重启容器
docker-compose restart

# 查看日志
docker-compose logs -f

# 进入容器
docker exec -it payment-system-integration bash
```

### 生产环境部署

对于生产环境，建议使用:
- **Docker Swarm** 或 **Kubernetes** 进行容器编排
- **Traefik** 或 **Nginx** 作为反向代理
- **Let's Encrypt** 进行SSL证书管理
