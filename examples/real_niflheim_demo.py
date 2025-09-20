"""
Real Niflheim-X Framework Demo with Gemini Integration

This demonstrates how to use the actual Niflheim-X framework with a custom Gemini adapter,
showing the framework's true capabilities rather than custom demo functions.
"""

import os
import sys
import asyncio
from typing import Dict, Any

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from niflheim_x import Agent, AgentOrchestrator, DictMemory, tool
from niflheim_x.core.types import Message, MessageRole, LLMConfig
from niflheim_adapters.gemini_llm_adapter import GeminiLLMAdapter

# Load environment variables
from dotenv import load_dotenv
load_dotenv()


# Define some tools for the framework
@tool(description="Calculate a mathematical expression safely")
def calculate(expression: str) -> str:
    """Calculate a mathematical expression safely."""
    try:
        # Only allow basic mathematical operations
        allowed_chars = set('0123456789+-*/.() ')
        if not all(c in allowed_chars for c in expression):
            return "Error: Invalid characters in expression"
        
        result = eval(expression)
        return f"Result: {result}"
    except Exception as e:
        return f"Error: {str(e)}"


@tool(description="Get weather information for a location")  
def get_weather(location: str) -> str:
    """Get weather information for a location (mock implementation)."""
    return f"The weather in {location} is sunny with a temperature of 22°C."


@tool(description="Get the current time")
def get_current_time() -> str:
    """Get the current time."""
    from datetime import datetime
    return f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"


class RealNiflheimDemo:
    """Demonstrates the real Niflheim-X framework capabilities."""
    
    def __init__(self, api_key: str):
        """Initialize the demo with Gemini API key."""
        self.api_key = api_key
        self.agents = {}
        self.orchestrator = None
        self._setup_framework()
    
    def _setup_framework(self):
        """Set up the Niflheim-X framework with Gemini adapter."""
        # Create Gemini adapter
        gemini_adapter = GeminiLLMAdapter(
            api_key=self.api_key,
            model="gemini-1.5-flash",
            temperature=0.7,
            max_tokens=2048
        )
        
        # Create specialized agents
        self.agents = {
            "assistant": Agent(
                llm=gemini_adapter,
                name="AI Assistant",
                system_prompt="You are a helpful AI assistant. Be concise and helpful.",
                memory_backend="dict"
            ),
            
            "mathematician": Agent(
                llm=gemini_adapter,
                name="Math Expert",
                system_prompt="You are a mathematics expert. Focus on mathematical problems and calculations.",
                memory_backend="dict"
            ),
            
            "weather_agent": Agent(
                llm=gemini_adapter,
                name="Weather Expert",
                system_prompt="You are a weather information specialist. Provide weather updates and forecasts.",
                memory_backend="dict"
            )
        }
        
        # Register tools with agents
        self.agents["assistant"].register_tool(calculate._niflheim_tool)
        self.agents["assistant"].register_tool(get_weather._niflheim_tool)
        self.agents["assistant"].register_tool(get_current_time._niflheim_tool)
        
        self.agents["mathematician"].register_tool(calculate._niflheim_tool)
        
        self.agents["weather_agent"].register_tool(get_weather._niflheim_tool)
        self.agents["weather_agent"].register_tool(get_current_time._niflheim_tool)
        
        # Create orchestrator for multi-agent scenarios (disabled for now)
        # self.orchestrator = AgentOrchestrator(
        #     agents=list(self.agents.values())
        # )
        self.orchestrator = None
    
    async def simple_chat(self, message: str) -> Dict[str, Any]:
        """Simple chat with the assistant agent."""
        try:
            agent = self.agents["assistant"]
            response = await agent.chat(message)
            
            return {
                "success": True,
                "response": response.content,
                "agent": "assistant",
                "metadata": response.metadata
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "agent": "assistant"
            }
    
    async def math_calculation(self, problem: str) -> Dict[str, Any]:
        """Solve mathematical problems using the math agent."""
        try:
            agent = self.agents["mathematician"]
            response = await agent.chat(f"Solve this problem: {problem}")
            
            return {
                "success": True,
                "response": response.content,
                "agent": "mathematician",
                "metadata": response.metadata
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "agent": "mathematician"
            }
    
    async def weather_query(self, location: str) -> Dict[str, Any]:
        """Get weather information using the weather agent."""
        try:
            agent = self.agents["weather_agent"]
            response = await agent.chat(f"What's the weather like in {location}?")
            
            return {
                "success": True,
                "response": response.content,
                "agent": "weather_agent", 
                "metadata": response.metadata
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "agent": "weather_agent"
            }
    
    async def multi_agent_task(self, task: str) -> Dict[str, Any]:
        """Handle complex tasks using multiple agents via orchestrator."""
        try:
            # Use assistant agent for complex tasks (orchestrator disabled for now)
            agent = self.agents["assistant"]
            response = await agent.chat(f"Help me with this complex task: {task}")
            
            return {
                "success": True,
                "response": response.content,
                "orchestrator": False,
                "note": "Multi-agent orchestration is disabled in this demo version",
                "metadata": response.metadata
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "orchestrator": False
            }
    
    async def memory_demo(self, message: str) -> Dict[str, Any]:
        """Demonstrate memory capabilities."""
        try:
            agent = self.agents["assistant"]
            
            # Process message and store in memory
            response = await agent.chat(message)
            
            # Get conversation history
            history = await agent.memory.get_messages(agent.session_id, limit=10)
            
            return {
                "success": True,
                "response": response.content,
                "memory_entries": len(history),
                "conversation_history": [
                    {"role": msg.role.value, "content": msg.content}
                    for msg in history[-5:]  # Last 5 messages
                ],
                "metadata": response.metadata
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "memory_entries": 0
            }
    
    async def streaming_response(self, message: str):
        """Demonstrate streaming responses."""
        try:
            agent = self.agents["assistant"]
            
            # Use chat_stream method
            async for token in agent.chat_stream(message):
                yield {
                    "success": True,
                    "chunk": token.content,
                    "is_tool_call": token.is_tool_call,
                    "finish_reason": token.finish_reason
                }
                
        except Exception as e:
            yield {
                "success": False,
                "error": str(e),
                "chunk": ""
            }
    
    def get_framework_info(self) -> Dict[str, Any]:
        """Get information about the current framework setup."""
        return {
            "framework": "Niflheim-X",
            "version": "0.1.0",
            "llm_provider": "Gemini",
            "agents": list(self.agents.keys()),
            "tools_available": ["calculate", "get_weather", "get_current_time"],
            "memory_backend": "DictMemory",
            "orchestrator_enabled": self.orchestrator is not None
        }


# Global demo instance
_demo_instance = None


def get_demo_instance():
    """Get or create the demo instance."""
    global _demo_instance
    if _demo_instance is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        _demo_instance = RealNiflheimDemo(api_key)
    return _demo_instance


# Async wrapper functions for Flask integration
async def demo_simple_chat(message: str) -> Dict[str, Any]:
    """Simple chat demo."""
    demo = get_demo_instance()
    return await demo.simple_chat(message)


async def demo_math_calculation(problem: str) -> Dict[str, Any]:
    """Math calculation demo."""
    demo = get_demo_instance()
    return await demo.math_calculation(problem)


async def demo_weather_query(location: str) -> Dict[str, Any]:
    """Weather query demo."""
    demo = get_demo_instance()
    return await demo.weather_query(location)


async def demo_multi_agent_task(task: str) -> Dict[str, Any]:
    """Multi-agent task demo."""
    demo = get_demo_instance()
    return await demo.multi_agent_task(task)


async def demo_memory_demo(message: str) -> Dict[str, Any]:
    """Memory demo."""
    demo = get_demo_instance()
    return await demo.memory_demo(message)


async def demo_streaming_response(message: str):
    """Streaming response demo."""
    demo = get_demo_instance()
    async for chunk in demo.streaming_response(message):
        yield chunk


def demo_framework_info() -> Dict[str, Any]:
    """Get framework information."""
    demo = get_demo_instance()
    return demo.get_framework_info()


if __name__ == "__main__":
    # Test the real framework
    async def test_framework():
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("Please set GEMINI_API_KEY environment variable")
            return
        
        demo = RealNiflheimDemo(api_key)
        
        print("=== Niflheim-X Framework Demo ===")
        print(f"Framework info: {demo.get_framework_info()}")
        
        # Test simple chat
        print("\n=== Simple Chat ===")
        result = await demo.simple_chat("Hello! What can you do?")
        print(f"Response: {result}")
        
        # Test math calculation
        print("\n=== Math Calculation ===") 
        result = await demo.math_calculation("What is 15 * 23 + 45?")
        print(f"Math result: {result}")
        
        # Test memory
        print("\n=== Memory Demo ===")
        result = await demo.memory_demo("Remember that my name is John and I like pizza.")
        print(f"Memory result: {result}")
        
        result = await demo.memory_demo("What do you remember about me?")
        print(f"Memory recall: {result}")
    
    # Run the test
    asyncio.run(test_framework())