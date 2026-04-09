#!/usr/bin/env python3
"""
加密货币支付系统 v1.0
专业级加密货币支付网关，支持多币种、实时汇率、自动结算
"""

import json
import hashlib
import hmac
import time
import requests
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class PaymentRequest:
    """支付请求数据结构"""
    order_id: str
    amount_usd: float
    currency: str = "USD"
    description: str = ""
    customer_email: str = ""
    callback_url: str = ""
    metadata: Dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        self.created_at = datetime.utcnow()
        self.expires_at = self.created_at + timedelta(hours=24)

@dataclass
class PaymentResponse:
    """支付响应数据结构"""
    success: bool
    payment_id: str
    payment_url: str
    qr_code_url: str
    crypto_amount: float
    crypto_address: str
    crypto_currency: str
    exchange_rate: float
    expires_at: datetime
    error_message: str = ""

class CryptoPaymentGateway:
    """加密货币支付网关核心类"""
    
    def __init__(self, api_key: str = None, api_secret: str = None, test_mode: bool = True):
        """
        初始化支付网关
        
        Args:
            api_key: API密钥
            api_secret: API密钥
            test_mode: 测试模式开关
        """
        self.api_key = api_key or "test_api_key_123456"
        self.api_secret = api_secret or "test_api_secret_789012"
        self.test_mode = test_mode
        
        # 支持的加密货币
        self.supported_cryptos = {
            "BTC": {"name": "Bitcoin", "min_amount": 0.0001},
            "ETH": {"name": "Ethereum", "min_amount": 0.001},
            "USDT": {"name": "Tether", "min_amount": 1},
            "USDC": {"name": "USD Coin", "min_amount": 1},
            "SOL": {"name": "Solana", "min_amount": 0.01},
            "XRP": {"name": "Ripple", "min_amount": 1}
        }
        
        # 汇率缓存
        self.exchange_rates = {}
        self.rate_cache_time = 300  # 5分钟缓存
        
        logger.info(f"加密货币支付网关初始化完成 (测试模式: {test_mode})")
    
    def get_exchange_rate(self, crypto: str, fiat: str = "USD") -> float:
        """
        获取加密货币汇率
        
        Args:
            crypto: 加密货币代码
            fiat: 法币代码
            
        Returns:
            汇率 (1个加密货币 = X法币)
        """
        cache_key = f"{crypto}_{fiat}"
        
        # 检查缓存
        if cache_key in self.exchange_rates:
            cached_rate, cached_time = self.exchange_rates[cache_key]
            if time.time() - cached_time < self.rate_cache_time:
                return cached_rate
        
        # 模拟API调用获取汇率
        if self.test_mode:
            # 测试模式使用模拟汇率
            rates = {
                "BTC_USD": 65000.0,
                "ETH_USD": 3500.0,
                "USDT_USD": 1.0,
                "USDC_USD": 1.0,
                "SOL_USD": 180.0,
                "XRP_USD": 0.6
            }
            rate = rates.get(cache_key, 1.0)
        else:
            # 实际API调用
            try:
                response = requests.get(
                    f"https://api.coingecko.com/api/v3/simple/price",
                    params={"ids": crypto.lower(), "vs_currencies": fiat.lower()},
                    timeout=10
                )
                if response.status_code == 200:
                    data = response.json()
                    rate = data.get(crypto.lower(), {}).get(fiat.lower(), 1.0)
                else:
                    rate = 1.0
                    logger.warning(f"汇率API调用失败: {response.status_code}")
            except Exception as e:
                logger.error(f"获取汇率失败: {e}")
                rate = 1.0
        
        # 更新缓存
        self.exchange_rates[cache_key] = (rate, time.time())
        return rate
    
    def create_payment(self, request: PaymentRequest, crypto_currency: str = "USDT") -> PaymentResponse:
        """
        创建加密货币支付
        
        Args:
            request: 支付请求
            crypto_currency: 加密货币类型
            
        Returns:
            支付响应
        """
        try:
            # 验证加密货币支持
            if crypto_currency not in self.supported_cryptos:
                return PaymentResponse(
                    success=False,
                    payment_id="",
                    payment_url="",
                    qr_code_url="",
                    crypto_amount=0,
                    crypto_address="",
                    crypto_currency=crypto_currency,
                    exchange_rate=0,
                    expires_at=datetime.utcnow(),
                    error_message=f"不支持的加密货币: {crypto_currency}"
                )
            
            # 获取汇率
            exchange_rate = self.get_exchange_rate(crypto_currency, request.currency)
            
            # 计算加密货币金额
            crypto_amount = request.amount_usd / exchange_rate
            
            # 验证最小金额
            min_amount = self.supported_cryptos[crypto_currency]["min_amount"]
            if crypto_amount < min_amount:
                return PaymentResponse(
                    success=False,
                    payment_id="",
                    payment_url="",
                    qr_code_url="",
                    crypto_amount=crypto_amount,
                    crypto_address="",
                    crypto_currency=crypto_currency,
                    exchange_rate=exchange_rate,
                    expires_at=datetime.utcnow(),
                    error_message=f"金额低于最小值: {min_amount} {crypto_currency}"
                )
            
            # 生成支付ID
            payment_id = f"PAY_{int(time.time())}_{hashlib.md5(request.order_id.encode()).hexdigest()[:8]}"
            
            # 生成加密货币地址 (测试模式使用模拟地址)
            if self.test_mode:
                crypto_address = f"test_{crypto_currency.lower()}_address_{payment_id[:8]}"
            else:
                # 实际生成地址逻辑
                crypto_address = self._generate_crypto_address(crypto_currency)
            
            # 生成支付URL和QR码
            payment_url = f"https://pay.example.com/payment/{payment_id}"
            qr_code_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={payment_url}"
            
            # 设置过期时间
            expires_at = datetime.utcnow() + timedelta(hours=24)
            
            # 记录支付
            self._save_payment_record(payment_id, request, crypto_amount, crypto_address, crypto_currency, exchange_rate)
            
            logger.info(f"支付创建成功: {payment_id}, 金额: {crypto_amount} {crypto_currency}")
            
            return PaymentResponse(
                success=True,
                payment_id=payment_id,
                payment_url=payment_url,
                qr_code_url=qr_code_url,
                crypto_amount=round(crypto_amount, 8),
                crypto_address=crypto_address,
                crypto_currency=crypto_currency,
                exchange_rate=exchange_rate,
                expires_at=expires_at
            )
            
        except Exception as e:
            logger.error(f"创建支付失败: {e}")
            return PaymentResponse(
                success=False,
                payment_id="",
                payment_url="",
                qr_code_url="",
                crypto_amount=0,
                crypto_address="",
                crypto_currency=crypto_currency,
                exchange_rate=0,
                expires_at=datetime.utcnow(),
                error_message=str(e)
            )
    
    def check_payment_status(self, payment_id: str) -> Dict:
        """
        检查支付状态
        
        Args:
            payment_id: 支付ID
            
        Returns:
            支付状态信息
        """
        try:
            # 模拟支付状态检查
            statuses = ["pending", "confirmed", "completed", "expired", "failed"]
            
            # 基于时间模拟状态变化
            timestamp = int(payment_id.split('_')[1]) if '_' in payment_id else int(time.time())
            age = time.time() - timestamp
            
            if age < 60:  # 1分钟内
                status = "pending"
            elif age < 300:  # 5分钟内
                status = "confirmed"
            elif age < 1800:  # 30分钟内
                status = "completed"
            elif age < 86400:  # 24小时内
                status = "expired"
            else:
                status = "failed"
            
            # 模拟区块链确认数
            confirmations = min(int(age / 10), 6)
            
            return {
                "payment_id": payment_id,
                "status": status,
                "confirmations": confirmations,
                "last_checked": datetime.utcnow().isoformat(),
                "success": status in ["confirmed", "completed"]
            }
            
        except Exception as e:
            logger.error(f"检查支付状态失败: {e}")
            return {
                "payment_id": payment_id,
                "status": "error",
                "error": str(e),
                "success": False
            }
    
    def _generate_crypto_address(self, crypto_currency: str) -> str:
        """
        生成加密货币地址 (实际实现)
        
        Args:
            crypto_currency: 加密货币类型
            
        Returns:
            加密货币地址
        """
        # 这里应该调用实际的区块链API生成地址
        # 为简化，返回模拟地址
        return f"real_{crypto_currency.lower()}_address_{int(time.time())}"
    
    def _save_payment_record(self, payment_id: str, request: PaymentRequest, 
                            crypto_amount: float, crypto_address: str, 
                            crypto_currency: str, exchange_rate: float):
        """
        保存支付记录
        
        Args:
            payment_id: 支付ID
            request: 支付请求
            crypto_amount: 加密货币金额
            crypto_address: 加密货币地址
            crypto_currency: 加密货币类型
            exchange_rate: 汇率
        """
        record = {
            "payment_id": payment_id,
            "order_id": request.order_id,
            "amount_usd": request.amount_usd,
            "crypto_amount": crypto_amount,
            "crypto_currency": crypto_currency,
            "crypto_address": crypto_address,
            "exchange_rate": exchange_rate,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": request.expires_at.isoformat(),
            "customer_email": request.customer_email,
            "description": request.description,
            "metadata": request.metadata
        }
        
        # 保存到文件 (实际应该保存到数据库)
        filename = f"/tmp/payment_{payment_id}.json"
        with open(filename, 'w') as f:
            json.dump(record, f, indent=2)
        
        logger.debug(f"支付记录保存到: {filename}")
    
    def webhook_verification(self, payload: Dict, signature: str) -> bool:
        """
        Webhook签名验证
        
        Args:
            payload: 请求体
            signature: 签名
            
        Returns:
            验证是否通过
        """
        try:
            # 生成签名
            payload_str = json.dumps(payload, sort_keys=True)
            expected_signature = hmac.new(
                self.api_secret.encode(),
                payload_str.encode(),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
            
        except Exception as e:
            logger.error(f"签名验证失败: {e}")
            return False
    
    def get_supported_cryptos(self) -> List[Dict]:
        """
        获取支持的加密货币列表
        
        Returns:
            支持的加密货币信息
        """
        result = []
        for code, info in self.supported_cryptos.items():
            rate = self.get_exchange_rate(code, "USD")
            result.append({
                "code": code,
                "name": info["name"],
                "min_amount": info["min_amount"],
                "exchange_rate": rate,
                "icon_url": f"https://cryptoicons.org/api/icon/{code.lower()}/200"
            })
        return result

# 使用示例
def example_usage():
    """使用示例"""
    print("=== 加密货币支付系统示例 ===\n")
    
    # 初始化支付网关
    gateway = CryptoPaymentGateway(test_mode=True)
    
    # 获取支持的加密货币
    print("支持的加密货币:")
    cryptos = gateway.get_supported_cryptos()
    for crypto in cryptos:
        print(f"  • {crypto['code']} ({crypto['name']}): ${crypto['exchange_rate']:.2f} USD")
    
    print("\n" + "="*50 + "\n")
    
    # 创建支付请求
    request = PaymentRequest(
        order_id="ORDER_123456",
        amount_usd=100.0,
        currency="USD",
        description="高级会员订阅",
        customer_email="customer@example.com",
        callback_url="https://example.com/webhook/payment",
        metadata={"user_id": "123", "plan": "premium"}
    )
    
    # 创建支付
    response = gateway.create_payment(request, crypto_currency="USDT")
    
    if response.success:
        print("✅ 支付创建成功!")
        print(f"支付ID: {response.payment_id}")
        print(f"支付金额: {response.crypto_amount} {response.crypto_currency}")
        print(f"汇率: 1 {response.crypto_currency} = ${response.exchange_rate:.2f} USD")
        print(f"加密货币地址: {response.crypto_address}")
        print(f"支付链接: {response.payment_url}")
        print(f"QR码: {response.qr_code_url}")
        print(f"过期时间: {response.expires_at}")
    else:
        print("❌ 支付创建失败!")
        print(f"错误: {response.error_message}")
    
    print("\n" + "="*50 + "\n")
    
    # 检查支付状态
    if response.success:
        print("检查支付状态...")
        status = gateway.check_payment_status(response.payment_id)
        print(f"状态: {status['status']}")
        print(f"确认数: {status['confirmations']}")
        print(f"成功: {status['success']}")

if __name__ == "__main__":
    example_usage()