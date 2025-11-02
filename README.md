# 🎭 角色扮演聊天机器人 - 使用指南

一个基于 GPT-4 的智能角色扮演聊天系统，支持与 5 个经典影视文学角色进行真实对话。集成了 MCP（Model Context Protocol）智能搜索增强功能，能够自动从网络获取真实背景资料，让对话更加准确生动。

---

## ✨ 主要特性

### 🎯 核心功能
- **多角色系统**：5 个性格鲜明的经典角色可选
- **智能对话**：基于 GPT-4o 模型，保持角色人设一致性
- **MCP 搜索增强**：AI 自动判断并搜索网络资料，提供准确的历史细节
- **美观界面**：现代化暗色主题，流畅动画效果
- **费用透明**：实时显示 Token 消耗和预估费用
- **历史管理**：支持保存和导出对话历史

### 👥 可选角色

| 角色 | 来源 | 特点 |
|------|------|------|
| 🔍 **夏洛克·福尔摩斯** | 《福尔摩斯探案集》 | 理性推理、高智商侦探 |
| 🦾 **托尼·斯塔克** | 漫威电影宇宙 | 科技天才、幽默风趣 |
| 🐒 **孙悟空** | 《西游记》 | 豪迈直率、神通广大 |
| 🎐 **诸葛亮** | 《三国演义》 | 智慧超群、儒雅谦逊 |
| ⚡ **哈利·波特** | 《哈利·波特》系列 | 勇敢善良、充满正义感 |

---

## 📋 系统要求

- **Python**: 3.8 或更高版本
- **操作系统**: Windows / Linux / macOS
- **网络**: 稳定的互联网连接（访问 OpenAI API 和搜索引擎）
- **OpenAI API Key**: 需要有效的 API 密钥

---

## 🚀 快速开始

### 第一步：安装 Python 依赖

```bash
pip install -r requirements.txt
```

**依赖包说明：**
- `streamlit` - Web 应用框架
- `openai` - OpenAI API 客户端
- `tiktoken` - Token 计数工具
- `Pillow` - 图像处理
- `requests` - HTTP 请求
- `beautifulsoup4` - HTML 解析
- `ddgs` - DuckDuckGo 搜索引擎（MCP 功能需要）

### 第二步：配置 API 密钥

#### Windows (命令提示符)
```cmd
set OPENAI_API_KEY=你的API密钥
set OPENAI_BASE_URL=https://api.openai.com/v1
```

#### Windows (PowerShell)
```powershell
$env:OPENAI_API_KEY="你的API密钥"
$env:OPENAI_BASE_URL="https://api.openai.com/v1"
```

#### Linux / macOS
```bash
export OPENAI_API_KEY=你的API密钥
export OPENAI_BASE_URL=https://api.openai.com/v1
```

**💡 提示**：建议将环境变量添加到系统配置文件中（如 `.bashrc`、`.zshrc` 或 Windows 环境变量设置），避免每次启动都要重新设置。

### 第三步：启动应用

#### 方法 1：使用启动脚本（推荐）

**Windows:**
```cmd
run.bat
```

**Linux/Mac:**
```bash
chmod +x run.sh
./run.sh
```

#### 方法 2：直接运行
```bash
streamlit run app.py
```

启动后，浏览器会自动打开应用，默认地址：`http://localhost:8501`

---

## 📖 使用指南

### 基本使用流程

#### 1. 选择角色
- 在左侧边栏点击任意角色按钮
- 当前选中的角色会以高亮显示
- 切换角色会自动清空当前对话历史

#### 2. 开始对话
- 在底部输入框输入您的消息
- 按 Enter 键或点击发送按钮
- AI 会以选定角色的身份回复

#### 3. 查看角色信息
- 点击主界面的"📖 查看角色详情"展开
- 查看角色的背景、性格特点和语言风格

#### 4. 使用 MCP 搜索增强（⭐ 新功能）

MCP 会自动判断何时需要搜索网络资料：

**触发搜索的问题类型：**
- 具体的历史事件细节（如"草船借箭借了多少箭？"）
- 原著中的具体场景和对话
- 需要准确数字或日期的问题
- 技术细节或专业知识

**不触发搜索的问题：**
- 日常闲聊（如"你好"、"心情如何"）
- 个人观点和假设性问题
- 情感表达类问题

**MCP 状态指示：**
- ✅ 绿色横幅：MCP 已启用
- 🔍 蓝色信息框：搜索已应用
- 📋 搜索历史：查看所有搜索记录
- 🔍 搜索次数：侧边栏统计

#### 5. 监控使用情况
左侧边栏实时显示：
- **总 Token 消耗**：累计使用的 Token 数量
- **预估费用**：根据 GPT-4o-ca 定价计算
- **MCP 搜索次数**：本次会话的搜索触发次数

#### 6. 管理对话历史
- **清空对话**：点击"🗑️ 清空对话"重置当前会话
- **保存历史**：点击"💾 保存对话历史"导出为 JSON 文件
  - 文件保存在 `chat_history/` 目录
  - 文件名格式：`角色名_时间戳.json`

---

## 🔍 MCP 搜索增强详解

### 什么是 MCP？

MCP (Model Context Protocol) 是一个智能搜索增强系统，它能：
1. **自动判断**：AI 分析问题，决定是否需要搜索
2. **网络搜索**：使用 DuckDuckGo 搜索相关资料
3. **智能总结**：GPT 提取关键信息
4. **增强回答**：将搜索结果融入角色回复中

### 如何使用 MCP

1. **启用/禁用**
   - 左侧边栏勾选"启用智能搜索增强"
   - 默认自动启用

2. **查看搜索结果**
   - 回复下方会显示"🔍 MCP搜索增强已应用"
   - 点击"📚 查看搜索来源和摘要"查看详细信息
   - 包含搜索关键词和参考来源链接

3. **查看搜索历史**
   - 左侧边栏"📋 搜索历史"显示最近 5 次搜索
   - 每条记录包含：问题、关键词、摘要、来源链接

### MCP 安装

如果 MCP 功能不可用，运行安装脚本：

**Windows:**
```cmd
install_mcp.bat
```

**Linux/Mac:**
```bash
chmod +x install_mcp.sh
./install_mcp.sh
```

或手动安装：
```bash
pip install ddgs beautifulsoup4 requests
```


## 📁 项目文件说明

```
final_lab/
├── app.py                 # 主应用程序（UI 和业务逻辑）
├── characters.py          # 角色配置文件
├── utils.py              # 工具函数（Token 计算、历史保存等）
├── mcp_search.py         # MCP 搜索增强模块
├── requirements.txt      # Python 依赖包列表
├── run.bat / run.sh      # 启动脚本
├── install_mcp.bat/sh    # MCP 安装脚本
├── clear_cache.bat/sh    # 缓存清理脚本
├── style.css             # CSS 样式（内嵌在 app.py 中）
├── assets/               # 角色头像图片
│   ├── sherlock.png
│   ├── tony.png
│   ├── wukong.png
│   ├── zhuge.png
│   └── harry.png
└── chat_history/         # 对话历史存储（自动生成）
```

