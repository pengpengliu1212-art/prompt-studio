#!/bin/bash

# 3C数码资讯系统启动脚本

echo "=========================================="
echo "   3C数码行业实时资讯系统启动脚本"
echo "=========================================="
echo ""

# 检查Python3是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误：未找到Python3，请先安装Python3"
    exit 1
fi

# 检查必要的Python包
echo "🔍 检查Python依赖..."
REQUIRED_PACKAGES=("flask" "flask_cors" "requests" "beautifulsoup4")

for package in "${REQUIRED_PACKAGES[@]}"; do
    if ! python3 -c "import ${package%%==*}" &> /dev/null; then
        echo "📦 安装缺失的包: $package"
        pip3 install "$package" || {
            echo "❌ 安装 $package 失败"
            exit 1
        }
    else
        echo "✅ $package 已安装"
    fi
done

echo ""
echo "✅ 所有依赖检查完成"
echo ""

# 显示系统信息
echo "📊 系统信息："
echo "   Python版本: $(python3 --version)"
echo "   工作目录: $(pwd)"
echo "   当前时间: $(date)"
echo ""

# 选择启动模式
echo "🚀 请选择启动模式："
echo "   1) 仅启动API服务器"
echo "   2) 仅获取资讯数据"
echo "   3) 完整启动（API服务器 + 获取数据）"
echo "   4) 查看帮助文档"
echo ""

read -p "请输入选项 (1-4): " choice

case $choice in
    1)
        echo ""
        echo "🌐 启动API服务器..."
        echo "   访问 http://localhost:5000/ 查看API文档"
        echo "   访问 http://localhost:5000/3c-news 查看资讯页面"
        echo "   按 Ctrl+C 停止服务器"
        echo ""
        python3 api_server.py
        ;;
    2)
        echo ""
        echo "📰 获取资讯数据..."
        python3 fetch_3c_news.py
        ;;
    3)
        echo ""
        echo "🔄 获取最新资讯数据..."
        python3 fetch_3c_news.py
        
        echo ""
        echo "🌐 启动API服务器..."
        echo "   访问 http://localhost:5000/ 查看API文档"
        echo "   访问 http://localhost:5000/3c-news 查看资讯页面"
        echo "   按 Ctrl+C 停止服务器"
        echo ""
        python3 api_server.py
        ;;
    4)
        echo ""
        echo "📖 帮助文档："
        cat README.md | head -50
        echo ""
        echo "... (完整文档请查看 README.md 文件)"
        ;;
    *)
        echo "❌ 无效选项"
        exit 1
        ;;
esac

echo ""
echo "=========================================="
echo "   感谢使用3C数码资讯系统！"
echo "=========================================="