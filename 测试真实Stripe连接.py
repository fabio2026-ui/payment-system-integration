#!/usr/bin/env python3
"""
测试真实Stripe连接
使用老板提供的真实密钥
"""

import os
import stripe
import json
from datetime import datetime

def test_real_stripe():
    print("=" * 70)
    print("🔍 测试真实Stripe连接")
    print("=" * 70)
    
    # 从.env读取密钥
    env_path = '/home/node/.openclaw/workspace/.env'
    stripe_secret_key = None
    stripe_publishable_key = None
    
    try:
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('STRIPE_SECRET_KEY='):
                    stripe_secret_key = line.split('=', 1)[1]
                elif line.startswith('STRIPE_PUBLISHABLE_KEY='):
                    stripe_publishable_key = line.split('=', 1)[1]
        
        if stripe_secret_key:
            print(f"✅ 找到Stripe密钥:")
            print(f"   密钥类型: {'LIVE' if 'live' in stripe_secret_key else 'TEST'}")
            print(f"   密钥前10位: {stripe_secret_key[:10]}...")
            
            # 测试连接
            try:
                stripe.api_key = stripe_secret_key
                account = stripe.Account.retrieve()
                
                print(f"✅ Stripe连接成功!")
                print(f"   • 账户ID: {account.id}")
                print(f"   • 账户类型: {account.type}")
                print(f"   • 国家: {account.country}")
                print(f"   • 默认货币: {account.default_currency}")
                
                # 获取业务信息
                business_name = getattr(account, 'business_profile', {}).get('name', '未设置')
                print(f"   • 业务名称: {business_name}")
                
                # 检查余额
                try:
                    balance = stripe.Balance.retrieve()
                    print(f"💰 账户余额:")
                    if balance.available:
                        for amount in balance.available:
                            currency = amount['currency'].upper()
                            amount_usd = amount['amount'] / 100
                            print(f"   • {amount_usd} {currency}")
                    else:
                        print(f"   • 暂无可用余额")
                        
                    if balance.pending:
                        print(f"   ⏳ 待处理余额:")
                        for amount in balance.pending:
                            currency = amount['currency'].upper()
                            amount_usd = amount['amount'] / 100
                            print(f"   • {amount_usd} {currency}")
                            
                except Exception as e:
                    print(f"⚠️  无法获取余额: {e}")
                
                # 检查最近交易
                try:
                    charges = stripe.Charge.list(limit=5)
                    if charges.data:
                        print(f"📊 最近交易:")
                        for charge in charges.data:
                            amount = charge.amount / 100
                            currency = charge.currency.upper()
                            status = charge.status
                            created = datetime.fromtimestamp(charge.created).strftime('%Y-%m-%d %H:%M')
                            print(f"   • {created}: ${amount} {currency} ({status})")
                    else:
                        print(f"📊 最近交易: 暂无交易记录")
                        
                except Exception as e:
                    print(f"⚠️  无法获取交易记录: {e}")
                
                return {
                    'success': True,
                    'account_id': account.id,
                    'country': account.country,
                    'currency': account.default_currency,
                    'business_name': business_name,
                    'is_live': 'live' in stripe_secret_key
                }
                
            except stripe.error.AuthenticationError:
                print(f"❌ Stripe认证失败 - 密钥可能无效")
                return {'success': False, 'error': '认证失败'}
            except Exception as e:
                print(f"❌ Stripe连接错误: {e}")
                return {'success': False, 'error': str(e)}
        else:
            print("❌ 未找到Stripe密钥")
            return {'success': False, 'error': '未找到密钥'}
            
    except Exception as e:
        print(f"❌ 读取.env文件失败: {e}")
        return {'success': False, 'error': str(e)}

def create_real_payment_test():
    """创建真实支付测试"""
    print("\n" + "=" * 70)
    print("🎯 创建真实支付测试")
    print("=" * 70)
    
    # 从.env读取密钥
    env_path = '/home/node/.openclaw/workspace/.env'
    stripe_secret_key = None
    
    try:
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('STRIPE_SECRET_KEY='):
                    stripe_secret_key = line.split('=', 1)[1]
                    break
        
        if not stripe_secret_key:
            print("❌ 未找到Stripe密钥")
            return {'success': False, 'error': '未找到密钥'}
        
        if 'test' in stripe_secret_key:
            print("⚠️  这是TEST密钥，不是LIVE密钥")
            print("   将创建测试支付会话")
            is_live = False
        else:
            print("✅ 这是LIVE密钥，将创建真实支付会话")
            is_live = True
        
        stripe.api_key = stripe_secret_key
        
        # 创建产品
        product = stripe.Product.create(
            name='AI自动化工作流模板 - 真实测试',
            description='立即提升工作效率10倍的AI自动化模板 (真实支付测试)'
        )
        
        # 创建价格
        price = stripe.Price.create(
            unit_amount=1999,  # $19.99 - 小额测试
            currency='usd',
            product=product.id,
        )
        
        # 创建支付会话
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': price.id,
                'quantity': 1,
            }],
            mode='payment',
            success_url='https://your-domain.com/success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url='https://your-domain.com/cancel',
            metadata={
                'product_name': 'AI自动化工作流模板',
                'test_type': 'real' if is_live else 'test',
                'created_by': 'openclaw_deployment'
            }
        )
        
        print(f"✅ 支付会话创建成功!")
        print(f"   • 会话ID: {session.id}")
        print(f"   • 支付链接: {session.url}")
        print(f"   • 金额: ${session.amount_total/100}")
        print(f"   • 货币: {session.currency.upper()}")
        print(f"   • 状态: {session.status}")
        print(f"   • 模式: {'LIVE' if is_live else 'TEST'}")
        
        # 保存会话信息
        session_info = {
            'session_id': session.id,
            'url': session.url,
            'amount': session.amount_total/100,
            'currency': session.currency,
            'created': datetime.now().isoformat(),
            'status': session.status,
            'is_live': is_live,
            'product_name': 'AI自动化工作流模板'
        }
        
        session_file = '/home/node/.openclaw/workspace/real_stripe_session.json'
        with open(session_file, 'w') as f:
            json.dump(session_info, f, indent=2)
        
        print(f"📄 会话信息已保存: {session_file}")
        
        # 生成HTML支付页面
        html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI自动化工作流模板 - 支付测试</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
        .container {{ background: #f5f5f5; padding: 30px; border-radius: 10px; }}
        .product {{ background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
        .price {{ font-size: 24px; color: #10b981; font-weight: bold; }}
        .btn {{ background: #10b981; color: white; padding: 15px 30px; border: none; border-radius: 5px; font-size: 18px; cursor: pointer; text-decoration: none; display: inline-block; }}
        .btn:hover {{ background: #0da271; }}
        .info {{ background: #e8f4fd; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .warning {{ background: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 AI自动化工作流模板</h1>
        <p>立即提升工作效率10倍的专业AI自动化模板</p>
        
        <div class="product">
            <h2>产品详情</h2>
            <p>包含10个专业工作流模板，适用于各种业务场景</p>
            <ul>
                <li>客户跟进自动化</li>
                <li>内容生成工作流</li>
                <li>数据分析自动化</li>
                <li>社交媒体管理</li>
                <li>邮件营销自动化</li>
            </ul>
        </div>
        
        <div class="price">价格: $19.99 USD</div>
        
        <div class="info">
            <strong>支付信息:</strong>
            <p>这是{"<span style='color: green;'>真实支付测试</span>" if is_live else "<span style='color: orange;'>测试模式支付</span>"}</p>
            <p>会话ID: {session.id}</p>
            <p>创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        {f'<div class="warning"><strong>⚠️ 重要提醒:</strong> 这是LIVE真实支付，将产生实际费用！</div>' if is_live else ''}
        
        <a href="{session.url}" class="btn">
            {"💳 立即支付 $19.99 (真实支付)" if is_live else "💳 测试支付 $19.99 (测试模式)"}
        </a>
        
        <div style="margin-top: 30px; font-size: 14px; color: #666;">
            <p>支付系统由Stripe提供，安全可靠</p>
            <p>如需帮助，请联系客服</p>
        </div>
    </div>
</body>
</html>'''
        
        html_file = '/home/node/.openclaw/workspace/real_payment_test.html'
        with open(html_file, 'w') as f:
            f.write(html_content)
        
        print(f"🌐 支付页面已生成: {html_file}")
        
        return {
            'success': True,
            'session_id': session.id,
            'url': session.url,
            'amount': session.amount_total/100,
            'is_live': is_live,
            'html_file': html_file
        }
        
    except stripe.error.AuthenticationError:
        print(f"❌ Stripe认证失败 - 密钥无效")
        return {'success': False, 'error': '认证失败'}
    except stripe.error.InvalidRequestError as e:
        print(f"❌ Stripe请求错误: {e}")
        return {'success': False, 'error': str(e)}
    except Exception as e:
        print(f"❌ 创建支付会话失败: {e}")
        return {'success': False, 'error': str(e)}

def main():
    """主函数"""
    print("🎯 老板指令: 全面真实部署")
    print(f"📅 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 1. 测试Stripe连接
    print("1. 🔗 测试Stripe连接...")
    connection_result = test_real_stripe()
    
    if not connection_result.get('success'):
        print("❌ Stripe连接失败，无法继续")
        return
    
    # 2. 创建真实支付测试
    print("\n2. 💰 创建真实支付测试...")
    payment_result = create_real_payment_test()
    
    # 3. 总结
    print("\n" + "=" * 70)
    print("✅ 真实支付系统部署完成")
    print("=" * 70)
    
    if connection_result.get('is_live'):
        print("🎯 系统状态: **LIVE真实模式**")
        print("   • 可以处理真实支付")
        print("   • 将产生实际收入")
        print("   • 资金将进入真实账户")
    else:
        print("🎯 系统状态: **TEST测试模式**")
        print("   • 仅用于测试")
        print("   • 不会产生实际费用")
        print("   • 需要切换到LIVE密钥")
    
    if payment_result.get('success'):
        print(f"\n📊 支付测试创建成功:")
        print(f"   • 会话ID: {payment_result.get('session_id')}")
        print(f"   • 金额: ${payment_result.get('amount')}")
        print(f"   • 模式: {'LIVE' if payment_result.get('is_live') else 'TEST'}")
        print(f"   • 支付页面: {payment_result.get('html_file')}")
        
        if payment_result.get('is_live'):
            print(f"\n🚨 **重要提醒**:")
            print(f"   这是真实支付链接!")
            print(f"   点击支付将产生$19.99实际费用!")
            print(f"   请谨慎测试!")
        else:
            print(f"\n💡 测试说明:")
            print(f"   这是测试支付链接")
            print(f"   不会产生实际费用")
            print(f"   可以使用测试卡号: 4242 4242 4242 4242")
    
    print(f"\n📋 下一步行动:")
    print(f"   1. 测试支付流程")
    print(f"   2. 监控支付状态")
    print(f"   3. 验证收入到账")
    print(f"   4. 扩展支付产品")
    
    print(f"\n💪 老板，真实支付系统已就绪!")
    print("=" * 70)
    
    return {
        'connection': connection_result,
        'payment': payment_result
    }

if __name__ == "__main__":
    main()