"""
agent_stream.py - Real-time event capture from OpenManus agent
Place in: C:\Users\tialc\Documents\GitHub\OpenManus\
"""

import asyncio
import json
from datetime import datetime
from collections import deque
from typing import Optional, Dict, Any, AsyncGenerator
import logging

class AgentEventStream:
    def __init__(self, max_events: int = 500):
        self.events = deque(maxlen=max_events)
        self.subscribers = []
        self.token_count = {"input": 0, "output": 0, "total": 0}
        self.current_step = 0
        self.status = "idle"
        
    def emit(self, event_type: str, content: str, metadata: Optional[Dict] = None):
        """Emit an event to all subscribers."""
        event = {
            "id": len(self.events),
            "type": event_type,
            "timestamp": datetime.now().isoformat(),
            "content": content,
            "metadata": metadata or {},
            "step": self.current_step
        }
        self.events.append(event)
        
        # Notify subscribers
        for queue in self.subscribers:
            queue.put_nowait(event)
        
        return event
    
    def thought(self, content: str):
        """Agent is thinking."""
        return self.emit("thought", content, {"icon": "💭"})
    
    def tool_start(self, tool_name: str, arguments: Dict):
        """Agent started using a tool."""
        return self.emit("tool_start", f"Using: {tool_name}", {
            "icon": "🔧",
            "tool": tool_name,
            "arguments": arguments
        })
    
    def tool_result(self, tool_name: str, result: Any, success: bool = True):
        """Tool returned a result."""
        return self.emit("tool_result", str(result)[:500], {
            "icon": "✅" if success else "❌",
            "tool": tool_name,
            "success": success
        })
    
    def step_start(self, step_num: int, max_steps: int):
        """New step started."""
        self.current_step = step_num
        self.status = "running"
        return self.emit("step", f"Step {step_num}/{max_steps}", {
            "icon": "📍",
            "step": step_num,
            "max_steps": max_steps
        })
    
    def update_tokens(self, input_tokens: int, output_tokens: int):
        """Update token counts."""
        self.token_count["input"] += input_tokens
        self.token_count["output"] += output_tokens
        self.token_count["total"] = self.token_count["input"] + self.token_count["output"]
        return self.emit("tokens", f"Tokens: {self.token_count['total']}", {
            "icon": "📊",
            "tokens": self.token_count.copy()
        })
    
    def complete(self, status: str = "success"):
        """Task completed."""
        self.status = "idle"
        return self.emit("complete", f"Task {status}", {"icon": "🏁", "status": status})
    
    def error(self, message: str):
        """Error occurred."""
        self.status = "error"
        return self.emit("error", message, {"icon": "❌"})
    
    async def subscribe(self) -> AsyncGenerator[Dict, None]:
        """Subscribe to event stream."""
        queue = asyncio.Queue()
        self.subscribers.append(queue)
        try:
            while True:
                event = await queue.get()
                yield event
        finally:
            self.subscribers.remove(queue)
    
    def get_history(self, limit: int = 50) -> list:
        """Get recent events."""
        return list(self.events)[-limit:]
    
    def reset(self):
        """Reset for new task."""
        self.events.clear()
        self.token_count = {"input": 0, "output": 0, "total": 0}
        self.current_step = 0
        self.status = "idle"


# Global instance
event_stream = AgentEventStream()