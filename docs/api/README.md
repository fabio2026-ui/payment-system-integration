# payment-system-integration API 文档


## 💳 API 文档

### 基础信息
- **API 版本**: v1.0.0
- **生产环境**: https://api.payment-system.com/v1
- **开发环境**: http://localhost:8000/v1
- **认证方式**: API Key

### 快速开始

```bash
# 设置API密钥
export API_KEY="your_api_key_here"

# 创建支付
curl -X POST https://api.payment-system.com/v1/payments/create \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 99.99,
    "currency": "USD",
    "payment_method": "stripe",
    "customer_email": "customer@example.com",
    "description": "Premium subscription"
  }'
```

### API 端点

#### 创建支付
```
POST /payments/create
```
创建新的支付请求。

**请求体**:
- `amount`: 金额 (必须)
- `currency`: 货币代码 (必须)
- `payment_method`: 支付方式 (必须)
- `customer_email`: 客户邮箱
- `description`: 支付描述
- `metadata`: 自定义元数据

#### 获取支付状态
```
GET /payments/{payment_id}
```
根据ID获取支付状态。

#### 支付Webhook
```
POST /payments/webhook
```
处理支付网关的webhook事件。

#### 获取可用网关
```
GET /gateways
```
获取可用的支付网关列表。

#### 获取汇率
```
GET /currencies
```
获取当前货币汇率。

### 支付流程

1. **创建支付**: 客户端调用 `/payments/create`
2. **重定向用户**: 返回支付URL，重定向用户
3. **支付完成**: 用户在支付网关完成支付
4. **Webhook通知**: 支付网关发送webhook到 `/payments/webhook`
5. **状态更新**: 支付状态更新，通知客户端

### 支持的支付方式

#### Stripe
- 信用卡/借记卡
- Apple Pay / Google Pay
- SEPA直接借记
- 支付宝/微信支付

#### PayPal
- PayPal账户支付
- 信用卡通过PayPal
- Venmo (美国)

#### 加密货币
- Bitcoin (BTC)
- Ethereum (ETH)
- USDC / USDT
- 其他ERC-20代币

#### 银行转账
- SEPA (欧洲)
- ACH (美国)
- 国际电汇

### 安全特性

- **PCI DSS合规**: 符合支付卡行业数据安全标准
- **端到端加密**: 所有支付数据加密传输
- **欺诈检测**: 实时欺诈检测系统
- **3D Secure**: 支持3D Secure 2.0
- **令牌化**: 支付信息令牌化存储

### 测试环境

**测试信用卡号**:
- `4242 4242 4242 4242` - Visa (成功)
- `4000 0000 0000 0002` - Visa (失败)
- `5555 5555 5555 4444` - Mastercard (成功)

**测试API密钥**:
- 开发环境: `test_sk_development_123456`
- 沙盒环境: `test_sk_sandbox_789012`

### 集成示例

#### Python
```python
from payment_sdk import PaymentClient

client = PaymentClient(api_key="your_api_key")
payment = client.create_payment(
    amount=99.99,
    currency="USD",
    payment_method="stripe"
)
print(f"Payment URL: {payment['payment_url']}")
```

#### JavaScript
```javascript
import { PaymentClient } from 'payment-sdk';

const client = new PaymentClient({ apiKey: 'your_api_key' });
const payment = await client.createPayment({
  amount: 99.99,
  currency: 'USD',
  paymentMethod: 'stripe'
});
console.log(`Payment URL: ${payment.payment_url}`);
```

### 监控和日志

- **实时监控**: 支付成功率、失败率、平均处理时间
- **详细日志**: 所有API请求和响应日志
- **警报系统**: 异常支付活动警报
- **审计跟踪**: 完整的支付审计跟踪

### OpenAPI 规范

完整的OpenAPI规范可在以下位置获取:
- [OpenAPI JSON](https://api.payment-system.com/v1/openapi.json)
- [Swagger UI](https://api.payment-system.com/v1/docs)
- [ReDoc](https://api.payment-system.com/v1/redoc)
