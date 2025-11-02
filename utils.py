import tiktoken
import json
from datetime import datetime
import os
from pathlib import Path
import base64
from PIL import Image
import io

def count_tokens(text, model="gpt-4"):
    try:
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
    except:
        return len(text) // 4

def format_cost(tokens, input_cost_per_1k=0.03, output_cost_per_1k=0.06):
    input_tokens = tokens * 0.7
    output_tokens = tokens * 0.3
    cost = (input_tokens / 1000) * input_cost_per_1k + (output_tokens / 1000) * output_cost_per_1k
    return cost

def save_chat_history(character_name, messages):
    if not os.path.exists("chat_history"):
        os.makedirs("chat_history")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"chat_history/{character_name}_{timestamp}.json"
    
    data = {
        "character": character_name,
        "timestamp": timestamp,
        "messages": messages
    }
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return filename

def load_chat_history(filename):
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

def optimize_image(img_data, max_size=300, quality=85):
    """
    优化图片：调整大小并压缩
    """
    try:
        # 打开图片
        img = Image.open(io.BytesIO(img_data))
        
        # 转换为RGB模式（如果是RGBA或其他模式）
        if img.mode in ('RGBA', 'LA', 'P'):
            # 创建白色背景
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # 调整大小（保持宽高比，限制最大边长）
        if max(img.size) > max_size:
            img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        
        # 保存到字节流
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=quality, optimize=True)
        return output.getvalue()
    except Exception as e:
        print(f"Error optimizing image: {e}")
        return img_data

def get_character_avatar(character_id, character_info):
    """
    获取角色头像，优先使用本地图片
    如果本地图片存在，自动优化并转换为base64编码
    """
    # 优先使用配置中的avatar_local路径
    if 'avatar_local' in character_info:
        avatar_local = character_info['avatar_local']
        local_path = Path(avatar_local)
        if local_path.exists():
            try:
                # 获取文件扩展名
                ext = local_path.suffix.lower()
                
                # 读取图片
                with open(local_path, "rb") as img_file:
                    img_data = img_file.read()
                
                # SVG和GIF不需要优化，直接使用
                if ext in ['.svg', '.gif']:
                    base64_img = base64.b64encode(img_data).decode()
                    mime_type = 'image/svg+xml' if ext == '.svg' else 'image/gif'
                    return f"data:{mime_type};base64,{base64_img}"
                
                # 检查文件大小，如果超过200KB则优化
                file_size_kb = len(img_data) / 1024
                if file_size_kb > 200:
                    print(f"优化 {character_id} 头像 ({file_size_kb:.1f}KB -> ", end="")
                    img_data = optimize_image(img_data, max_size=300, quality=85)
                    optimized_size_kb = len(img_data) / 1024
                    print(f"{optimized_size_kb:.1f}KB)")
                
                # 转换为base64
                base64_img = base64.b64encode(img_data).decode()
                
                # 使用JPEG格式（优化后都是JPEG）
                mime_type = 'image/jpeg' if file_size_kb > 200 else 'image/png'
                
                # 返回base64格式的data URL
                return f"data:{mime_type};base64,{base64_img}"
            except Exception as e:
                print(f"Error loading avatar_local {local_path}: {e}")
    
    # 备用方案：尝试用character_id直接查找
    for ext in ['.png', '.jpg', '.jpeg', '.svg', '.gif']:
        local_path = Path(f"./assets/{character_id}{ext}")
        if local_path.exists():
            try:
                # 读取图片
                with open(local_path, "rb") as img_file:
                    img_data = img_file.read()
                
                # SVG和GIF不需要优化，直接使用
                if ext in ['.svg', '.gif']:
                    base64_img = base64.b64encode(img_data).decode()
                    mime_type = 'image/svg+xml' if ext == '.svg' else 'image/gif'
                    return f"data:{mime_type};base64,{base64_img}"
                
                # 检查文件大小，如果超过200KB则优化
                file_size_kb = len(img_data) / 1024
                if file_size_kb > 200:
                    print(f"优化 {character_id} 头像 ({file_size_kb:.1f}KB -> ", end="")
                    img_data = optimize_image(img_data, max_size=300, quality=85)
                    optimized_size_kb = len(img_data) / 1024
                    print(f"{optimized_size_kb:.1f}KB)")
                
                # 转换为base64
                base64_img = base64.b64encode(img_data).decode()
                
                # 使用JPEG格式（优化后都是JPEG）
                mime_type = 'image/jpeg' if file_size_kb > 200 else 'image/png'
                
                # 返回base64格式的data URL
                return f"data:{mime_type};base64,{base64_img}"
            except Exception as e:
                print(f"Error loading local image {local_path}: {e}")
                continue
    
    # 如果本地不存在或加载失败，使用在线URL
    return character_info.get('avatar', character_info.get('emoji', '👤'))

