#!/usr/bin/env python3
"""
统一支付中枢系统 - 多项目支付处理引擎
为全自动盈利项目工厂提供统一的支付处理能力
"""

import os
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import hashlib
import secrets

# 尝试导入stripe，如果失败则使用模拟模式
try:
    import stripe
    STRIPE_AVAILABLE = True
except ImportError:
    STRIPE_AVAILABLE = False
    print("⚠️ Stripe库不可用，使用模拟模式")

class UnifiedPaymentHub:
    """统一支付中枢 - 支持多项目的支付处理系统"""
    
    def __init__(self):
        """初始化支付中枢"""
        self.stripe_mode = os.getenv('STRIPE_MODE', 'live')
        self.stripe_secret_key = os.getenv('STRIPE_SECRET_KEY', '')
        self.stripe_publishable_key = os.getenv('STRIPE_PUBLISHABLE_KEY', '')
        
        # 初始化Stripe（如果可用）
        if STRIPE_AVAILABLE and self.stripe_secret_key:
            stripe.api_key = self.stripe_secret_key
            self.stripe_enabled = True
        else:
            self.stripe_enabled = False
            print("⚠️ Stripe支付暂时不可用，使用模拟模式")
        
        # 初始化数据库
        self.db_path = '/home/node/.openclaw/workspace/payment_hub.db'
        self.init_database()
        
        # 项目注册表
        self.projects = {}
        self.load_projects()
        
        print(f"✅ 统一支付中枢初始化完成 - 模式: {self.stripe_mode}")
        print(f"📊 已注册项目: {len(self.projects)} 个")
    
    def init_database(self):
        """初始化支付中枢数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 项目表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'active',
            config_json TEXT
        )
        ''')
        
        # 支付表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            stripe_payment_id TEXT,
            amount INTEGER NOT NULL,
            currency TEXT DEFAULT 'usd',
            status TEXT NOT NULL,
            customer_email TEXT,
            customer_name TEXT,
            metadata_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects (id)
        )
        ''')
        
        # 收入汇总表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS revenue_summary (
            date DATE PRIMARY KEY,
            total_amount INTEGER DEFAULT 0,
            project_count INTEGER DEFAULT 0,
            payment_count INTEGER DEFAULT 0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 项目收入表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS project_revenue (
            project_id TEXT,
            date DATE,
            amount INTEGER DEFAULT 0,
            payment_count INTEGER DEFAULT 0,
            PRIMARY KEY (project_id, date),
            FOREIGN KEY (project_id) REFERENCES projects (id)
        )
        ''')
        
        conn.commit()
        conn.close()
        
        print("✅ 支付中枢数据库初始化完成")
    
    def load_projects(self):
        """加载已注册项目"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, name, description, config_json FROM projects WHERE status = "active"')
        rows = cursor.fetchall()
        
        for row in rows:
            project_id, name, description, config_json = row
            config = json.loads(config_json) if config_json else {}
            self.projects[project_id] = {
                'name': name,
                'description': description,
                'config': config
            }
        
        conn.close()
    
    def register_project(self, project_id: str, name: str, description: str = "", config: Dict = None) -> bool:
        """注册新项目到支付中枢"""
        if project_id in self.projects:
            print(f"⚠️  项目 {project_id} 已存在")
            return False
        
        config = config or {}
        config_json = json.dumps(config)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO projects (id, name, description, config_json)
        VALUES (?, ?, ?, ?)
        ''', (project_id, name, description, config_json))
        
        conn.commit()
        conn.close()
        
        # 更新内存中的项目列表
        self.projects[project_id] = {
            'name': name,
            'description': description,
            'config': config
        }
        
        print(f"✅ 项目注册成功: {name} ({project_id})")
        return True
    
    def create_payment_intent(self, project_id: str, amount: int, currency: str = 'usd', 
                             metadata: Dict = None) -> Dict:
        """创建支付意图"""
        if project_id not in self.projects:
            return {'error': f'项目 {project_id} 未注册'}
        
        try:
            # 创建Stripe支付意图
            intent = stripe.PaymentIntent.create(
                amount=amount,
                currency=currency,
                metadata={
                    'project_id': project_id,
                    'project_name': self.projects[project_id]['name'],
                    **(metadata or {})
                }
            )
            
            # 记录支付意图
            payment_id = f"pay_{secrets.token_hex(8)}"
            self.record_payment(payment_id, project_id, intent.id, amount, currency, 'created', metadata)
            
            return {
                'success': True,
                'payment_id': payment_id,
                'client_secret': intent.client_secret,
                'publishable_key': self.stripe_publishable_key,
                'amount': amount,
                'currency': currency,
                'project': self.projects[project_id]['name']
            }
            
        except stripe.error.StripeError as e:
            return {'error': f'Stripe错误: {str(e)}'}
        except Exception as e:
            return {'error': f'系统错误: {str(e)}'}
    
    def record_payment(self, payment_id: str, project_id: str, stripe_payment_id: str,
                      amount: int, currency: str, status: str, metadata: Dict = None):
        """记录支付到数据库"""
        metadata_json = json.dumps(metadata or {})
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO payments (id, project_id, stripe_payment_id, amount, currency, status, metadata_json)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (payment_id, project_id, stripe_payment_id, amount, currency, status, metadata_json))
        
        # 更新收入汇总
        today = datetime.now().date().isoformat()
        cursor.execute('''
        INSERT OR REPLACE INTO revenue_summary (date, total_amount, payment_count)
        VALUES (?, COALESCE((SELECT total_amount FROM revenue_summary WHERE date = ?), 0) + ?,
                COALESCE((SELECT payment_count FROM revenue_summary WHERE date = ?), 0) + 1)
        ''', (today, today, amount, today))
        
        # 更新项目收入
        cursor.execute('''
        INSERT OR REPLACE INTO project_revenue (project_id, date, amount, payment_count)
        VALUES (?, ?, COALESCE((SELECT amount FROM project_revenue WHERE project_id = ? AND date = ?), 0) + ?,
                COALESCE((SELECT payment_count FROM project_revenue WHERE project_id = ? AND date = ?), 0) + 1)
        ''', (project_id, today, project_id, today, amount, project_id, today, 1))
        
        conn.commit()
        conn.close()
        
        print(f"💰 支付记录: {project_id} - ${amount/100:.2f} - 状态: {status}")
    
    def update_payment_status(self, stripe_payment_id: str, new_status: str):
        """更新支付状态"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        UPDATE payments SET status = ? WHERE stripe_payment_id = ?
        ''', (new_status, stripe_payment_id))
        
        conn.commit()
        
        # 获取支付信息用于日志
        cursor.execute('SELECT project_id, amount FROM payments WHERE stripe_payment_id = ?', (stripe_payment_id,))
        row = cursor.fetchone()
        
        if row:
            project_id, amount = row
            print(f"🔄 支付状态更新: {project_id} - ${amount/100:.2f} -> {new_status}")
        
        conn.close()
    
    def get_project_revenue(self, project_id: str, days: int = 30) -> Dict:
        """获取项目收入统计"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 今日收入
        today = datetime.now().date().isoformat()
        cursor.execute('''
        SELECT COALESCE(SUM(amount), 0), COALESCE(COUNT(*), 0)
        FROM payments 
        WHERE project_id = ? AND status = 'succeeded' AND date(created_at) = ?
        ''', (project_id, today))
        
        today_revenue, today_count = cursor.fetchone()
        
        # 本周收入
        week_ago = (datetime.now() - timedelta(days=7)).date().isoformat()
        cursor.execute('''
        SELECT COALESCE(SUM(amount), 0), COALESCE(COUNT(*), 0)
        FROM payments 
        WHERE project_id = ? AND status = 'succeeded' AND date(created_at) >= ?
        ''', (project_id, week_ago))
        
        week_revenue, week_count = cursor.fetchone()
        
        # 总收入
        cursor.execute('''
        SELECT COALESCE(SUM(amount), 0), COALESCE(COUNT(*), 0)
        FROM payments 
        WHERE project_id = ? AND status = 'succeeded'
        ''', (project_id,))
        
        total_revenue, total_count = cursor.fetchone()
        
        conn.close()
        
        return {
            'project_id': project_id,
            'project_name': self.projects.get(project_id, {}).get('name', '未知'),
            'today': {
                'revenue': today_revenue / 100,
                'count': today_count
            },
            'this_week': {
                'revenue': week_revenue / 100,
                'count': week_count
            },
            'all_time': {
                'revenue': total_revenue / 100,
                'count': total_count
            }
        }
    
    def get_overall_revenue(self, days: int = 30) -> Dict:
        """获取总体收入统计"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 今日总体收入
        today = datetime.now().date().isoformat()
        cursor.execute('''
        SELECT COALESCE(SUM(amount), 0), COALESCE(COUNT(*), 0), COUNT(DISTINCT project_id)
        FROM payments 
        WHERE status = 'succeeded' AND date(created_at) = ?
        ''', (today,))
        
        today_revenue, today_count, today_projects = cursor.fetchone()
        
        # 项目收入排名
        cursor.execute('''
        SELECT p.project_id, pr.name, COALESCE(SUM(p.amount), 0) as total_revenue
        FROM payments p
        JOIN projects pr ON p.project_id = pr.id
        WHERE p.status = 'succeeded' AND date(p.created_at) >= date('now', '-30 days')
        GROUP BY p.project_id
        ORDER BY total_revenue DESC
        LIMIT 10
        ''')
        
        top_projects = []
        for row in cursor.fetchall():
            project_id, project_name, revenue = row
            top_projects.append({
                'project_id': project_id,
                'name': project_name,
                'revenue': revenue / 100
            })
        
        conn.close()
        
        return {
            'today': {
                'revenue': today_revenue / 100,
                'payments': today_count,
                'active_projects': today_projects
            },
            'top_projects': top_projects,
            'total_projects': len(self.projects),
            'system_status': 'active'
        }
    
    def generate_revenue_report(self) -> str:
        """生成收入报告"""
        overall = self.get_overall_revenue()
        
        report = f"""# 📊 统一支付中枢收入报告

## 报告时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

## 🎯 今日收入概览
- **总收入**: ${overall['today']['revenue']:.2f}
- **支付次数**: {overall['today']['payments']}
- **活跃项目**: {overall['today']['active_projects']}

## 🏆 收入排名前10项目
"""
        
        for i, project in enumerate(overall['top_projects'], 1):
            report += f"{i}. **{project['name']}** - ${project['revenue']:.2f}\n"
        
        report += f"""
## 📈 系统状态
- **总注册项目**: {overall['total_projects']}
- **支付系统**: {self.stripe_mode.upper()} 模式
- **系统状态**: {overall['system_status'].upper()}

## 💰 项目详细收入
"""
        
        for project_id in self.projects:
            project_revenue = self.get_project_revenue(project_id)
            report += f"""
### {project_revenue['project_name']}
- **今日收入**: ${project_revenue['today']['revenue']:.2f} ({project_revenue['today']['count']} 笔)
- **本周收入**: ${project_revenue['this_week']['revenue']:.2f} ({project_revenue['this_week']['count']} 笔)
- **总收入**: ${project_revenue['all_time']['revenue']:.2f} ({project_revenue['all_time']['count']} 笔)
"""
        
        return report

def main():
    """主函数 - 启动统一支付中枢"""
    print("🚀 启动统一支付中枢系统...")
    print("=" * 50)
    
    # 初始化支付中枢
    payment_hub = UnifiedPaymentHub()
    
    # 注册示例项目（实际中从项目工厂自动注册）
    payment_hub.register_project(
        project_id="ai_outsourcing",
        name="AI外包公司",
        description="全自动AI外包服务平台"
    )
    
    payment_hub.register_project(
        project_id="content_factory",
        name="内容工厂",
        description="AI驱动的内容生成和分发平台"
    )
    
    payment_hub.register_project(
        project_id="saas_builder",
        name="SaaS构建器",
        description="一键生成和部署SaaS产品"
    )
    
    # 生成初始报告
    report = payment_hub.generate_revenue_report()
    
    # 保存报告
    report_path = "/home/node/.openclaw/workspace/payment_hub_report.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n✅ 统一支付中枢启动完成")
    print(f"📊 报告已保存: {report_path}")
    print(f"🎯 已注册项目: {len(payment_hub.projects)} 个")
    print(f"💰 支付模式: {payment_hub.stripe_mode.upper()}")
    print("\n🔧 系统就绪，等待项目工厂调用...")

if __name__ == "__main__":
    main()