"""
Niflheim-X Demo Scenarios

This module demonstrates the key capabilities of the niflheim-x framework:
- Agent creation with Gemini API
- Tool integration 
- Memory systems
- Multi-agent orchestration
- Real-time streaming

All examples are production-ready and showcase the framework's lightweight performance.
"""

import asyncio
import logging
import math
import re
from datetime import datetime
from typing import Dict, List, Any
from niflheim_adapters.gemini_adapter import GeminiAgentAdapter

logger = logging.getLogger(__name__)

class DemoScenarios:
    """
    Collection of demo scenarios showcasing niflheim-x capabilities.
    Designed to work with Gemini API for live demonstrations.
    """
    
    def __init__(self, api_key: str):
        """Initialize demo scenarios with Gemini API key."""
        self.api_key = api_key
        self.chat_agent = None
        self.tool_agent = None
        self.memory_agent = None
        self.agents = {}
        self.memory_store = []
        
        # Initialize agents
        self._setup_agents()
        
    def _setup_agents(self):
        """Setup specialized agents for different demo scenarios."""
        try:
            # Chat agent - general conversation
            self.chat_agent = GeminiAgentAdapter(
                api_key=self.api_key,
                temperature=0.7,
                max_output_tokens=1024
            )
            
            # Tool-enabled agent
            self.tool_agent = GeminiAgentAdapter(
                api_key=self.api_key,
                temperature=0.3,  # Lower temperature for accurate calculations
                max_output_tokens=512
            )
            
            # Memory-enabled agent
            self.memory_agent = GeminiAgentAdapter(
                api_key=self.api_key,
                temperature=0.5,
                max_output_tokens=1024
            )
            
            # Multi-agent specialists
            self.agents = {
                'researcher': GeminiAgentAdapter(
                    api_key=self.api_key,
                    temperature=0.4,
                    max_output_tokens=1024
                ),
                'writer': GeminiAgentAdapter(
                    api_key=self.api_key,
                    temperature=0.8,
                    max_output_tokens=1024
                ),
                'reviewer': GeminiAgentAdapter(
                    api_key=self.api_key,
                    temperature=0.3,
                    max_output_tokens=512
                )
            }
            
            logger.info("Demo agents initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to setup agents: {e}")
            raise
    
    async def simple_chat(self, message: str) -> str:
        """
        Simple chat demonstration with context awareness.
        
        Args:
            message: User message
            
        Returns:
            Agent response
        """
        try:
            if not self.chat_agent:
                return "Chat agent not properly initialized. Please check API configuration."
                
            system_prompt = """You are a helpful AI assistant demonstrating the Niflheim-X framework. 
            You are powered by Gemini API and showcase the framework's lightweight, fast performance.
            Be conversational, helpful, and mention that you're running on the niflheim-x framework when appropriate.
            Keep responses concise but informative."""
            
            response = await self.chat_agent.send_message(message, system_prompt)
            return response
            
        except Exception as e:
            logger.error(f"Chat demo error: {e}")
            return f"I apologize, but I'm experiencing some technical difficulties. Error: {str(e)}"
    
    async def tool_integration_demo(self, task: str) -> str:
        """
        Demonstrate tool integration capabilities.
        
        Args:
            task: Task requiring tool usage
            
        Returns:
            Result of tool execution
        """
        try:
            if not self.tool_agent:
                return "Tool agent not properly initialized. Please check API configuration."
                
            # Analyze the task to determine which tool to use
            tool_response = await self._execute_with_tools(task)
            
            system_prompt = """You are demonstrating tool integration in the Niflheim-X framework.
            You have access to various tools like calculators, converters, etc.
            Present the tool results in a clear, user-friendly way."""
            
            # Get agent's interpretation of the tool result
            context = f"The user asked: '{task}'\nTool result: {tool_response}"
            response = await self.tool_agent.send_message(context, system_prompt)
            
            return response
            
        except Exception as e:
            logger.error(f"Tool demo error: {e}")
            return f"Tool execution failed: {str(e)}"
    
    async def _execute_with_tools(self, task: str) -> str:
        """Execute task using appropriate tools."""
        task_lower = task.lower()
        
        # Calculator tool
        if any(word in task_lower for word in ['calculate', 'math', '+', '-', '*', '/', 'square', 'root']):
            return await self._calculator_tool(task)
        
        # Temperature converter
        elif any(word in task_lower for word in ['fahrenheit', 'celsius', 'temperature', 'convert']):
            return await self._temperature_converter_tool(task)
        
        # Date/time tool
        elif any(word in task_lower for word in ['date', 'time', 'day', 'year']):
            return await self._datetime_tool(task)
        
        else:
            return f"Processed task: {task}. No specific tool matched, but niflheim-x can easily add new tools!"
    
    async def _calculator_tool(self, expression: str) -> str:
        """Safe calculator tool."""
        try:
            # Extract mathematical expressions
            math_pattern = r'[\d+\-*/().\s]+'
            
            # Handle specific cases
            if 'square root' in expression.lower():
                numbers = re.findall(r'\d+(?:\.\d+)?', expression)
                if numbers:
                    result = math.sqrt(float(numbers[0]))
                    return f"√{numbers[0]} = {result}"
            
            if '%' in expression:
                # Handle percentage calculations
                parts = expression.replace('%', '/100 *')
                # Simple percentage calculation
                if 'of' in expression.lower():
                    numbers = re.findall(r'\d+(?:\.\d+)?', expression)
                    if len(numbers) >= 2:
                        percent = float(numbers[0])
                        value = float(numbers[1])
                        result = (percent / 100) * value
                        return f"{percent}% of {value} = {result}"
            
            # Extract and evaluate mathematical expression
            matches = re.findall(math_pattern, expression)
            if matches:
                expr = matches[0].strip()
                # Basic safety check
                if re.match(r'^[\d+\-*/().\s]+$', expr):
                    result = eval(expr)
                    return f"{expr} = {result}"
            
            return f"Could not parse mathematical expression from: {expression}"
            
        except Exception as e:
            return f"Calculation error: {str(e)}"
    
    async def _temperature_converter_tool(self, text: str) -> str:
        """Temperature conversion tool."""
        try:
            numbers = re.findall(r'\d+(?:\.\d+)?', text)
            if not numbers:
                return "No temperature value found"
            
            temp = float(numbers[0])
            
            if 'fahrenheit' in text.lower() or 'f' in text.lower():
                celsius = (temp - 32) * 5/9
                return f"{temp}°F = {celsius:.1f}°C"
            elif 'celsius' in text.lower() or 'c' in text.lower():
                fahrenheit = (temp * 9/5) + 32
                return f"{temp}°C = {fahrenheit:.1f}°F"
            
            return f"Temperature conversion completed for {temp} degrees"
            
        except Exception as e:
            return f"Conversion error: {str(e)}"
    
    async def _datetime_tool(self, text: str) -> str:
        """Date and time tool."""
        try:
            now = datetime.now()
            return f"Current date/time: {now.strftime('%Y-%m-%d %H:%M:%S')}"
        except Exception as e:
            return f"DateTime error: {str(e)}"
    
    async def memory_demo(self, message: str) -> str:
        """
        Demonstrate memory systems.
        
        Args:
            message: Message to store or query
            
        Returns:
            Memory response
        """
        try:
            if not self.memory_agent:
                return "Memory agent not properly initialized. Please check API configuration."
                
            # Store information in simple memory
            if any(word in message.lower() for word in ['remember', 'my name is', 'i am', 'i like', 'i love']):
                self.memory_store.append({
                    'content': message,
                    'timestamp': datetime.now().isoformat(),
                    'type': 'user_info'
                })
                
                system_prompt = """You are demonstrating memory capabilities in niflheim-x.
                The user has shared some information that has been stored in memory.
                Acknowledge that you've remembered it and explain how niflheim-x memory works."""
                
                context = f"User shared: '{message}'. This has been stored in memory."
                response = await self.memory_agent.send_message(context, system_prompt)
                
            else:
                # Query memory
                system_prompt = """You are demonstrating memory recall in niflheim-x.
                Look at the stored memories and answer the user's question based on what you remember."""
                
                memory_context = "\n".join([f"Memory {i+1}: {mem['content']}" 
                                          for i, mem in enumerate(self.memory_store)])
                
                context = f"User asks: '{message}'\nStored memories:\n{memory_context}"
                response = await self.memory_agent.send_message(context, system_prompt)
            
            return response
            
        except Exception as e:
            logger.error(f"Memory demo error: {e}")
            return f"Memory operation failed: {str(e)}"
    
    async def multi_agent_demo(self, topic: str) -> str:
        """
        Demonstrate multi-agent orchestration.
        
        Args:
            topic: Topic for agents to collaborate on
            
        Returns:
            Collaborative result
        """
        try:
            # Step 1: Researcher gathers information
            research_prompt = f"""You are a research specialist in a multi-agent system powered by niflheim-x.
            Research and gather key information about: {topic}
            Provide factual, well-structured research findings."""
            
            research_result = await self.agents['researcher'].generate_response(
                f"{research_prompt}\n\nTopic: {topic}"
            )
            
            # Step 2: Writer creates content
            writing_prompt = f"""You are a content writer in a multi-agent system powered by niflheim-x.
            Based on the research provided, create engaging, well-written content about: {topic}
            
            Research findings: {research_result}
            
            Create compelling content that's informative and engaging."""
            
            writing_result = await self.agents['writer'].generate_response(writing_prompt)
            
            # Step 3: Reviewer checks quality
            review_prompt = f"""You are a quality reviewer in a multi-agent system powered by niflheim-x.
            Review the content and provide a final polished version.
            
            Original topic: {topic}
            Content to review: {writing_result}
            
            Provide the final, polished result highlighting the collaborative process."""
            
            final_result = await self.agents['reviewer'].generate_response(review_prompt)
            
            return final_result
            
        except Exception as e:
            logger.error(f"Multi-agent demo error: {e}")
            return f"Multi-agent collaboration failed: {str(e)}"
    
    async def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all demo agents."""
        return {
            'chat_agent': self.chat_agent is not None,
            'tool_agent': self.tool_agent is not None,
            'memory_agent': self.memory_agent is not None,
            'multi_agents': len(self.agents),
            'memory_items': len(self.memory_store),
            'api_configured': bool(self.api_key)
        }
    
    def clear_memory(self):
        """Clear stored memories."""
        self.memory_store.clear()
        if self.memory_agent:
            self.memory_agent.clear_history()
    
    def get_memory_summary(self) -> List[Dict[str, Any]]:
        """Get summary of stored memories."""
        return [
            {
                'id': i,
                'content': mem['content'][:100] + '...' if len(mem['content']) > 100 else mem['content'],
                'timestamp': mem['timestamp'],
                'type': mem['type']
            }
            for i, mem in enumerate(self.memory_store)
        ]