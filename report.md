# 角色扮演聊天机器人 - 技术报告

## 项目概述

本项目是一个基于大语言模型的角色扮演聊天机器人系统，支持用户与5个经典影视文学角色进行真实对话。通过精心设计的角色系统提示词和对话管理机制，实现了高度一致的角色人设保持能力。

### 核心功能

- 🎭 **多角色对话系统**：支持5个不同风格的经典角色切换
- 💬 **智能对话生成**：基于GPT-4o-ca模型的上下文感知对话
- 💰 **实时费用统计**：Token消耗和费用的精确计算与展示
- 💾 **对话历史管理**：支持对话历史的保存和导出
- 🎨 **现代化UI设计**：流畅的用户界面和交互体验

---

## 技术架构

### 1. 技术栈

| 技术/框架 | 版本 | 用途 |
|----------|------|------|
| Python | 3.8+ | 编程语言 |
| Streamlit | 1.28.0+ | Web应用框架 |
| OpenAI API | 1.3.0+ | 大语言模型接口 |
| tiktoken | 0.5.1+ | Token计数工具 |
| Pillow | 10.0.0+ | 图像处理 |

### 2. 项目结构

```
final_lab/
├── app.py              # 主应用程序 - UI和业务逻辑
├── characters.py       # 角色配置文件 - 5个角色的详细设定
├── utils.py           # 工具函数库 - Token计算、历史保存等
├── requirements.txt   # Python依赖包列表
├── assets/            # 静态资源目录
│   ├── sherlock.png   # 福尔摩斯头像
│   ├── tony.png       # 托尼·斯塔克头像
│   ├── wukong.png     # 孙悟空头像
│   ├── zhuge.png      # 诸葛亮头像
│   └── harry.png      # 哈利·波特头像
├── .streamlit/        # Streamlit配置
│   └── config.toml    # 应用配置文件
├── chat_history/      # 对话历史存储目录（自动生成）
├── run.bat            # Windows启动脚本
├── run.sh             # Linux/Mac启动脚本
├── clear_cache.bat    # Windows缓存清理脚本
└── clear_cache.sh     # Linux/Mac缓存清理脚本
```

---

## 核心技术实现

### 1. 角色系统设计 (`characters.py`)

#### 1.1 数据结构

每个角色包含以下属性：

```python
{
    "name": "角色名称",           # 中文显示名称
    "emoji": "🔍",              # 表情符号标识
    "avatar": "在线头像URL",     # 备用头像（在线）
    "avatar_local": "本地路径",  # 本地头像图片路径
    "source": "作品来源",        # 角色出处
    "background": "背景设定",    # 详细背景介绍
    "personality": "性格特点",   # 性格描述
    "speaking_style": "语言风格" # 说话方式
}
```

#### 1.2 角色列表

本系统实现了5个经典角色：

1. **夏洛克·福尔摩斯** (Sherlock Holmes)
   - 特点：理性推理、高智商、擅长观察
   - 风格：简洁精准、逻辑严密

2. **托尼·斯塔克** (Tony Stark)
   - 特点：科技天才、幽默风趣、自信
   - 风格：轻松诙谐、技术导向

3. **孙悟空** (Sun Wukong)
   - 特点：豪迈直率、神通广大、重情义
   - 风格：自称"俺老孙"、豪爽洒脱

4. **诸葛亮** (Zhuge Liang)
   - 特点：智慧超群、谨慎稳重、儒雅
   - 风格：引经据典、文雅含蓄

5. **哈利·波特** (Harry Potter)
   - 特点：勇敢善良、忠诚正直
   - 风格：真诚直接、充满勇气

### 2. 系统提示词工程 (`app.py`)

#### 2.1 提示词构建策略

系统通过 `get_system_prompt()` 函数动态生成角色提示词：

```python
def get_system_prompt(character_name):
    character = CHARACTERS[character_name]
    return f"""你现在要扮演{character['name']}。

角色背景：
{character['background']}

性格特点：
{character['personality']}

语言风格：
{character['speaking_style']}

重要规则：
1. 始终保持角色的性格、年龄、职业等设定的一致性
2. 使用符合角色背景的语言风格进行回复
3. 当用户询问角色相关信息时，基于角色设定回答
4. 完全沉浸在角色中，不要跳出角色身份
5. 用第一人称"我"来称呼自己
6. 回答要详细充实，通常应该包含3-5个句子或更多
7. 可以讲述相关的故事、经历或见解，使对话更加生动有趣
8. 展现角色的专业知识和独特视角"""
```

#### 2.2 提示词设计要点

- **角色身份确立**：明确告知AI要扮演的角色
- **背景信息注入**：提供详细的角色背景和设定
- **行为规则约束**：8条规则确保角色一致性
- **输出质量控制**：要求详细充实的回复（3-5句或更多）
- **第一人称视角**：强调用"我"来保持沉浸感

### 3. 对话管理系统

#### 3.1 会话状态管理

使用Streamlit的 `session_state` 管理会话数据：

```python
def init_session_state():
    if 'messages' not in st.session_state:
        st.session_state.messages = []  # 对话历史
    if 'current_character' not in st.session_state:
        st.session_state.current_character = None  # 当前角色
    if 'total_tokens' not in st.session_state:
        st.session_state.total_tokens = 0  # 总Token消耗
    if 'total_cost' not in st.session_state:
        st.session_state.total_cost = 0.0  # 总费用
    if 'client' not in st.session_state:
        # 初始化OpenAI客户端
        api_key = os.getenv('OPENAI_API_KEY')
        base_url = os.getenv('OPENAI_BASE_URL')
        st.session_state.client = OpenAI(api_key=api_key, base_url=base_url)
```

**设计优势**：
- 持久化：会话状态在页面刷新后保持
- 隔离性：每个用户会话独立
- 高效性：避免重复初始化API客户端

#### 3.2 角色切换机制

```python
def switch_character(character_name):
    if st.session_state.current_character != character_name:
        st.session_state.current_character = character_name
        st.session_state.messages = []  # 清空对话历史
```

**设计考虑**：
- 角色切换时自动清空历史，避免上下文混淆
- 保留Token统计，方便用户了解总体消耗

#### 3.3 对话生成流程

```python
def chat_with_character(user_message):
    # 1. 构建完整消息列表
    messages = [
        {"role": "system", "content": get_system_prompt(...)},  # 系统提示词
        *st.session_state.messages,  # 历史对话
        {"role": "user", "content": user_message}  # 当前输入
    ]
    
    # 2. 调用OpenAI API
    response = st.session_state.client.chat.completions.create(
        model="gpt-4o-ca",
        messages=messages,
        temperature=0.8,      # 适度随机性，保持创造力
        max_tokens=2000       # 限制单次回复长度
    )
    
    # 3. 提取响应和统计信息
    assistant_message = response.choices[0].message.content
    prompt_tokens = response.usage.prompt_tokens
    completion_tokens = response.usage.completion_tokens
    
    # 4. 计算费用（gpt-4o-ca定价）
    cost = (prompt_tokens * 0.000005 + completion_tokens * 0.000015)
    
    # 5. 更新会话状态
    st.session_state.total_tokens += response.usage.total_tokens
    st.session_state.total_cost += cost
    st.session_state.messages.extend([
        {"role": "user", "content": user_message},
        {"role": "assistant", "content": assistant_message}
    ])
    
    return assistant_message, tokens_used, cost
```

**关键参数说明**：

| 参数 | 值 | 说明 |
|-----|----|----|
| model | gpt-4o-ca | OpenAI的GPT-4o加拿大区模型 |
| temperature | 0.8 | 适度随机性，平衡创造力和一致性 |
| max_tokens | 2000 | 单次响应最大Token数，避免过长 |

### 4. Token计数与费用统计 (`utils.py`)

#### 4.1 Token计数实现

```python
def count_tokens(text, model="gpt-4"):
    try:
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
    except:
        # 备用方案：粗略估算（1 token ≈ 4 字符）
        return len(text) // 4
```

**技术要点**：
- 使用 `tiktoken` 库精确计算Token数
- 提供降级方案，确保健壮性

#### 4.2 费用计算

```python
# gpt-4o-ca 定价（2024标准）
INPUT_COST_PER_TOKEN = 0.000005   # $5/1M tokens
OUTPUT_COST_PER_TOKEN = 0.000015  # $15/1M tokens

# 计算公式
cost = (prompt_tokens * INPUT_COST_PER_TOKEN + 
        completion_tokens * OUTPUT_COST_PER_TOKEN)
```

**精确性保障**：
- 区分输入和输出Token的不同定价
- 使用API返回的实际Token数，避免估算误差

### 5. 对话历史管理

#### 5.1 保存功能

```python
def save_chat_history(character_name, messages):
    # 创建存储目录
    if not os.path.exists("chat_history"):
        os.makedirs("chat_history")
    
    # 生成时间戳文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"chat_history/{character_name}_{timestamp}.json"
    
    # 构建数据结构
    data = {
        "character": character_name,
        "timestamp": timestamp,
        "messages": messages
    }
    
    # 保存为JSON格式
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return filename
```

**文件格式示例**：
```json
{
  "character": "sherlock",
  "timestamp": "20241102_153045",
  "messages": [
    {
      "role": "user",
      "content": "你好，福尔摩斯先生"
    },
    {
      "role": "assistant",
      "content": "显而易见，你是来寻求我的帮助的..."
    }
  ]
}
```

#### 5.2 加载功能

```python
def load_chat_history(filename):
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data
```

### 6. 头像管理系统

#### 6.1 本地图片优化

为了提升加载速度和减少带宽消耗，系统实现了智能图片优化：

```python
def optimize_image(img_data, max_size=300, quality=85):
    """优化图片：调整大小并压缩"""
    img = Image.open(io.BytesIO(img_data))
    
    # 1. 转换为RGB模式（统一格式）
    if img.mode in ('RGBA', 'LA', 'P'):
        background = Image.new('RGB', img.size, (255, 255, 255))
        if img.mode == 'P':
            img = img.convert('RGBA')
        background.paste(img, mask=img.split()[-1])
        img = background
    
    # 2. 调整大小（保持宽高比）
    if max(img.size) > max_size:
        img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
    
    # 3. 压缩保存
    output = io.BytesIO()
    img.save(output, format='JPEG', quality=85, optimize=True)
    return output.getvalue()
```

**优化策略**：
- 尺寸限制：最大边长300px，适合头像显示
- 格式统一：转换为JPEG，压缩率更高
- 质量平衡：85%质量，视觉效果与文件大小的最佳平衡

#### 6.2 Base64编码

```python
def get_character_avatar(character_id, character_info):
    """获取角色头像，自动优化并转换为base64"""
    local_path = Path(character_info['avatar_local'])
    
    if local_path.exists():
        with open(local_path, "rb") as img_file:
            img_data = img_file.read()
        
        # 文件大小超过200KB时自动优化
        if len(img_data) / 1024 > 200:
            img_data = optimize_image(img_data)
        
        # 转换为base64 Data URL
        base64_img = base64.b64encode(img_data).decode()
        return f"data:image/jpeg;base64,{base64_img}"
    
    # 降级方案：使用在线URL
    return character_info.get('avatar', character_info.get('emoji', '👤'))
```

**技术优势**：
- **离线可用**：base64编码嵌入HTML，无需外部请求
- **加载速度**：避免多次HTTP请求
- **智能优化**：仅对大文件进行压缩处理

### 7. UI设计与样式

#### 7.1 CSS样式系统

系统通过内嵌CSS实现现代化UI：

```css
/* 全局字体优化 */
html, body, [class*="css"] {
    font-size: 14px;
}

/* 按钮交互动画 */
.stButton>button:hover {
    transform: translateY(-2px);
    transition: all 0.3s ease;
}

/* 消息渐入动画 */
@keyframes fadeIn {
    from { 
        opacity: 0; 
        transform: translateY(10px); 
    }
    to { 
        opacity: 1; 
        transform: translateY(0); 
    }
}

/* 统计指标渐变背景 */
div[data-testid="metric-container"] {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 10px;
}
```

#### 7.2 头像一致性控制

```css
/* 主区域头像 - 60x60px */
.character-avatar {
    width: 60px !important;
    height: 60px !important;
    border-radius: 50%;
    object-fit: cover;
}

/* 侧边栏头像 - 40x40px */
.sidebar-avatar {
    width: 40px !important;
    height: 40px !important;
    border-radius: 50%;
    object-fit: cover;
}

/* 聊天消息头像 - 40x40px */
.stChatMessage img {
    width: 40px !important;
    height: 40px !important;
    border-radius: 50%;
    object-fit: cover;
}
```

**设计原则**：
- **统一性**：所有头像统一圆形样式
- **一致性**：固定尺寸避免布局抖动
- **美观性**：边框阴影增强视觉效果

### 8. 页面布局结构

#### 8.1 侧边栏设计

```python
with st.sidebar:
    st.title("🎭 角色选择")
    
    # 角色按钮列表
    for char_id, char_info in CHARACTERS.items():
        with st.container():
            col1, col2 = st.columns([1, 4])
            with col1:
                # 头像显示
                st.markdown(f'<img src="{avatar_url}" class="sidebar-avatar" />')
            with col2:
                # 选择按钮
                if st.button(char_info['name'], ...):
                    switch_character(char_id)
    
    # 统计信息
    st.subheader("📊 使用统计")
    st.metric("总Token消耗", f"{st.session_state.total_tokens:,}")
    st.metric("预估费用", f"${st.session_state.total_cost:.6f}")
    
    # 功能按钮
    st.button("🗑️ 清空对话")
    st.button("💾 保存对话历史")
```

#### 8.2 主对话区域

```python
# 角色信息头部
col_header1, col_header2 = st.columns([1, 9])
with col_header1:
    st.markdown(f'<img src="{avatar_url}" class="character-avatar" />')
with col_header2:
    st.markdown(f"<h2>正在与 {character['name']} 对话</h2>")

# 可折叠的角色详情
with st.expander("📖 查看角色详情"):
    st.markdown(f"**背景：** {character['background']}")
    st.markdown(f"**性格特点：** {character['personality']}")

# 对话历史显示
for message in st.session_state.messages:
    if message["role"] == "user":
        with st.chat_message("user", avatar="👤"):
            st.markdown(message["content"])
    else:
        with st.chat_message("assistant", avatar=avatar_url):
            st.markdown(message["content"])

# 输入框
user_input = st.chat_input("输入你的消息...")
```

---

## 关键技术难点与解决方案

### 难点1：角色人设一致性保持

**问题**：如何确保AI在长对话中始终保持角色设定？

**解决方案**：
1. **详细的系统提示词**：包含背景、性格、语言风格三个维度
2. **8条强制规则**：明确约束AI的行为模式
3. **第一人称强制**：要求用"我"来增强沉浸感
4. **输出质量要求**：3-5句或更多，避免敷衍回复
5. **完整上下文维护**：每次请求都包含完整对话历史

### 难点2：Token消耗控制

**问题**：长对话会导致Token消耗急剧增加。

**解决方案**：
1. **单次响应限制**：max_tokens=2000，避免过长回复
2. **实时统计展示**：让用户了解消耗情况
3. **角色切换清空**：避免不必要的历史累积
4. **精确计费**：使用API返回的实际Token数

### 难点3：头像加载性能

**问题**：网络头像加载慢，影响用户体验。

**解决方案**：
1. **本地图片优先**：优先使用本地assets
2. **base64嵌入**：避免额外HTTP请求
3. **智能压缩**：超过200KB自动优化
4. **降级方案**：本地失败时使用在线URL
5. **格式统一**：统一转换为JPEG格式

### 难点4：会话状态管理

**问题**：Streamlit页面刷新会导致状态丢失。

**解决方案**：
1. **session_state持久化**：所有关键数据存储在session_state
2. **API客户端复用**：避免重复初始化
3. **历史保存功能**：重要对话可导出JSON文件

---

## 性能优化

### 1. API调用优化

- **Temperature设置**：0.8，平衡创造力和一致性
- **Max Tokens限制**：2000，控制单次响应长度
- **错误处理**：try-except包裹API调用，提供友好错误提示

### 2. 前端性能

- **CSS动画**：使用transition和transform，流畅不卡顿
- **图片优化**：自动压缩大图，减少加载时间
- **按需加载**：角色详情使用expander折叠，减少初始渲染

### 3. 数据管理

- **JSON格式**：对话历史使用JSON，易于解析和备份
- **时间戳命名**：避免文件名冲突
- **UTF-8编码**：确保中文正确保存

---

## 项目使用说明

### 环境配置

#### 1. 安装Python依赖

```bash
pip install -r requirements.txt
```

**依赖说明**：
- `streamlit>=1.28.0` - Web应用框架
- `openai>=1.3.0` - OpenAI API客户端
- `tiktoken>=0.5.1` - Token计数工具
- `Pillow>=10.0.0` - 图像处理库

#### 2. 配置环境变量

**方案一：系统环境变量**

Windows (cmd):
```cmd
set OPENAI_API_KEY=sk-your-api-key-here
set OPENAI_BASE_URL=https://api.openai.com/v1
```

Windows (PowerShell):
```powershell
$env:OPENAI_API_KEY="sk-your-api-key-here"
$env:OPENAI_BASE_URL="https://api.openai.com/v1"
```

Linux/Mac:
```bash
export OPENAI_API_KEY=sk-your-api-key-here
export OPENAI_BASE_URL=https://api.openai.com/v1
```

**方案二：使用.env文件**（推荐）

创建 `.env` 文件：
```env
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_BASE_URL=https://api.openai.com/v1
```

修改 `app.py` 添加支持：
```python
from dotenv import load_dotenv
load_dotenv()  # 在文件开头添加
```

### 启动应用

#### 方法1：使用启动脚本（推荐）

**Windows:**
```cmd
run.bat
```

**Linux/Mac:**
```bash
chmod +x run.sh
./run.sh
```

#### 方法2：直接运行

```bash
streamlit run app.py
```

启动后会自动打开浏览器访问 `http://localhost:8501`

### 使用流程

1. **选择角色**
   - 点击左侧边栏的角色按钮
   - 当前选中的角色按钮会高亮显示

2. **查看角色信息**
   - 点击"📖 查看角色详情"展开
   - 了解角色的背景、性格和语言风格

3. **开始对话**
   - 在底部输入框输入消息
   - 按回车或点击发送按钮
   - 等待AI生成回复

4. **监控消耗**
   - 侧边栏实时显示Token消耗
   - 每条消息下方显示单次消耗

5. **保存对话**
   - 点击"💾 保存对话历史"按钮
   - 文件保存在 `chat_history/` 目录
   - 文件名格式：`角色名_时间戳.json`

6. **切换角色**
   - 随时点击其他角色按钮
   - 会自动清空当前对话历史
   - Token统计不会清空

7. **清空对话**
   - 点击"🗑️ 清空对话"按钮
   - 仅清空当前角色的对话历史
   - Token统计不会清空

### 清理缓存

如果遇到问题，可以清理Streamlit缓存：

**Windows:**
```cmd
clear_cache.bat
```

**Linux/Mac:**
```bash
chmod +x clear_cache.sh
./clear_cache.sh
```

---

## 费用说明

### 定价标准（gpt-4o-ca）

| Token类型 | 单价 | 说明 |
|----------|------|------|
| 输入Token | $0.000005/token | 约$5/1M tokens |
| 输出Token | $0.000015/token | 约$15/1M tokens |

### 消耗估算

- **普通对话**：每轮约1000-2000 tokens，费用约$0.01-0.02
- **长对话**：10轮约10000-20000 tokens，费用约$0.10-0.20
- **角色切换**：会清空历史，重新开始计数

### 节省建议

1. 避免过于冗长的输入
2. 定期清空对话历史
3. 关注侧边栏的费用统计
4. 使用max_tokens限制响应长度

---

## 常见问题

### Q1: 启动时提示API Key错误？

**A**: 检查环境变量是否正确设置：
```bash
# Windows
echo %OPENAI_API_KEY%

# Linux/Mac
echo $OPENAI_API_KEY
```

### Q2: 角色回复不符合人设？

**A**: 可能原因：
1. 对话历史过长，上下文混淆
2. Temperature参数设置（已优化为0.8）
3. 尝试清空对话重新开始

### Q3: 头像不显示？

**A**: 检查步骤：
1. 确认 `assets/` 目录存在
2. 检查图片文件是否存在
3. 查看控制台是否有错误信息

### Q4: 对话历史保存在哪里？

**A**: 保存在项目根目录的 `chat_history/` 文件夹，格式为JSON。

### Q5: 如何修改角色设定？

**A**: 编辑 `characters.py` 文件中的CHARACTERS字典，修改对应角色的属性。

---

## 扩展开发建议

### 1. 添加新角色

在 `characters.py` 中添加新角色：

```python
CHARACTERS = {
    # ... 现有角色 ...
    
    "new_character": {
        "name": "角色名称",
        "emoji": "🎭",
        "avatar_local": "./assets/new_character.png",
        "source": "作品来源",
        "background": "详细背景...",
        "personality": "性格特点...",
        "speaking_style": "语言风格..."
    }
}
```

### 2. 支持更多模型

修改 `chat_with_character()` 函数中的model参数：

```python
response = st.session_state.client.chat.completions.create(
    model="gpt-4-turbo",  # 或其他模型
    messages=messages,
    temperature=0.8,
    max_tokens=2000
)
```

### 3. 添加对话导入功能

扩展 `utils.py` 添加导入函数：

```python
def import_chat_history(filename):
    data = load_chat_history(filename)
    st.session_state.current_character = data['character']
    st.session_state.messages = data['messages']
```

### 4. 实现多轮对话摘要

当对话过长时，使用GPT生成摘要，压缩上下文：

```python
def summarize_conversation(messages):
    # 使用GPT生成前N轮对话的摘要
    # 用摘要替换原始消息，减少Token消耗
    pass
```

### 5. 添加语音输入输出

集成语音识别和TTS功能：

```python
# 使用Whisper API进行语音转文字
# 使用TTS API进行文字转语音
```

---

## 总结

本项目实现了一个功能完善、用户体验优秀的角色扮演聊天机器人系统。通过精心设计的架构和优化策略，在保证角色一致性的同时，有效控制了Token消耗和响应速度。项目代码结构清晰，易于维护和扩展，为AI对话系统开发提供了良好的参考范例。

### 技术亮点

✅ 多角色系统提示词工程  
✅ 完整的上下文管理机制  
✅ 精确的Token计数和费用统计  
✅ 智能的图片优化和加载策略  
✅ 现代化的UI设计和交互体验  
✅ 健壮的错误处理和降级方案  
✅ 灵活的配置和扩展能力  

### 应用价值

- 📚 **教育领域**：历史人物对话、文学角色互动
- 🎮 **娱乐领域**：角色扮演游戏、互动故事
- 💼 **商业领域**：客服机器人、品牌形象代言
- 🔬 **研究领域**：人机交互、对话系统研究

---

**项目完成时间**: 2024年11月  
**技术栈版本**: Python 3.8+, Streamlit 1.28.0, OpenAI API 1.3.0  
**作者**: [您的名字]  
**许可**: MIT License (仅用于学习和演示)

