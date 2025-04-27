# Content from: https://www.aivi.fyi/aiagents/introduce-ADK

Source URL: `https://www.aivi.fyi/aiagents/introduce-ADK`
Fetched on: 2025-04-14 05:10:32 CST

---

🚀颠覆传统智能体！ADK谷歌最强AI智能体发布！支持MCP与ollama！Agent Development Kit详细教程！超越AutoGen和LangChain!轻松打造多智能体系统！自带UI界面！- 完整教程
在人工智能领域，单一功能模型逐渐让位于更复杂的多智能体系统。这些系统通过多个智能体协同工作，能够完成复杂任务。然而，多智能体系统的开发往往面临诸多挑战。为了解决这一问题，Google在Google Cloud NEXT 2025大会上推出了一款全新的开源框架——Agent Development Kit (ADK)，旨在简化多智能体应用的开发流程。
🚀本篇笔记所对应的视频：
- 👉👉👉 通过哔哩哔哩观看
- 👉👉👉 通过YouTube观看
- 👉👉👉 我的开源项目
- 👉👉👉 请我喝咖啡
- 👉👉👉 我的微信：stoeng
- 👉👉👉 承接大模型微调、RAG、AI智能体、AI相关应用开发等项目。
🔥AI智能体相关视频
什么是Agent Development Kit？
ADK是一个灵活且模块化的框架，专为开发和部署AI智能体而设计。它支持构建对话型和非对话型智能体，能够处理复杂任务和工作流。ADK不仅适用于Google生态系统中的Gemini模型，还兼容其他主流大语言模型（LLMs）和开源生成式AI工具。这一框架的核心目标是让开发者能够快速构建、管理、评估并部署生产级的智能体应用。
ADK的核心功能
ADK覆盖了智能体开发生命周期的每一个阶段，从逻辑定义到生产部署，提供了一系列强大的工具和功能：
- 简化开发：通过直观的Python代码，开发者可以用不到100行代码快速构建一个AI智能体。
- 动态路由与行为控制：支持基于LLM驱动的动态路由以及确定性逻辑控制，让开发者对智能体行为有更精确的掌控。
- 多模态交互：ADK支持双向音频和视频流，使得人机交互更加自然。
- 预配置样本与工具：内置丰富的样本库（Agent Garden），涵盖零售、客户服务等场景，帮助开发者快速上手。
- 跨平台部署：支持多种部署环境，包括本地调试、容器化运行时（如Kubernetes）以及Google Vertex AI。
与Google生态深度集成
ADK特别优化了与Google Cloud生态系统的集成，例如与Gemini 2.5 Pro Experimental模型和Vertex AI平台无缝衔接。通过这些集成，开发者可以充分利用Gemini模型的增强推理能力，并直接将智能体部署到企业级运行时环境中。此外，ADK还支持Model Context Protocol (MCP)，一种由Anthropic创建的数据连接协议，用于在不同智能体之间实现标准化的数据传输。
企业级扩展能力
为了满足企业需求，Google还推出了Agent Engine作为ADK的重要补充。这一托管运行时接口提供了从概念验证到生产部署的一站式解决方案，包括上下文管理、基础设施监控、扩展、安全性评估等功能。此外，Agent Engine还支持长短期记忆功能，使得智能体能够根据历史上下文进行更精准的决策。
应用场景与未来展望
ADK已经在多个行业中展现出强大的应用潜力。例如：
- 零售商可以利用ADK构建动态定价系统，通过多智能体协作优化价格策略。
- 汽车行业则使用ADK分析地理和交通数据，为电动车充电站选址提供决策支持。
- 媒体公司借助ADK进行视频分析，大幅提升内容处理效率。
未来，Google计划进一步扩展ADK及其相关工具，如引入模拟环境以测试智能体在真实场景中的表现，并推动开放协议（如Agent2Agent Protocol），实现跨平台、多供应商智能体之间的无缝协作。
Google的Agent Development Kit以其模块化设计、灵活性以及与Google生态系统的深度集成，为多智能体系统开发提供了强大的支持。无论是初创企业还是大型企业，这一框架都能帮助开发者快速从概念验证迈向生产部署，为人工智能应用带来更多可能性。
🚀部署和启动
pip install google-adk
pip install litellm
pip install mcp
pip install mcp-server-fetch
mkdir multi_tool_agent/
echo "from . import agent" > multi_tool_agent/__init__.py
touch multi_tool_agent/agent.py
touch multi_tool_agent/.env
GOOGLE_GENAI_USE_VERTEXAI="False"
GOOGLE_API_KEY="gemini api key"
OPENAI_API_KEY="openai api key"
adk run my_agent
adk web
# 浏览器打开:
http://localhost:8000/
# 设置openai api
export OPENAI_API_KEY="YOUR_OPENAI_API_KEY"
🔥最简单的demo
# my_agent/agent.py
from google.adk.agents import Agent
root_agent = Agent(
name="simple_assistant",
model="gemini-2.0-flash-exp", # Or your preferred Gemini model
instruction="You are a helpful assistant.",
description="A helpful assistant.",
)
🔥调用ollama里的模型
## 🔥 调用ollama模型
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
# 创建使用Ollama Gemma模型的代理
root_agent = LlmAgent(
model=LiteLlm(model="ollama/gemma3:12b"), # Correct format for Ollama models
name="helpful_agent",
description=(
"a helpful assistant."
),
instruction=(
"You are a helpful assistant"
),
)
🔥天气预报agent
## 🔥天气预报
import datetime
import requests
from zoneinfo import ZoneInfo
from google.adk.agents import Agent
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
# 城市名称映射字典，将中文城市名映射到英文
CITY_NAME_MAP = {
"纽约": "New York",
"伦敦": "London",
"东京": "Tokyo",
"北京": "Beijing",
"上海": "Shanghai",
"巴黎": "Paris",
"柏林": "Berlin",
"悉尼": "Sydney",
"莫斯科": "Moscow",
"迪拜": "Dubai",
# 可以继续添加更多常用城市
}
def get_weather(city: str) -> dict:
"""获取指定城市的当前天气报告。
使用weatherapi.com的API获取实时天气数据。
支持中文城市名，内部会自动转换为英文名。
参数:
city (str): 要获取天气报告的城市名称（中文或英文）。
返回:
dict: 包含状态和结果或错误信息的字典。
"""
# API密钥和基础URL
api_key = "你的key"
base_url = "http://api.weatherapi.com/v1/current.json"
# 检查城市名是否需要转换为英文
query_city = CITY_NAME_MAP.get(city, city)
try:
# 构建API请求
params = {
"key": api_key,
"q": query_city
}
# 发送GET请求到天气API
response = requests.get(base_url, params=params)
# 检查请求是否成功
if response.status_code == 200:
# 解析JSON响应
data = response.json()
# 提取相关天气信息
location = data["location"]["name"]
country = data["location"]["country"]
temp_c = data["current"]["temp_c"]
temp_f = data["current"]["temp_f"]
condition = data["current"]["condition"]["text"]
humidity = data["current"]["humidity"]
wind_kph = data["current"]["wind_kph"]
# 构建天气报告（使用原始输入的城市名）
report = (
f"当前{city}({country})的天气为{condition}，"
f"温度{temp_c}°C ({temp_f}°F)，"
f"湿度{humidity}%，风速{wind_kph}公里/小时。"
)
return {
"status": "success",
"report": report,
}
else:
# 处理API错误
return {
"status": "error",
"error_message": f"无法获取'{city}'的天气信息。API响应代码: {response.status_code}，请检查城市名称是否正确。"
}
except Exception as e:
# 处理其他异常
return {
"status": "error",
"error_message": f"获取'{city}'的天气信息时出错: {str(e)}"
}
def get_current_time(city: str) -> dict:
"""获取指定城市的当前时间。
使用weatherapi.com的API获取城市的时区信息，
然后根据时区计算当前时间。
支持中文城市名，内部会自动转换为英文名。
参数:
city (str): 要获取当前时间的城市名称（中文或英文）。
返回:
dict: 包含状态和结果或错误信息的字典。
"""
# API密钥和基础URL（与天气API相同）
api_key = "7dd6adfdddfb4309ab7132443240409"
base_url = "http://api.weatherapi.com/v1/current.json"
# 检查城市名是否需要转换为英文
query_city = CITY_NAME_MAP.get(city, city)
try:
# 构建API请求
params = {
"key": api_key,
"q": query_city
}
# 发送GET请求到API获取时区信息
response = requests.get(base_url, params=params)
# 检查请求是否成功
if response.status_code == 200:
# 解析JSON响应
data = response.json()
# 提取时区ID和本地时间
tz_id = data["location"]["tz_id"]
localtime = data["location"]["localtime"]
# 构建时间报告（使用原始输入的城市名）
report = f"当前{city}的时间是 {localtime} ({tz_id}时区)"
return {
"status": "success",
"report": report
}
else:
# 处理API错误
return {
"status": "error",
"error_message": f"无法获取'{city}'的时区信息。API响应代码: {response.status_code}，请检查城市名称是否正确。"
}
except Exception as e:
# 处理其他异常
return {
"status": "error",
"error_message": f"获取'{city}'的时间信息时出错: {str(e)}"
}
# 创建根代理
root_agent = Agent(
name="weather_time_agent", # 代理名称
model="gemini-2.0-flash-exp", # 使用的模型
description=(
"智能助手，可以回答关于各个城市的天气和时间问题。"
), # 代理描述
instruction=(
"我是一个能够提供城市天气和时间信息的智能助手。"
"当用户询问某个城市的天气情况时，使用get_weather工具获取最新天气数据。"
"当用户询问某个城市的当前时间时，使用get_current_time工具获取准确时间。"
"请以友好的方式回应用户的询问，并提供完整的天气或时间信息。"
"我能够理解中文城市名称，并自动转换为对应的英文名。"
), # 代理指令（中文版）
tools=[get_weather, get_current_time], # 可用工具
)
🔥MCP调用
# python ./multi_tool_agent/agent.py
import asyncio
from dotenv import load_dotenv
from google.genai import types
from google.adk.agents.llm_agent import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseServerParams, StdioServerParameters
# Load environment variables from .env file if needed
load_dotenv()
# --- Step 1: 获取工具的异步函数 ---
async def get_tools_async():
"""从MCP服务器获取工具"""
print("尝试连接到MCP服务器...")
tools, exit_stack = await MCPToolset.from_server(
connection_params=StdioServerParameters(
command='python3',
args=["-m", "mcp_server_fetch"],
)
)
print("MCP Toolset 创建成功.")
# MCP 需要维持与本地MCP服务器的连接
# exit_stack 管理这个连接的清理
return tools, exit_stack
# --- Step 2: 创建代理的异步函数 ---
async def get_agent_async():
"""创建一个配备了MCP服务器工具的ADK代理"""
tools, exit_stack = await get_tools_async()
print(f"从MCP服务器获取了 {len(tools)} 个工具.")
root_agent = LlmAgent(
model='gemini-2.0-flash', # 根据可用性调整模型名称
name='fetch_assistant',
instruction='使用可用工具帮助用户从网页中提取内容.',
tools=tools, # 将MCP工具提供给ADK代理
)
return root_agent, exit_stack
# --- Step 3: 主执行逻辑 ---
async def async_main():
session_service = InMemorySessionService()
artifacts_service = InMemoryArtifactService()
session = session_service.create_session(
state={}, app_name='mcp_fetch_app', user_id='user_fetch'
)
# 设置查询
query = "从 https://example.com 提取内容"
print(f"用户查询: '{query}'")
content = types.Content(role='user', parts=[types.Part(text=query)])
root_agent, exit_stack = await get_agent_async()
runner = Runner(
app_name='mcp_fetch_app',
agent=root_agent,
artifact_service=artifacts_service,
session_service=session_service,
)
print("运行代理中...")
events_async = runner.run_async(
session_id=session.id, user_id=session.user_id, new_message=content
)
async for event in events_async:
print(f"收到事件: {event}")
# 关键清理步骤: 确保MCP服务器进程连接已关闭
print("关闭MCP服务器连接...")
await exit_stack.aclose()
print("清理完成.")
if __name__ == '__main__':
try:
asyncio.run(async_main())
except Exception as e:
print(f"发生错误: {e}")
🔥代码优化agent
# 导入必要的库
from google.adk.agents.sequential_agent import SequentialAgent # 导入顺序代理
from google.adk.agents.llm_agent import LlmAgent # 导入LLM代理
from google.adk.agents import Agent # 导入基础代理类
from google.genai import types # 导入类型定义
from google.adk.sessions import InMemorySessionService # 导入内存会话服务
from google.adk.runners import Runner # 导入运行器
from google.adk.tools import FunctionTool # 导入函数工具，用于创建自定义工具
# --- 常量定义 ---
APP_NAME = "code_pipeline_app" # 应用名称
USER_ID = "dev_user_01" # 用户ID
SESSION_ID = "pipeline_session_01" # 会话ID
GEMINI_MODEL = "gemini-2.0-flash-exp" # 使用的Gemini模型
# --- 1. 定义代码处理管道的各个阶段子代理 ---
# 代码编写代理
# 接收初始规格说明(来自用户查询)并编写代码
code_writer_agent = LlmAgent(
name="CodeWriterAgent", # 代理名称
model=GEMINI_MODEL, # 使用的模型
instruction="""你是一个代码编写AI。
根据用户的请求，编写初始Python代码。
只输出原始代码块。
""", # 代理指令（中文版）
description="根据规格说明编写初始代码。", # 代理描述
# 将其输出(生成的代码)存储到会话状态中
# 键名为'generated_code'
output_key="generated_code" # 输出键，用于存储代理输出到会话状态
)
# 代码审查代理
# 读取上一个代理生成的代码(从状态中读取)并提供反馈
code_reviewer_agent = LlmAgent(
name="CodeReviewerAgent", # 代理名称
model=GEMINI_MODEL, # 使用的模型
instruction="""你是一个代码审查AI。
审查会话状态中键名为'generated_code'的Python代码。
提供关于潜在错误、风格问题或改进的建设性反馈。
注重清晰度和正确性。
仅输出审查评论。
""", # 代理指令（中文版）
description="审查代码并提供反馈。", # 代理描述
# 将其输出(审查评论)存储到会话状态中
# 键名为'review_comments'
output_key="review_comments" # 输出键，用于存储代理输出到会话状态
)
# 代码重构代理
# 获取原始代码和审查评论(从状态中读取)并重构代码
code_refactorer_agent = LlmAgent(
name="CodeRefactorerAgent", # 代理名称
model=GEMINI_MODEL, # 使用的模型
instruction="""你是一个代码重构AI。
获取会话状态键'generated_code'中的原始Python代码
以及会话状态键'review_comments'中的审查评论。
重构原始代码以解决反馈并提高其质量。
仅输出最终的、重构后的代码块。
""", # 代理指令（中文版）
description="根据审查评论重构代码。", # 代理描述
# 将其输出(重构的代码)存储到会话状态中
# 键名为'refactored_code'
output_key="refactored_code" # 输出键，用于存储代理输出到会话状态
)
# --- 2. 创建顺序代理 ---
# 这个代理通过按顺序运行子代理来编排流水线
code_pipeline_agent = SequentialAgent(
name="CodePipelineAgent", # 顺序代理名称
sub_agents=[code_writer_agent, code_reviewer_agent, code_refactorer_agent]
# 子代理将按提供的顺序运行：编写器 -> 审查器 -> 重构器
)
# --- 3. 创建一个函数作为工具 ---
def process_code_request(request: str) -> str:
"""
使用代码处理管道处理用户的代码请求。
Args:
request (str): 用户的代码请求，如"创建一个计算加法的函数"
Returns:
str: 处理后的最终代码
"""
print(f"处理代码请求: {request}")
# 这个函数实际上不会被执行，而是被LLM用来理解它应该如何使用code_pipeline_agent
# 真正的执行是通过root_agent对code_pipeline_agent的委托实现的
return "最终的代码将在这里返回"
# --- 4. 创建根代理 ---
root_agent = Agent(
name="CodeAssistant", # 根代理名称
model=GEMINI_MODEL, # 使用的模型
instruction="""你是一个代码助手AI。
你的角色是通过三步流水线帮助用户改进代码：
1. 根据规格说明编写初始代码
2. 审查代码以发现问题和改进
3. 根据审查反馈重构代码
当用户请求代码帮助时，使用code_pipeline_agent来处理请求。
将最终的、重构后的代码作为你的响应呈现给用户。
""", # 根代理指令（中文版）
description="通过编写-审查-重构流水线改进代码的助手。", # 根代理描述
# 不在工具中添加code_pipeline_agent，而是作为子代理
tools=[], # 这里可以为空，或者添加其他工具
sub_agents=[code_pipeline_agent] # 将code_pipeline_agent作为子代理
)
# 会话和运行器设置
session_service = InMemorySessionService() # 创建内存会话服务
session = session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID) # 创建会话
runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service) # 创建运行器
# 代理交互函数
def call_agent(query):
"""
调用代理并处理用户查询
Args:
query (str): 用户的查询文本
"""
content = types.Content(role='user', parts=[types.Part(text=query)]) # 创建用户内容
events = runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=content) # 运行代理
for event in events: # 遍历事件
if event.is_final_response(): # 如果是最终响应
final_response = event.content.parts[0].text # 获取响应文本
print("代理响应: ", final_response) # 打印响应
# 调用代理进行测试
call_agent("执行数学加法") # 测试查询
测试问题
优化下面的代码:
import urllib.request
contents = urllib.request.urlopen("https://www.aivi.fyi/").read()
Comments
