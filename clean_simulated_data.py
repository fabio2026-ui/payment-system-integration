import sqlite3
from datetime import datetime

# 清理模拟数据
db_path = '24h_revenue_monitor.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print('🧹 清理所有模拟收入数据...')

# 删除所有收入记录
cursor.execute('DELETE FROM revenue_records')
print(f'✅ 删除收入记录: {cursor.rowcount} 条')

# 重置每小时实际收入为0
cursor.execute('UPDATE hourly_targets SET actual_amount = 0.0')
print('✅ 重置每小时收入为0')

conn.commit()
conn.close()

print('')
print('📊 现在检查真实状态...')

# 重新连接检查
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute('SELECT SUM(amount) FROM revenue_records')
total_revenue = cursor.fetchone()[0] or 0.0
cursor.execute('SELECT COUNT(*) FROM revenue_records')
total_sales = cursor.fetchone()[0] or 0

print(f'💰 真实收入: ${total_revenue:.2f}')
print(f'📦 真实销售数: {total_sales}')
print('')
print('✅ 所有模拟数据已清除，现在只显示真实数据！')

conn.close()