"""
MCP (Model Context Protocol) 搜索增强模块
智能判断并执行网络搜索，为角色对话提供真实背景资料
"""
import re
import json
from typing import List, Dict, Optional
try:
    from ddgs import DDGS  # 新版本的包名
except ImportError:
    try:
        from duckduckgo_search import DDGS  # 向后兼容旧版本
    except ImportError:
        raise ImportError("请安装搜索包: pip install ddgs")
import requests
from bs4 import BeautifulSoup
from openai import OpenAI


class MCPSearchEngine:
    """MCP搜索引擎 - 智能判断并执行网络搜索"""
    
    def __init__(self, client: OpenAI):
        self.client = client
        self.ddgs = DDGS()
        
    def should_search(self, user_message: str, character_name: str) -> Dict:
        """
        使用GPT判断是否需要进行网络搜索
        
        参数:
            user_message: 用户的问题
            character_name: 当前角色名称
            
        返回:
            {
                "need_search": bool,
                "search_query": str,
                "reason": str
            }
        """
        decision_prompt = f"""你是一个智能助手，负责判断用户的问题是否需要网络搜索来增强回答。

角色：{character_name}
用户问题：{user_message}

请判断以下情况是否需要搜索：
1. 涉及具体的历史事件、故事情节细节
2. 提到原著中的具体场景、对话
3. 询问角色背景故事的详细内容
4. 需要引用原作内容的问题
5. 询问具体的技术细节、专业知识

如果需要搜索，请生成一个精确的搜索关键词（优先中文）。

请以JSON格式回复：
{{
    "need_search": true/false,
    "search_query": "搜索关键词",
    "reason": "判断理由"
}}"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # 使用更便宜的模型做判断
                messages=[{"role": "user", "content": decision_prompt}],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            print(f"MCP决策失败: {e}")
            return {"need_search": False, "search_query": "", "reason": "决策失败"}
    
    def search_web(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        使用DuckDuckGo搜索网络内容
        
        参数:
            query: 搜索关键词
            max_results: 最大结果数
            
        返回:
            搜索结果列表
        """
        try:
            results = []
            print(f"🔍 开始搜索: {query}")
            
            # 尝试多种搜索策略
            search_strategies = [
                {'region': None, 'safesearch': 'moderate'},  # 先不指定region
                {'region': 'wt-wt', 'safesearch': 'moderate'},  # 全球
                {'region': 'cn-zh', 'safesearch': 'off'},  # 中国区，关闭安全搜索
            ]
            
            for i, strategy in enumerate(search_strategies):
                try:
                    print(f"  策略 {i+1}: region={strategy['region']}, safesearch={strategy['safesearch']}")
                    
                    search_params = {
                        'keywords': query,
                        'max_results': max_results,
                        'safesearch': strategy['safesearch']
                    }
                    if strategy['region']:
                        search_params['region'] = strategy['region']
                    
                    # 注意：新版ddgs包的API可能有变化
                    search_results = self.ddgs.text(**search_params)
                    
                    # 将生成器转换为列表
                    search_results_list = list(search_results) if search_results else []
                    
                    if search_results_list:
                        for r in search_results_list:
                            results.append({
                                'title': r.get('title', ''),
                                'snippet': r.get('body', ''),
                                'url': r.get('href', '')
                            })
                        print(f"  ✅ 成功！找到 {len(results)} 条结果")
                        break  # 成功就退出
                    else:
                        print(f"  ❌ 策略 {i+1} 返回空结果，尝试下一个策略")
                        
                except Exception as strategy_error:
                    print(f"  ❌ 策略 {i+1} 失败: {strategy_error}")
                    continue
            
            if not results:
                print("⚠️ 所有搜索策略都未能找到结果")
            
            return results
            
        except Exception as e:
            print(f"❌ 搜索失败: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def summarize_search_results(self, query: str, results: List[Dict]) -> str:
        """
        使用GPT总结搜索结果
        
        参数:
            query: 搜索关键词
            results: 搜索结果列表
            
        返回:
            总结文本
        """
        if not results:
            return "未找到相关信息"
        
        # 构建搜索结果文本
        results_text = "\n\n".join([
            f"来源 {i+1}：{r['title']}\n{r['snippet']}"
            for i, r in enumerate(results[:3])  # 只用前3个结果
        ])
        
        summary_prompt = f"""请总结以下关于"{query}"的搜索结果，提取关键信息：

{results_text}

要求：
1. 只提取与问题直接相关的事实信息
2. 保持客观，不添加个人观点
3. 用简洁的语言，3-5句话概括
4. 如果信息有矛盾，指出不同说法
5. 保持中文输出"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": summary_prompt}],
                temperature=0.3,
                max_tokens=500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"总结失败: {e}")
            # 降级方案：直接返回前3个结果的摘要
            return "\n".join([r['snippet'][:200] for r in results[:3]])
    
    def enhance_context(self, 
                       user_message: str, 
                       character_name: str,
                       search_results_summary: str) -> str:
        """
        生成增强的上下文信息
        
        参数:
            user_message: 用户问题
            character_name: 角色名称
            search_results_summary: 搜索结果总结
            
        返回:
            增强的上下文文本
        """
        enhanced_context = f"""
【背景知识增强】
用户询问：{user_message}

相关背景资料（来自网络搜索）：
{search_results_summary}

请基于以上真实资料，结合角色{character_name}的身份和经历，给出准确、详细的回答。
注意：
1. 优先使用搜索到的真实信息
2. 保持角色的语言风格和性格特点
3. 如果搜索结果不充分，可以基于角色设定进行合理推测，但要说明
4. 自然地将背景知识融入回答中，不要生硬地照搬"""
        return enhanced_context


class MCPChatManager:
    """整合MCP搜索的对话管理器"""
    
    def __init__(self, openai_client: OpenAI):
        self.client = openai_client
        self.search_engine = MCPSearchEngine(openai_client)
        self.search_cache = {}  # 缓存搜索结果
    
    def chat_with_mcp(self, 
                      user_message: str,
                      character: Dict,
                      system_prompt: str,
                      conversation_history: List[Dict],
                      enable_search: bool = True,
                      model: str = "gpt-4o-ca",
                      temperature: float = 0.8,
                      max_tokens: int = 2000) -> Dict:
        """
        带MCP搜索增强的对话
        
        参数:
            user_message: 用户消息
            character: 角色信息字典
            system_prompt: 系统提示词
            conversation_history: 对话历史
            enable_search: 是否启用搜索
            model: 使用的模型
            temperature: 温度参数
            max_tokens: 最大token数
            
        返回:
            {
                "response": str,
                "tokens_used": int,
                "cost": float,
                "search_performed": bool,
                "search_query": str,
                "search_summary": str,
                "search_results": List[Dict]
            }
        """
        result = {
            "response": "",
            "tokens_used": 0,
            "cost": 0.0,
            "search_performed": False,
            "search_query": "",
            "search_summary": "",
            "search_results": []
        }
        
        # 1. MCP决策：是否需要搜索
        if enable_search:
            decision = self.search_engine.should_search(
                user_message, 
                character['name']
            )
            
            if decision['need_search']:
                search_query = decision['search_query']
                print(f"🔍 MCP触发搜索: {search_query}")
                
                # 检查缓存
                if search_query in self.search_cache:
                    search_summary = self.search_cache[search_query]['summary']
                    search_results = self.search_cache[search_query]['results']
                    print("📦 使用缓存的搜索结果")
                else:
                    # 2. 执行搜索
                    search_results = self.search_engine.search_web(search_query)
                    
                    if search_results:
                        # 3. 总结搜索结果
                        search_summary = self.search_engine.summarize_search_results(
                            search_query, 
                            search_results
                        )
                        
                        # 缓存结果
                        self.search_cache[search_query] = {
                            'summary': search_summary,
                            'results': search_results
                        }
                        print(f"✅ 搜索完成，找到 {len(search_results)} 条结果")
                    else:
                        search_summary = "未找到相关信息"
                        search_results = []
                        print("❌ 搜索无结果")
                
                # 4. 增强系统提示词
                enhanced_context = self.search_engine.enhance_context(
                    user_message,
                    character['name'],
                    search_summary
                )
                
                system_prompt = f"{system_prompt}\n\n{enhanced_context}"
                
                result['search_performed'] = True
                result['search_query'] = search_query
                result['search_summary'] = search_summary
                result['search_results'] = search_results
        
        # 5. 构建消息列表
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        messages.extend(conversation_history)
        messages.append({"role": "user", "content": user_message})
        
        # 6. 调用GPT生成回复
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            result['response'] = response.choices[0].message.content
            result['tokens_used'] = response.usage.total_tokens
            
            # 计算费用（gpt-4o-ca定价）
            prompt_tokens = response.usage.prompt_tokens
            completion_tokens = response.usage.completion_tokens
            result['cost'] = (prompt_tokens * 0.000005 + 
                            completion_tokens * 0.000015)
            
        except Exception as e:
            print(f"GPT调用失败: {e}")
            result['response'] = f"抱歉，回复生成失败：{str(e)}"
        
        return result

