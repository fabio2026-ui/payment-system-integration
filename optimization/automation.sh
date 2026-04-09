#!/bin/bash
# payment-system-integration 自动化运维脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO] ${NC}$1"
}

log_warn() {
    echo -e "${YELLOW}[WARN] ${NC}$1"
}

log_error() {
    echo -e "${RED}[ERROR] ${NC}$1"
}

# 检查命令是否存在
check_command() {
    if ! command -v $1 &> /dev/null; then
        log_error "命令 $1 不存在，请先安装"
        exit 1
    fi
}

# 健康检查
health_check() {
    log_info "执行健康检查..."
    
    # 检查服务是否运行
    if curl -s http://localhost:8000/health | grep -q "healthy"; then
        log_info "服务健康状态: 正常"
        return 0
    else
        log_error "服务健康状态: 异常"
        return 1
    fi
}

# 性能检查
performance_check() {
    log_info "执行性能检查..."
    
    # 检查响应时间
    response_time=$(curl -o /dev/null -s -w '%{time_total}\n' http://localhost:8000/health)
    if (( $(echo "$response_time < 1" | bc -l) )); then
        log_info "响应时间: $response_time 秒 (正常)"
    else
        log_warn "响应时间: $response_time 秒 (较慢)"
    fi
    
    # 检查内存使用
    memory_usage=$(ps aux | grep "payment-system-integration" | grep -v grep | awk '{print $4}')
    if (( $(echo "$memory_usage < 80" | bc -l) )); then
        log_info "内存使用: $memory_usage% (正常)"
    else
        log_warn "内存使用: $memory_usage% (较高)"
    fi
    
    # 检查磁盘空间
    disk_usage=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ $disk_usage -lt 80 ]; then
        log_info "磁盘使用: $disk_usage% (正常)"
    else
        log_warn "磁盘使用: $disk_usage% (较高)"
    fi
}

# 备份数据库
backup_database() {
    log_info "备份数据库..."
    
    timestamp=$(date +%Y%m%d_%H%M%S)
    backup_file="backup_payment-system-integration_${timestamp}.sql"
    
    if [ -f "database.db" ]; then
        sqlite3 database.db ".backup $backup_file"
        log_info "数据库备份完成: $backup_file"
        
        # 压缩备份文件
        gzip $backup_file
        log_info "备份文件已压缩: $backup_file.gz"
    else
        log_warn "数据库文件不存在，跳过备份"
    fi
}

# 清理旧日志
cleanup_logs() {
    log_info "清理旧日志..."
    
    # 保留最近7天的日志
    find logs/ -name "*.log" -mtime +7 -delete
    log_info "已清理7天前的日志文件"
    
    # 清理临时文件
    find /tmp -name "*payment-system-integration*" -mtime +1 -delete
    log_info "已清理临时文件"
}

# 更新依赖
update_dependencies() {
    log_info "更新依赖..."
    
    if [ -f "requirements.txt" ]; then
        pip install --upgrade -r requirements.txt
        log_info "依赖更新完成"
    else
        log_warn "requirements.txt 不存在，跳过依赖更新"
    fi
}

# 重启服务
restart_service() {
    log_info "重启服务..."
    
    # 停止服务
    pkill -f "payment-system-integration" || true
    
    # 启动服务
    nohup python3 main.py > logs/payment-system-integration_$(date +%Y%m%d_%H%M%S).log 2>&1 &
    
    # 等待服务启动
    sleep 5
    
    # 检查服务状态
    if health_check; then
        log_info "服务重启成功"
    else
        log_error "服务重启失败"
        exit 1
    fi
}

# 部署新版本
deploy_new_version() {
    log_info "部署新版本..."
    
    # 备份当前版本
    backup_database
    
    # 拉取最新代码
    git pull origin main
    
    # 更新依赖
    update_dependencies
    
    # 重启服务
    restart_service
    
    log_info "新版本部署完成"
}

# 监控报告
generate_monitoring_report() {
    log_info "生成监控报告..."
    
    report_file="monitoring_report_$(date +%Y%m%d_%H%M%S).md"
    
    cat > $report_file << EOF
# payment-system-integration 监控报告
生成时间: $(date)

## 系统状态
$(health_check 2>&1)

## 性能指标
$(performance_check 2>&1)

## 磁盘使用
$(df -h)

## 内存使用
$(free -h)

## 进程状态
$(ps aux | grep "payment-system-integration" | grep -v grep)

## 网络连接
$(netstat -tulpn | grep ":8000")

## 错误日志 (最近10行)
$(tail -10 logs/*.log 2>/dev/null || echo "无错误日志")

## 建议
1. 定期备份数据库
2. 监控磁盘使用情况
3. 检查错误日志
4. 更新依赖包
EOF
    
    log_info "监控报告已生成: $report_file"
}

# 主函数
main() {
    case "$1" in
        health)
            health_check
            ;;
        performance)
            performance_check
            ;;
        backup)
            backup_database
            ;;
        cleanup)
            cleanup_logs
            ;;
        update)
            update_dependencies
            ;;
        restart)
            restart_service
            ;;
        deploy)
            deploy_new_version
            ;;
        report)
            generate_monitoring_report
            ;;
        all)
            log_info "执行所有运维任务..."
            health_check
            performance_check
            backup_database
            cleanup_logs
            update_dependencies
            generate_monitoring_report
            log_info "所有运维任务完成"
            ;;
        *)
            echo "用法: $0 {health|performance|backup|cleanup|update|restart|deploy|report|all}"
            exit 1
            ;;
    esac
}

# 检查必要命令
check_command curl
check_command sqlite3
check_command gzip
check_command git

# 创建日志目录
mkdir -p logs

# 执行主函数
main "$@"
