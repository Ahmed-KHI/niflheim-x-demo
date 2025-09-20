"""
Gemini LLM Adapter for Niflheim_x Framework

This adapter integrates Google's Gemini API with the Niflheim_x framework,
following the framework's LLMAdapter interface.
"""

import asyncio
import json
from typing import AsyncIterator, Dict, List, Optional

import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

from niflheim_x.llms.base import LLMAdapter
from niflheim_x.core.types import Message, AgentResponse, LLMConfig, StreamingToken, MessageRole


class GeminiLLMAdapter(LLMAdapter):
    """Gemini LLM adapter that integrates with Niflheim_x framework."""
    
    def __init__(
        self,
        api_key: str,
        model: str = "gemini-1.5-flash",
        **config_kwargs
    ):
        """Initialize the Gemini adapter.
        
        Args:
            api_key: Google Gemini API key
            model: Model name to use
            **config_kwargs: Additional configuration options
        """
        # Create LLM configuration
        config = LLMConfig(
            model=model,
            **config_kwargs
        )
        super().__init__(config)
        
        # Store API key separately
        self.api_key = api_key
        
        # Configure Gemini API
        genai.configure(api_key=api_key)
        
        # Initialize the model
        self.model = genai.GenerativeModel(
            model_name=self.config.model,
            generation_config=genai.GenerationConfig(
                temperature=self.config.temperature,
                max_output_tokens=self.config.max_tokens or 2048,
            ),
            safety_settings={
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            }
        )
    
    def _convert_messages_to_gemini_format(self, messages: List[Message]) -> List[Dict]:
        """Convert Niflheim_x messages to Gemini format."""
        gemini_messages = []
        
        for msg in messages:
            if msg.role == MessageRole.SYSTEM:
                # Gemini doesn't have system role, prepend to first user message
                continue
            elif msg.role == MessageRole.USER:
                gemini_messages.append({
                    "role": "user",
                    "parts": [{"text": msg.content}]
                })
            elif msg.role == MessageRole.ASSISTANT:
                gemini_messages.append({
                    "role": "model",
                    "parts": [{"text": msg.content}]
                })
        
        return gemini_messages
    
    def _get_system_instruction(self, messages: List[Message]) -> Optional[str]:
        """Extract system instruction from messages."""
        for msg in messages:
            if msg.role == MessageRole.SYSTEM:
                return msg.content
        return None
    
    async def generate_response(
        self,
        messages: List[Message],
        tools: Optional[List[Dict]] = None,
        stream: bool = False,
    ) -> AgentResponse:
        """Generate a response from Gemini.
        
        Args:
            messages: List of conversation messages
            tools: Available tools for the LLM to call (not implemented yet)
            stream: Whether to stream the response
            
        Returns:
            Response from Gemini
        """
        try:
            # Get system instruction
            system_instruction = self._get_system_instruction(messages)
            
            # Convert messages to Gemini format
            gemini_messages = self._convert_messages_to_gemini_format(messages)
            
            # Create chat session
            chat = self.model.start_chat(history=gemini_messages[:-1] if len(gemini_messages) > 1 else [])
            
            # Get the latest user message
            latest_message = gemini_messages[-1]["parts"][0]["text"] if gemini_messages else ""
            
            # Add system instruction to the message if present
            if system_instruction:
                latest_message = f"System: {system_instruction}\n\nUser: {latest_message}"
            
            if stream:
                # For streaming, we need to collect all chunks first
                response_text = ""
                async for chunk in self.stream_response(messages, tools):
                    response_text += chunk.content
                
                return AgentResponse(
                    content=response_text,
                    metadata={
                        "model": self.config.model,
                        "provider": "gemini",
                        "stream": True
                    }
                )
            else:
                # Non-streaming response
                response = await asyncio.to_thread(chat.send_message, latest_message)
                
                return AgentResponse(
                    content=response.text,
                    metadata={
                        "model": self.config.model,
                        "provider": "gemini",
                        "stream": False
                    }
                )
                
        except Exception as e:
            return AgentResponse(
                content=f"Error generating response: {str(e)}",
                metadata={
                    "error": True,
                    "error_type": type(e).__name__,
                    "model": self.config.model,
                    "provider": "gemini"
                }
            )
    
    async def stream_response(
        self,
        messages: List[Message],
        tools: Optional[List[Dict]] = None,
    ) -> AsyncIterator[StreamingToken]:
        """Stream tokens from Gemini response.
        
        Args:
            messages: List of conversation messages
            tools: Available tools for the LLM to call
            
        Yields:
            Individual tokens from the response
        """
        try:
            # Get system instruction
            system_instruction = self._get_system_instruction(messages)
            
            # Convert messages to Gemini format
            gemini_messages = self._convert_messages_to_gemini_format(messages)
            
            # Create chat session
            chat = self.model.start_chat(history=gemini_messages[:-1] if len(gemini_messages) > 1 else [])
            
            # Get the latest user message
            latest_message = gemini_messages[-1]["parts"][0]["text"] if gemini_messages else ""
            
            # Add system instruction to the message if present
            if system_instruction:
                latest_message = f"System: {system_instruction}\n\nUser: {latest_message}"
            
            # Generate streaming response
            response = await asyncio.to_thread(
                lambda: chat.send_message(latest_message, stream=True)
            )
            
            for chunk in response:
                if chunk.text:
                    yield StreamingToken(
                        content=chunk.text,
                        is_tool_call=False,
                        finish_reason=None
                    )
                    
        except Exception as e:
            yield StreamingToken(
                content=f"Error streaming response: {str(e)}",
                is_tool_call=False,
                finish_reason="error"
            )
    
    async def validate_connection(self) -> bool:
        """Validate that the Gemini connection is working."""
        try:
            test_messages = [Message(role=MessageRole.USER, content="Hello")]
            response = await self.generate_response(test_messages)
            return not response.metadata.get("error", False)
        except Exception:
            return False
    
    def get_model_info(self) -> Dict[str, str]:
        """Get information about the current Gemini model."""
        return {
            "model": self.config.model,
            "provider": "gemini",
            "api_version": "v1",
            "features": "text_generation,streaming,conversation"
        }


# Factory function for easy adapter creation
def create_gemini_adapter(api_key: str, model: str = "gemini-1.5-flash", **kwargs) -> GeminiLLMAdapter:
    """Create a Gemini LLM adapter with the given configuration.
    
    Args:
        api_key: Google Gemini API key
        model: Model name to use
        **kwargs: Additional configuration options
        
    Returns:
        Configured GeminiLLMAdapter instance
    """
    return GeminiLLMAdapter(
        api_key=api_key,
        model=model,
        **kwargs
    )