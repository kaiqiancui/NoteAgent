#!/bin/bash

echo "=================================="
echo "视频学习辅助智能体 - 启动脚本"
echo "=================================="
echo ""

# 检查 conda
if ! command -v conda &> /dev/null; then
    echo "❌ 错误: 未找到 conda"
    echo "请先安装 Anaconda 或 Miniconda"
    exit 1
fi

echo "✅ Conda 已安装"

# 检查 map 环境是否存在
if ! conda env list | grep -q "^map "; then
    echo "❌ 错误: 未找到 conda 环境 'map'"
    echo "请创建环境: conda create -n map python=3.10"
    exit 1
fi

echo "✅ 找到 conda 环境: map"
echo ""

# 激活 conda 环境
echo "🔧 激活 conda 环境 map..."
# 对于不同的 shell，激活方式可能不同
eval "$(conda shell.bash hook)"
conda activate map

if [ $? -ne 0 ]; then
    echo "❌ 激活环境失败"
    echo "请手动运行: conda activate map"
    exit 1
fi

echo "✅ 环境已激活: $(conda info --envs | grep '*')"
echo ""

# 进入后端目录
cd backend

echo "=================================="
echo "🚀 启动后端服务..."
echo "=================================="
echo ""
echo "API 配置："
echo "  - API Key: sk-1cateP6i..."
echo "  - API URL: https://api.qingyuntop.top"
echo "  - 模型: gpt-4o"
echo ""
echo "访问以下地址："
echo "  - API 文档: http://localhost:8000/docs"
echo "  - 健康检查: http://localhost:8000/"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""

# 启动服务
python main.py
