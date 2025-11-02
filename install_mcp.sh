#!/bin/bash

echo "========================================"
echo "安装 MCP 搜索增强依赖"
echo "========================================"
echo

echo "正在安装搜索相关依赖..."
pip install duckduckgo-search>=3.9.0
pip install beautifulsoup4>=4.12.0
pip install requests>=2.31.0

echo
echo "========================================"
echo "安装完成！"
echo "========================================"
echo
echo "MCP 搜索增强功能已启用。"
echo "重新运行应用即可使用智能搜索功能。"
echo

