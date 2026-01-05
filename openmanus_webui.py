"""
OpenManus Web UI - Fixed for Gradio 6.0
"""

import gradio as gr
import subprocess
import os
import sys
from datetime import datetime

# Setup
OPENMANUS_PATH = r"C:\Users\tialc\Documents\GitHub\OpenManus"
sys.path.insert(0, OPENMANUS_PATH)
os.environ["DAYTONA_API_KEY"] = "disabled"
os.environ["SANDBOX_ENABLED"] = "false"

# Global
agent = None
logs = []

def add_log(msg):
    timestamp = datetime.now().strftime("%H:%M:%S")
    logs.append(f"[{timestamp}] {msg}")
    if len(logs) > 50:
        logs.pop(0)
    return "\n".join(logs[-20:])

def get_logs():
    return "\n".join(logs[-20:]) if logs else "Ready..."

def check_system():
    status = []
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            status.append("🟢 Ollama: Running")
        else:
            status.append("🔴 Ollama: Not running")
    except:
        status.append("🔴 Ollama: Error")
    
    status.append(f"{'🟢' if agent else '⚪'} Agent: {'Ready' if agent else 'Not loaded'}")
    status.append("💰 Cost: $0/month")
    return "\n".join(status)

def init_agent():
    global agent
    add_log("Initializing agent...")
    try:
        from app.agent.manus import Manus
        agent = Manus()
        add_log("✅ Agent ready!")
        return check_system(), get_logs()
    except Exception as e:
        add_log(f"❌ Error: {e}")
        return check_system(), get_logs()

def run_task(prompt, history):
    global agent
    
    if not prompt.strip():
        return history, "", get_logs()
    
    add_log(f"Task: {prompt[:40]}...")
    
    if history is None:
        history = []
    
    if agent is None:
        init_agent()
    
    if agent is None:
        response = "❌ Agent not initialized. Click 'Initialize Agent' first."
        return history + [[prompt, response]], "", get_logs()
    
    try:
        import asyncio
        
        async def execute():
            return await agent.run(prompt)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(execute())
        loop.close()
        
        response = str(result) if result else "✅ Task completed"
        add_log("✅ Done")
        
    except Exception as e:
        response = f"❌ Error: {str(e)}"
        add_log(f"❌ {e}")
    
    return history + [[prompt, response]], "", get_logs()

def clear_chat():
    return [], "", add_log("Chat cleared")

# UI
with gr.Blocks(title="OpenManus") as app:
    
    gr.Markdown("# 🤖 OpenManus - Local AI Agent")
    gr.Markdown("**Running on:** RTX 4060 + Ryzen 9 7900X | **Model:** Qwen 2.5 7B | **Cost:** $0")
    
    with gr.Row():
        with gr.Column(scale=3):
            chatbot = gr.Chatbot(height=400, label="Tasks")
            
            with gr.Row():
                txt = gr.Textbox(
                    placeholder="Enter a task...",
                    lines=2, 
                    scale=4,
                    show_label=False
                )
                btn = gr.Button("🚀 Run", variant="primary", scale=1)
            
            with gr.Row():
                clear = gr.Button("🗑️ Clear")
                init = gr.Button("🔧 Initialize Agent")
        
        with gr.Column(scale=1):
            gr.Markdown("### Status")
            status = gr.Textbox(value=check_system(), lines=4, show_label=False, interactive=False)
            refresh = gr.Button("🔄 Refresh")
            
            gr.Markdown("### Activity Log")
            log_box = gr.Textbox(value="Ready...", lines=10, show_label=False, interactive=False)
    
    btn.click(run_task, [txt, chatbot], [chatbot, txt, log_box])
    txt.submit(run_task, [txt, chatbot], [chatbot, txt, log_box])
    clear.click(clear_chat, None, [chatbot, txt, log_box])
    init.click(init_agent, None, [status, log_box])
    refresh.click(check_system, None, [status])

if __name__ == "__main__":
    print("=" * 50)
    print("  OpenManus Web UI - http://localhost:7860")
    print("=" * 50)
    app.launch(server_name="127.0.0.1", server_port=7860, inbrowser=True)