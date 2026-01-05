import asyncio
import json
import os
import sys
import subprocess
import logging
import re
from pathlib import Path
from queue import Queue
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
import uvicorn

SCRIPT_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(SCRIPT_DIR))

os.environ["DAYTONA_API_KEY"] = "disabled"
os.environ["SANDBOX_ENABLED"] = "false"

app = FastAPI()
agent = None
event_queue = Queue()

class StreamHandler(logging.Handler):
    def emit(self, record):
        try:
            msg = self.format(record)
            
            # Step execution
            if "Executing step" in msg:
                match = re.search(r'step (\d+)/(\d+)', msg)
                if match:
                    event_queue.put({
                        "type": "step",
                        "icon": "📍",
                        "content": f"Step {match.group(1)}/{match.group(2)}"
                    })
            
            # Manus thoughts
            elif "Manus's thoughts" in msg:
                thought = msg.split("thoughts:")[-1].strip() if "thoughts:" in msg else ""
                # Get the next line which contains actual thought
                if thought:
                    event_queue.put({
                        "type": "thought",
                        "icon": "💭",
                        "content": thought[:500] if thought else "Thinking..."
                    })
            
            # Tools selected
            elif "selected" in msg and "tools to use" in msg:
                match = re.search(r'selected (\d+) tools', msg)
                count = match.group(1) if match else "?"
                event_queue.put({
                    "type": "tool",
                    "icon": "🛠️",
                    "content": f"Selected {count} tool(s)"
                })
            
            # Tools being prepared
            elif "Tools being prepared" in msg:
                tools = msg.split("prepared:")[-1].strip() if "prepared:" in msg else msg
                event_queue.put({
                    "type": "tool",
                    "icon": "🧰",
                    "content": f"Tools: {tools}"
                })
            
            # Tool arguments
            elif "Tool arguments" in msg:
                args = msg.split("arguments:")[-1].strip() if "arguments:" in msg else msg
                event_queue.put({
                    "type": "args",
                    "icon": "🔧",
                    "content": args[:300]
                })
            
            # Activating tool
            elif "Activating tool" in msg:
                tool_name = re.search(r"'(\w+)'", msg)
                if tool_name:
                    event_queue.put({
                        "type": "tool",
                        "icon": "⚡",
                        "content": f"Running: {tool_name.group(1)}"
                    })
            
            # Tool completed
            elif "completed its mission" in msg:
                result = msg.split("Result:")[-1].strip()[:200] if "Result:" in msg else "Done"
                event_queue.put({
                    "type": "result",
                    "icon": "✅",
                    "content": result
                })
            
            # Token usage
            elif "Token usage" in msg:
                match = re.search(r'Total=(\d+)', msg)
                if match:
                    tokens = int(match.group(1))
                    event_queue.put({
                        "type": "tokens",
                        "icon": "📊",
                        "content": f"Tokens: {tokens}",
                        "tokens": tokens
                    })
            
            # Errors
            elif "ERROR" in msg or "Error" in msg:
                event_queue.put({
                    "type": "error",
                    "icon": "❌",
                    "content": msg[:300]
                })
                
        except Exception as e:
            pass

# Create and attach handler
handler = StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(message)s')
handler.setFormatter(formatter)

# Attach to all relevant loggers
loggers_to_monitor = [
    "app.agent.toolcall",
    "app.agent.base",
    "app.llm",
    "app.tool",
    "root",
    ""
]

for logger_name in loggers_to_monitor:
    logger = logging.getLogger(logger_name)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

# Also capture root logger
logging.root.addHandler(handler)
logging.root.setLevel(logging.DEBUG)

def get_agent():
    global agent
    if agent is None:
        from app.agent.manus import Manus
        agent = Manus()
    return agent

@app.get("/", response_class=HTMLResponse)
async def index():
    html_path = SCRIPT_DIR / "ui.html"
    if html_path.exists():
        return html_path.read_text(encoding="utf-8")
    return "<h1>ui.html not found</h1>"

@app.get("/api/status")
async def status():
    ollama_ok = False
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, timeout=5)
        ollama_ok = result.returncode == 0
    except:
        pass
    return {"ollama": ollama_ok, "agent": agent is not None}

@app.post("/api/run")
async def run_task(request: Request):
    data = await request.json()
    prompt = data.get("prompt", "")
    
    # Clear queue
    while not event_queue.empty():
        event_queue.get()
    
    async def event_stream():
        yield json.dumps({"type": "start", "icon": "🚀", "content": "Starting task..."}) + "\n"
        
        task_done = asyncio.Event()
        result_holder = {"result": None, "error": None}
        
        async def run_agent():
            try:
                manus = get_agent()
                result_holder["result"] = await manus.run(prompt)
            except Exception as e:
                result_holder["error"] = str(e)
            finally:
                task_done.set()
        
        asyncio.create_task(run_agent())
        
        # Stream events while agent runs
        while not task_done.is_set():
            while not event_queue.empty():
                event = event_queue.get()
                yield json.dumps(event) + "\n"
            await asyncio.sleep(0.05)  # Faster polling
        
        # Get remaining events
        await asyncio.sleep(0.1)
        while not event_queue.empty():
            event = event_queue.get()
            yield json.dumps(event) + "\n"
        
        # Final result
        if result_holder["error"]:
            yield json.dumps({"type": "error", "icon": "❌", "content": result_holder["error"]}) + "\n"
        else:
            result_text = str(result_holder["result"]) if result_holder["result"] else "Task completed"
            yield json.dumps({"type": "complete", "icon": "🏁", "content": "Done", "result": result_text}) + "\n"
    
    return StreamingResponse(event_stream(), media_type="text/plain")

if __name__ == "__main__":
    print("=" * 60)
    print("  OpenManus AI - http://localhost:8000")
    print("=" * 60)
    uvicorn.run(app, host="127.0.0.1", port=8000)