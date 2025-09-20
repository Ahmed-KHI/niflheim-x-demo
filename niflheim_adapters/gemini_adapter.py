"""
Gemini API Adapter for Niflheim-X Framework
A lightweight adapter that integrates Google's Gemini API with the niflheim-x framework.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, AsyncGenerator, List
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# Set up logging
logger = logging.getLogger(__name__)

class GeminiAdapter:
    """
    Lightweight Gemini API adapter for niflheim-x framework.
    Provides a simple interface to Google's Gemini models.
    """
    
    def __init__(
        self, 
        api_key: str, 
        model_name: str = "gemini-1.5-flash",
        temperature: float = 0.7,
        max_output_tokens: int = 2048,
        **kwargs
    ):
        """
        Initialize the Gemini adapter.
        
        Args:
            api_key: Google API key for Gemini
            model_name: Model to use (default: gemini-1.5-flash)
            temperature: Sampling temperature
            max_output_tokens: Maximum tokens in response
        """
        self.api_key = api_key
        self.model_name = model_name
        self.temperature = temperature
        self.max_output_tokens = max_output_tokens
        
        # Configure the API
        genai.configure(api_key=api_key)
        
        # Initialize the model
        self.model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_output_tokens,
                **kwargs
            ),
            safety_settings={
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            }
        )
        
        logger.info(f"Gemini adapter initialized with model: {model_name}")
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate a response from the Gemini model.
        
        Args:
            prompt: Input prompt for the model
            **kwargs: Additional generation parameters
            
        Returns:
            Generated text response
        """
        try:
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, 
                self._sync_generate, 
                prompt
            )
            return response
            
        except Exception as e:
            logger.error(f"Generation error: {e}")
            raise
    
    def _sync_generate(self, prompt: str) -> str:
        """Synchronous generation method."""
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Sync generation error: {e}")
            raise
    
    async def generate_stream(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        """
        Generate a streaming response from the Gemini model.
        
        Args:
            prompt: Input prompt for the model
            **kwargs: Additional generation parameters
            
        Yields:
            Chunks of generated text
        """
        try:
            loop = asyncio.get_event_loop()
            
            # Create streaming response
            def _create_stream():
                return self.model.generate_content(prompt, stream=True)
            
            response = await loop.run_in_executor(None, _create_stream)
            
            # Yield chunks as they arrive
            for chunk in response:
                if chunk.text:
                    yield chunk.text
                    
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield f"Error: {str(e)}"
    
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Chat interface for conversational interactions.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            **kwargs: Additional generation parameters
            
        Returns:
            Generated response
        """
        try:
            # Convert messages to a single prompt for Gemini
            prompt = self._messages_to_prompt(messages)
            return await self.generate(prompt, **kwargs)
            
        except Exception as e:
            logger.error(f"Chat error: {e}")
            raise
    
    def _messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Convert message list to a single prompt string."""
        prompt_parts = []
        
        for message in messages:
            role = message.get('role', 'user')
            content = message.get('content', '')
            
            if role == 'system':
                prompt_parts.append(f"System: {content}")
            elif role == 'user':
                prompt_parts.append(f"Human: {content}")
            elif role == 'assistant':
                prompt_parts.append(f"Assistant: {content}")
        
        return "\n\n".join(prompt_parts) + "\n\nAssistant:"
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current model.
        
        Returns:
            Dictionary with model information
        """
        return {
            'model_name': self.model_name,
            'temperature': self.temperature,
            'max_output_tokens': self.max_output_tokens,
            'provider': 'Google Gemini',
            'adapter_version': '1.0.0'
        }
    
    async def test_connection(self) -> bool:
        """
        Test the connection to the Gemini API.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            test_response = await self.generate("Hello! Please respond with 'Connection successful.'")
            return "successful" in test_response.lower()
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False

class GeminiAgentAdapter:
    """
    Enhanced adapter that integrates directly with niflheim-x Agent class.
    This provides the interface expected by the niflheim-x framework.
    """
    
    def __init__(self, api_key: str, **kwargs):
        """Initialize the agent adapter."""
        self.gemini = GeminiAdapter(api_key, **kwargs)
        self.conversation_history = []
    
    async def send_message(self, message: str, system_prompt: Optional[str] = None) -> str:
        """
        Send a message and get a response.
        This method provides the interface expected by niflheim-x agents.
        """
        # Build conversation context
        messages = []
        
        if system_prompt:
            messages.append({'role': 'system', 'content': system_prompt})
        
        # Add conversation history
        messages.extend(self.conversation_history)
        
        # Add current message
        messages.append({'role': 'user', 'content': message})
        
        # Get response
        response = await self.gemini.chat(messages)
        
        # Update conversation history
        self.conversation_history.append({'role': 'user', 'content': message})
        self.conversation_history.append({'role': 'assistant', 'content': response})
        
        # Keep history manageable (last 10 exchanges)
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]
        
        return response
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []
    
    async def generate_response(self, prompt: str) -> str:
        """Simple generation method for tool integrations."""
        return await self.gemini.generate(prompt)