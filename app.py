import streamlit as st
import os
from openai import OpenAI
from datetime import datetime
import json

from characters import CHARACTERS
from utils import count_tokens, format_cost, save_chat_history, load_chat_history, get_character_avatar

st.set_page_config(
    page_title="角色扮演聊天机器人",
    page_icon="🎭",
    layout="wide",
    initial_sidebar_state="expanded"
)

def load_css():
    st.markdown("""
    <style>
    /* 全局字体大小调整 */
    html, body, [class*="css"] {
        font-size: 14px;
    }
    
    h1 {
        font-size: 1.8rem !important;
    }
    
    h2 {
        font-size: 1.5rem !important;
    }
    
    h3 {
        font-size: 1.2rem !important;
    }
    
    p, div, span, label {
        font-size: 0.9rem !important;
    }
    
    .stButton>button {
        border-radius: 10px;
        font-weight: 500;
        transition: all 0.3s ease;
        font-size: 0.85rem !important;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
    }
    
    div[data-testid="stExpander"] {
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .chat-message {
        animation: fadeIn 0.5s ease-in;
    }
    
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
    
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        padding: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    div[data-testid="metric-container"] label {
        font-size: 0.75rem !important;
    }
    
    div[data-testid="metric-container"] [data-testid="stMetricValue"] {
        font-size: 1.2rem !important;
    }
    
    .character-header {
        background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%);
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    /* 聊天消息字体 */
    .stChatMessage {
        font-size: 0.9rem !important;
    }
    
    /* 输入框字体 */
    .stChatInput input {
        font-size: 0.9rem !important;
    }
    
    /* 侧边栏标题 */
    .css-1d391kg, [data-testid="stSidebar"] h1 {
        font-size: 1.3rem !important;
    }
    
    /* 头像样式 - 固定大小确保一致性 */
    .character-avatar {
        width: 60px !important;
        height: 60px !important;
        border-radius: 50%;
        object-fit: cover;
        border: 3px solid #FF6B6B;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
        display: block;
    }
    
    .sidebar-avatar {
        width: 40px !important;
        height: 40px !important;
        border-radius: 50%;
        object-fit: cover;
        border: 2px solid #FF6B6B;
        display: block;
    }
    
    /* 确保聊天消息中的头像也一致 */
    .stChatMessage img {
        width: 40px !important;
        height: 40px !important;
        border-radius: 50%;
        object-fit: cover;
    }
    </style>
    """, unsafe_allow_html=True)

def init_session_state():
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'current_character' not in st.session_state:
        st.session_state.current_character = None
    if 'total_tokens' not in st.session_state:
        st.session_state.total_tokens = 0
    if 'total_cost' not in st.session_state:
        st.session_state.total_cost = 0.0
    if 'client' not in st.session_state:
        api_key = os.getenv('OPENAI_API_KEY')
        base_url = os.getenv('OPENAI_BASE_URL')
        if not api_key or not base_url:
            st.error("请设置 OPENAI_API_KEY 和 OPENAI_BASE_URL 环境变量")
            st.stop()
        st.session_state.client = OpenAI(api_key=api_key, base_url=base_url)

def switch_character(character_name):
    if st.session_state.current_character != character_name:
        st.session_state.current_character = character_name
        st.session_state.messages = []

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

def chat_with_character(user_message):
    character = CHARACTERS[st.session_state.current_character]
    
    messages = [
        {"role": "system", "content": get_system_prompt(st.session_state.current_character)}
    ]
    
    for msg in st.session_state.messages:
        messages.append({"role": msg["role"], "content": msg["content"]})
    
    messages.append({"role": "user", "content": user_message})
    
    try:
        response = st.session_state.client.chat.completions.create(
            model="gpt-4o-ca",
            messages=messages,
            temperature=0.8,
            max_tokens=2000
        )
        
        assistant_message = response.choices[0].message.content
        tokens_used = response.usage.total_tokens
        
        prompt_tokens = response.usage.prompt_tokens
        completion_tokens = response.usage.completion_tokens
        cost = (prompt_tokens * 0.000005 + completion_tokens * 0.000015)
        
        st.session_state.total_tokens += tokens_used
        st.session_state.total_cost += cost
        
        st.session_state.messages.append({"role": "user", "content": user_message})
        st.session_state.messages.append({"role": "assistant", "content": assistant_message})
        
        return assistant_message, tokens_used, cost
        
    except Exception as e:
        st.error(f"API调用失败: {str(e)}")
        return None, 0, 0.0

def main():
    init_session_state()
    load_css()
    
    with st.sidebar:
        st.title("🎭 角色选择")
        
        for char_id, char_info in CHARACTERS.items():
            with st.container():
                col1, col2 = st.columns([1, 4])
                with col1:
                    avatar_url = get_character_avatar(char_id, char_info)
                    st.markdown(
                        f'<img src="{avatar_url}" class="sidebar-avatar" />',
                        unsafe_allow_html=True
                    )
                with col2:
                    if st.button(
                        char_info['name'],
                        key=f"btn_{char_id}",
                        use_container_width=True,
                        type="primary" if st.session_state.current_character == char_id else "secondary"
                    ):
                        switch_character(char_id)
                        st.rerun()
        
        st.divider()
        
        st.subheader("📊 使用统计")
        st.metric("总Token消耗", f"{st.session_state.total_tokens:,}")
        st.metric("预估费用", f"${st.session_state.total_cost:.6f}")
        
        st.divider()
        
        if st.button("🗑️ 清空对话", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
        
        if st.button("💾 保存对话历史", use_container_width=True):
            if st.session_state.messages and st.session_state.current_character:
                filename = save_chat_history(
                    st.session_state.current_character,
                    st.session_state.messages
                )
                st.success(f"已保存到 {filename}")
    
    st.title("🎭 角色扮演聊天机器人")
    
    if not st.session_state.current_character:
        st.info("👈 请在左侧选择一个角色开始对话")
        
        st.markdown("### 可选角色介绍")
        cols = st.columns(2)
        for idx, (char_id, char_info) in enumerate(CHARACTERS.items()):
            with cols[idx % 2]:
                with st.expander(f"{char_info['emoji']} {char_info['name']}"):
                    st.markdown(f"**来源：** {char_info['source']}")
                    st.markdown(f"**背景：** {char_info['background']}")
                    st.markdown(f"**性格：** {char_info['personality']}")
    else:
        character = CHARACTERS[st.session_state.current_character]
        
        avatar_url = get_character_avatar(st.session_state.current_character, character)
        
        col_header1, col_header2 = st.columns([1, 9])
        with col_header1:
            st.markdown(
                f'<img src="{avatar_url}" class="character-avatar" />',
                unsafe_allow_html=True
            )
        with col_header2:
            st.markdown(f"""
            <div style="padding-top: 5px;">
                <h2 style="margin:0;">正在与 {character['name']} 对话</h2>
                <p style="margin:5px 0 0 0; color: rgba(255,255,255,0.6); font-size: 0.85rem;">来源：{character['source']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with st.expander("📖 查看角色详情"):
            st.markdown(f"**背景：** {character['background']}")
            st.markdown(f"**性格特点：** {character['personality']}")
            st.markdown(f"**语言风格：** {character['speaking_style']}")
        
        chat_container = st.container()
        with chat_container:
            for message in st.session_state.messages:
                if message["role"] == "user":
                    with st.chat_message("user", avatar="👤"):
                        st.markdown(message["content"])
                else:
                    with st.chat_message("assistant", avatar=avatar_url):
                        st.markdown(message["content"])
        
        user_input = st.chat_input("输入你的消息...")
        
        if user_input:
            with st.chat_message("user", avatar="👤"):
                st.markdown(user_input)
            
            with st.chat_message("assistant", avatar=avatar_url):
                with st.spinner(f"{character['name']}正在思考..."):
                    response, tokens, cost = chat_with_character(user_input)
                    if response:
                        st.markdown(response)
                        st.caption(f"💰 本次消耗: {tokens} tokens (${cost:.6f})")
            
            st.rerun()

if __name__ == "__main__":
    main()

