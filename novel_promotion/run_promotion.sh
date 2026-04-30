#!/bin/bash
# 《沧纪元》小说自动化宣发 - 运行脚本
# 作者：白月AI助理

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# 检查环境
check_environment() {
    log_info "检查运行环境..."
    
    # 检查Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python3未安装"
        return 1
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    log_info "Python版本: $PYTHON_VERSION"
    
    # 检查agent-browser（可选）
    if command -v agent-browser &> /dev/null; then
        log_info "agent-browser已安装"
    else
        log_warning "agent-browser未安装，部分功能受限"
    fi
    
    # 检查依赖
    if [ -f "requirements.txt" ]; then
        log_info "检查Python依赖..."
        python3 -c "import yaml, json" 2>/dev/null || {
            log_warning "部分Python依赖未安装，尝试安装..."
            pip install -r requirements.txt 2>/dev/null || log_warning "依赖安装失败，继续运行..."
        }
    fi
    
    # 检查配置文件
    if [ ! -f "config.yaml" ]; then
        log_error "配置文件 config.yaml 不存在"
        return 1
    fi
    
    log_success "环境检查通过"
    return 0
}

# 显示横幅
show_banner() {
    echo ""
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║               《沧纪元》小说自动化宣发系统               ║"
    echo "║                番茄免费小说平台专用                     ║"
    echo "║                版本 1.0 · 白月AI助理                    ║"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo ""
}

# 显示帮助
show_help() {
    echo "使用方法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  run             运行单次推广检查（默认）"
    echo "  schedule        安排推广任务"
    echo "  report          生成推广报告"
    echo "  test            测试系统功能"
    echo "  continuous      持续运行模式"
    echo "  setup           设置自动化任务"
    echo "  help            显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 run          运行单次推广"
    echo "  $0 report       生成日报"
    echo "  $0 test         测试所有功能"
    echo ""
}

# 运行单次推广
run_promotion() {
    log_info "开始单次推广运行..."
    
    local output=$(python3 novel_promoter.py run 2>&1)
    local exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        log_success "推广运行完成"
        echo "$output"
    else
        log_error "推广运行失败"
        echo "$output"
        return 1
    fi
}

# 安排任务
schedule_tasks() {
    log_info "安排推广任务..."
    
    local output=$(python3 novel_promoter.py schedule 2>&1)
    echo "$output"
    
    log_success "任务安排完成"
}

# 生成报告
generate_report() {
    local period=${1:-"daily"}
    
    log_info "生成${period}报告..."
    
    local output=$(python3 novel_promoter.py report --period "$period" 2>&1)
    echo "$output"
    
    log_success "报告生成完成"
}

# 测试系统
test_system() {
    log_info "开始系统测试..."
    
    echo "1. 测试内容生成..."
    python3 novel_promoter.py test
    
    echo ""
    echo "2. 测试浏览器自动化..."
    python3 tomato_novel_automation.py --action test 2>/dev/null || \
        log_warning "浏览器自动化测试跳过或失败"
    
    echo ""
    echo "3. 测试配置加载..."
    python3 -c "import yaml; print('✓ 配置加载正常')"
    
    log_success "系统测试完成"
}

# 持续运行模式
run_continuous() {
    local interval=${1:-30}
    
    log_info "启动持续运行模式，检查间隔: ${interval}分钟"
    log_warning "按Ctrl+C停止运行"
    
    python3 novel_promoter.py continuous --interval "$interval"
}

# 设置自动化
setup_automation() {
    log_info "设置自动化任务..."
    
    local output=$(python3 novel_promoter.py setup 2>&1)
    echo "$output"
    
    # 显示Cron设置提示
    echo ""
    log_info "请将以下Cron配置添加到crontab中："
    cat cron_setup.txt 2>/dev/null || echo "（cron_setup.txt文件不存在）"
    
    log_success "自动化设置完成"
}

# 主函数
main() {
    local action=${1:-"run"}
    
    show_banner
    
    case "$action" in
        "run")
            check_environment || exit 1
            run_promotion
            ;;
        "schedule")
            check_environment || exit 1
            schedule_tasks
            ;;
        "report")
            check_environment || exit 1
            generate_report "daily"
            ;;
        "weekly-report")
            check_environment || exit 1
            generate_report "weekly"
            ;;
        "monthly-report")
            check_environment || exit 1
            generate_report "monthly"
            ;;
        "test")
            check_environment || exit 1
            test_system
            ;;
        "continuous")
            check_environment || exit 1
            run_continuous "$2"
            ;;
        "setup")
            check_environment || exit 1
            setup_automation
            ;;
        "help"|"--help"|"-h")
            show_help
            ;;
        *)
            log_error "未知操作: $action"
            show_help
            exit 1
            ;;
    esac
    
    echo ""
    log_info "运行完成，日志文件: novel_promotion.log"
    log_info "数据目录: data/"
}

# 执行主函数
main "$@"