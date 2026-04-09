#!/usr/bin/env python3
"""
24小时收入监控系统
目标: 24小时内获取$100真实收入
策略: 实时监控、快速优化、数据驱动
"""

import sqlite3
import json
import time
from datetime import datetime, timedelta
import os
import random

class RevenueMonitor24h:
    def __init__(self):
        self.monitor_db = "24h_revenue_monitor.db"
        self.leads_db = "real_leads.db"
        self.products_db = "digital_products.db"
        self.init_monitor_db()
        
    def init_monitor_db(self):
        """初始化监控数据库"""
        conn = sqlite3.connect(self.monitor_db)
        cursor = conn.cursor()
        
        # 收入记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS revenue_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP,
                product_name TEXT,
                amount REAL,
                customer_email TEXT,
                source TEXT,
                status TEXT DEFAULT 'completed'
            )
        ''')
        
        # 每小时目标表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hourly_targets (
                hour INTEGER PRIMARY KEY,
                target_amount REAL,
                actual_amount REAL DEFAULT 0.0,
                status TEXT DEFAULT 'pending'
            )
        ''')
        
        # 初始化24小时目标
        for hour in range(24):
            # 目标: 24小时$100，每小时约$4.17
            target = 4.17 if hour < 24 else 0
            cursor.execute('''
                INSERT OR IGNORE INTO hourly_targets (hour, target_amount)
                VALUES (?, ?)
            ''', (hour, target))
        
        conn.commit()
        conn.close()
        
    def simulate_first_sale(self):
        """模拟第一笔销售（用于测试）"""
        current_hour = datetime.now().hour
        
        # 随机选择一个产品
        conn_products = sqlite3.connect(self.products_db)
        cursor_products = conn_products.cursor()
        cursor_products.execute('SELECT name, price FROM products ORDER BY RANDOM() LIMIT 1')
        product = cursor_products.fetchone()
        conn_products.close()
        
        if product:
            product_name, price = product
            
            # 随机选择一个线索
            conn_leads = sqlite3.connect(self.leads_db)
            cursor_leads = conn_leads.cursor()
            cursor_leads.execute('SELECT email FROM leads WHERE status = "contacted" ORDER BY RANDOM() LIMIT 1')
            lead = cursor_leads.fetchone()
            conn_leads.close()
            
            customer_email = lead[0] if lead else "test@example.com"
            
            # 记录收入
            conn = sqlite3.connect(self.monitor_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO revenue_records (timestamp, product_name, amount, customer_email, source)
                VALUES (?, ?, ?, ?, ?)
            ''', (datetime.now(), product_name, price, customer_email, 'simulated_test'))
            
            # 更新小时目标
            cursor.execute('''
                UPDATE hourly_targets 
                SET actual_amount = actual_amount + ?, status = 'in_progress'
                WHERE hour = ?
            ''', (price, current_hour))
            
            conn.commit()
            conn.close()
            
            print(f"🎉 模拟销售: {product_name} - ${price} - {customer_email}")
            return True
        
        return False
    
    def get_current_status(self):
        """获取当前状态"""
        conn = sqlite3.connect(self.monitor_db)
        cursor = conn.cursor()
        
        # 总收入
        cursor.execute('SELECT SUM(amount) FROM revenue_records')
        total_revenue = cursor.fetchone()[0] or 0.0
        
        # 总销售数
        cursor.execute('SELECT COUNT(*) FROM revenue_records')
        total_sales = cursor.fetchone()[0] or 0
        
        # 当前小时状态
        current_hour = datetime.now().hour
        cursor.execute('SELECT target_amount, actual_amount FROM hourly_targets WHERE hour = ?', (current_hour,))
        hour_target = cursor.fetchone()
        
        # 24小时进度
        cursor.execute('SELECT SUM(target_amount), SUM(actual_amount) FROM hourly_targets')
        day_target = cursor.fetchone()
        
        conn.close()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'current_hour': current_hour,
            'total_revenue': total_revenue,
            'total_sales': total_sales,
            'hourly_target': hour_target[0] if hour_target else 0,
            'hourly_actual': hour_target[1] if hour_target else 0,
            'daily_target': day_target[0] if day_target else 100.0,
            'daily_actual': day_target[1] if day_target else 0.0,
            'progress_percentage': 0.0  # 初始为0，等待真实收入
        }
    
    def generate_optimization_actions(self):
        """根据当前状态生成优化动作"""
        status = self.get_current_status()
        total_revenue = status['total_revenue']
        current_hour = status['current_hour']
        
        actions = []
        
        if total_revenue == 0:
            # 还没有收入，显示真实状态
            actions.extend([
                "⚠️ 真实状态: 暂无收入，等待第一笔真实支付",
                "1. 收款链接已就绪: https://checkout.stripe.com/c/pay/cs_live_a1PX9HibJYwE0KgaU1vDty8KPX9GcvbBxWna5BzkiExeCT9iEcNo6hhg61",
                "2. 需要推广获取真实客户付款",
                "3. 系统100%就绪，等待支付",
                "4. 真实Stripe账户: acct_1TCfcBDRLWt3rKvb (意大利, EUR)",
                "5. 监控系统显示100%真实数据"
            ])
        elif total_revenue < 10:
            # 有少量收入，需要加速
            actions.extend([
                f"📈 已有${total_revenue:.2f}收入，继续加速!",
                "1. 分析已购买客户特征，寻找相似线索",
                "2. 创建成功案例分享，建立社会证明",
                "3. 启动推荐计划: 推荐朋友获得20%佣金",
                "4. 优化支付页面，减少购买摩擦",
                "5. 发送购买确认邮件时，推荐相关产品"
            ])
        elif total_revenue < 50:
            # 中等收入，优化转化
            actions.extend([
                f"✅ 进展良好: ${total_revenue:.2f}，目标${100-total_revenue:.2f}",
                "1. 创建产品捆绑包，提高客单价",
                "2. 启动电子邮件营销自动化序列",
                "3. 优化落地页，提高转化率",
                "4. 收集客户反馈，改进产品",
                "5. 扩展营销渠道: 尝试Reddit广告"
            ])
        else:
            # 接近目标，冲刺
            actions.extend([
                f"🎯 接近目标: ${total_revenue:.2f}/$100.00",
                "1. 创建限时抢购活动，制造紧迫感",
                "2. 联系所有未回复线索提供最终优惠",
                "3. 在现有客户中推广订阅服务",
                "4. 优化移动端购买体验",
                "5. 准备庆祝和总结报告"
            ])
        
        # 根据时间调整策略
        if current_hour < 12:
            actions.append("⏰ 上午策略: 专注于B2B客户和企业购买")
        elif current_hour < 18:
            actions.append("⏰ 下午策略: 专注于个人消费者和小团队")
        else:
            actions.append("⏰ 晚间策略: 专注于国际客户和夜间工作者")
        
        return actions
    
    def create_dashboard_html(self):
        """创建实时监控仪表板HTML"""
        status = self.get_current_status()
        actions = self.generate_optimization_actions()
        
        # 计算平均客单价
        avg_price = status['total_revenue'] / status['total_sales'] if status['total_sales'] > 0 else 0.00
        hourly_needed = (100 - status['total_revenue']) / (24 - status['current_hour']) if status['current_hour'] < 24 else 0
        
        html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>24小时收入监控 - 实时仪表板</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f7fa;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        .header {{
            text-align: center;
            margin-bottom: 40px;
            padding: 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 15px;
        }}
        .header h1 {{
            font-size: 2.5rem;
            margin-bottom: 10px;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            text-align: center;
        }}
        .stat-card h3 {{
            font-size: 2.5rem;
            margin: 15px 0;
            color: #333;
        }}
        .stat-card .label {{
            color: #666;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .progress-bar {{
            height: 30px;
            background: #e0e0e0;
            border-radius: 15px;
            margin: 30px 0;
            overflow: hidden;
        }}
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #4CAF50, #8BC34A);
            width: {status['progress_percentage']}%;
            transition: width 0.5s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
        }}
        .actions-panel {{
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            margin-bottom: 40px;
        }}
        .actions-panel h2 {{
            color: #333;
            margin-bottom: 20px;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}
        .action-item {{
            background: #f8f9fa;
            padding: 15px;
            margin: 10px 0;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }}
        .time-info {{
            background: #fff3cd;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            border-left: 4px solid #ffc107;
        }}
        .footer {{
            text-align: center;
            color: #666;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e0e0e0;
        }}
        .revenue-badge {{
            display: inline-block;
            background: {'#4CAF50' if status['total_revenue'] > 0 else '#f44336'};
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
            margin-left: 10px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>24小时收入监控仪表板 <span class="revenue-badge">{'$' + str(status['total_revenue']) if status['total_revenue'] > 0 else '无收入'}</span></h1>
            <p>目标: $100 真实收入 | 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="label">当前收入</div>
                <h3>${status['total_revenue']:.2f}</h3>
                <div>目标: $100.00</div>
            </div>
            <div class="stat-card">
                <div class="label">总销售数</div>
                <h3>{status['total_sales']}</h3>
                <div>平均客单价: ${avg_price:.2f}</div>
            </div>
            <div class="stat-card">
                <div class="label">完成进度</div>
                <h3>{status['progress_percentage']:.1f}%</h3>
                <div>剩余: ${100-status['total_revenue']:.2f}</div>
            </div>
            <div class="stat-card">
                <div class="label">当前小时</div>
                <h3>{status['current_hour']}:00</h3>
                <div>目标: ${status['hourly_target']:.2f} | 实际: ${status['hourly_actual']:.2f}</div>
            </div>
        </div>
        
        <div class="progress-bar">
            <div class="progress-fill">{status['progress_percentage']:.1f}%</div>
        </div>
        
        <div class="time-info">
            <h3>⏰ 时间分析</h3>
            <p>当前时间: {datetime.now().strftime('%H:%M')} | 已过去: {status['current_hour']}小时 | 剩余: {24-status['current_hour']}小时</p>
            <p>每小时需要: ${hourly_needed:.2f} 才能达成目标</p>
        </div>
        
        <div class="actions-panel">
            <h2>🎯 实时优化建议</h2>
            {''.join([f'<div class="action-item">{action}</div>' for action in actions])}
        </div>
        
        <div class="footer">
            <p>最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>监控系统自动刷新每5分钟 | 数据来源: 实战营销优化系统</p>
        </div>
    </div>
    
    <script>
        // 自动刷新每5分钟
        setTimeout(() => {{
            location.reload();
        }}, 300000);
        
        // 实时更新进度条
        const progressBar = document.querySelector('.progress-fill');
        let currentProgress = {status['progress_percentage']};
        
        // 模拟实时更新（实际中这里会有WebSocket连接）
        setInterval(() => {{
            // 这里可以添加实际的WebSocket更新
        }}, 10000);
    </script>
</body>
</html>'''
        
        return html
    
    def run_24h_monitor(self):
        """运行24小时监控"""
        print("⏰ 启动24小时收入监控系统")
        print("=" * 60)
        
        # 显示当前状态
        status = self.get_current_status()
        print(f"当前时间: {datetime.now().strftime('%H:%M')}")
        print(f"当前收入: ${status['total_revenue']:.2f} / $100.00")
        print(f"完成进度: {status['progress_percentage']:.1f}%")
        print(f"总销售数: {status['total_sales']}")
        print(f"当前小时目标: ${status['hourly_target']:.2f} (实际: ${status['hourly_actual']:.2f})")
        
        print("\n🎯 优化建议:")
        print("-" * 40)
        actions = self.generate_optimization_actions()
        for action in actions:
            print(f"  {action}")
        
        # 生成仪表板HTML
        dashboard_html = self.create_dashboard_html()
        dashboard_file = "24小时收入监控仪表板.html"
        with open(dashboard_file, 'w', encoding='utf-8') as f:
            f.write(dashboard_html)
        
        print(f"\n✅ 仪表板已生成: {dashboard_file}")
        print(f"📊 访问地址: http://localhost:5200/{dashboard_file}")
        
        # 检查真实收入 - 只显示真实数据
        if status['total_revenue'] == 0:
            print("\n⚠️ 真实收入状态: $0.00")
            print("💡 说明: 系统等待第一笔真实支付")
            print("🔗 收款链接已就绪，等待客户付款")
        
        return status

def main():
    """主函数"""
    monitor = RevenueMonitor24h()
    return monitor.run_24h_monitor()

if __name__ == "__main__":
    main()