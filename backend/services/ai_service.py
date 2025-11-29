"""
AI Service - Handles AI/LLM integration for grading and Q&A
Supports OpenAI API and local LLM models
"""
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

from openai import AsyncOpenAI
from core.config import settings


class AIProvider(str, Enum):
    OPENAI = "openai"
    LOCAL = "local"


@dataclass
class AIConfig:
    provider: AIProvider = AIProvider.OPENAI
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 2000
    api_key: Optional[str] = None


class BaseAIProvider(ABC):
    @abstractmethod
    async def generate_response(self, prompt: str, system_prompt: str = "", **kwargs) -> str:
        pass
    
    @abstractmethod
    async def generate_code_feedback(self, code: str, analysis_results: Dict[str, Any]) -> str:
        pass
    
    @abstractmethod
    async def answer_question(self, question: str, context: str = "") -> Dict[str, Any]:
        pass
    
    @abstractmethod
    async def categorize_question(self, question: str) -> str:
        pass


class OpenAIProvider(BaseAIProvider):
    def __init__(self, config: AIConfig):
        self.config = config
        api_key = config.api_key or settings.OPENAI_API_KEY
        base_url = settings.OPENAI_API_BASE
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url) if api_key else None
    
    async def generate_response(self, prompt: str, system_prompt: str = "", **kwargs) -> str:
        if not self.client:
            return "AI service not configured. Set OPENAI_API_KEY."
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            response = await self.client.chat.completions.create(
                model=kwargs.get("model", self.config.model),
                messages=messages,
                temperature=kwargs.get("temperature", self.config.temperature),
                max_tokens=kwargs.get("max_tokens", self.config.max_tokens)
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"AI service error: {str(e)}"
    
    async def generate_code_feedback(self, code: str, analysis_results: Dict[str, Any]) -> str:
        system_prompt = "You are an expert programming instructor. Be encouraging but honest."
        prompt = f"""Analyze this code and provide feedback:
```python
{code}
```
Analysis: Style={analysis_results.get('style_score', 'N/A')}, Complexity={analysis_results.get('complexity', 'N/A')}
Issues: {analysis_results.get('issues', [])}

Provide: 1) What's good 2) Areas to improve 3) Specific suggestions"""
        return await self.generate_response(prompt, system_prompt)
    
    async def answer_question(self, question: str, context: str = "") -> Dict[str, Any]:
        system_prompt = "You are a helpful teaching assistant. Provide clear, educational answers."
        prompt = f"Question: {question}\n{f'Context: {context}' if context else ''}"
        answer = await self.generate_response(prompt, system_prompt)
        confidence = 0.85 if len(answer) > 100 else 0.6
        needs_review = "not sure" in answer.lower() or "might be" in answer.lower()
        return {"answer": answer, "confidence": confidence, "needs_teacher_review": needs_review, "sources": []}
    
    async def categorize_question(self, question: str) -> str:
        prompt = f"""Categorize: {question}
Categories: basic, intermediate, advanced, administrative
Respond with only the category."""
        response = await self.generate_response(prompt, max_tokens=20)
        cat = response.strip().lower()
        return cat if cat in ["basic", "intermediate", "advanced", "administrative"] else "intermediate"


class LocalLLMProvider(BaseAIProvider):
    """Local LLM provider - placeholder for llama-cpp-python or transformers."""
    
    def __init__(self, config: AIConfig):
        self.config = config
        self.model = None
    
    async def generate_response(self, prompt: str, system_prompt: str = "", **kwargs) -> str:
        return "Local LLM not configured. Install llama-cpp-python."
    
    async def generate_code_feedback(self, code: str, analysis_results: Dict[str, Any]) -> str:
        parts = []
        score = analysis_results.get('style_score', 0)
        if score >= 90: parts.append("Excellent code style!")
        elif score >= 70: parts.append("Good style with minor issues.")
        else: parts.append("Style needs improvement.")
        if analysis_results.get('complexity', 0) > 10:
            parts.append("Consider breaking down complex functions.")
        return "\n".join(parts)
    
    async def answer_question(self, question: str, context: str = "") -> Dict[str, Any]:
        q = question.lower()
        responses = {
            "recursion": "Recursion is when a function calls itself with a base case.",
            "loop": "Loops repeat code. Use 'for' for known iterations, 'while' for conditions.",
            "function": "Functions are reusable code blocks defined with 'def'.",
        }
        for kw, resp in responses.items():
            if kw in q:
                return {"answer": resp, "confidence": 0.7, "needs_teacher_review": True, "sources": []}
        return {"answer": "Requires teacher assistance.", "confidence": 0.3, "needs_teacher_review": True, "sources": []}
    
    async def categorize_question(self, question: str) -> str:
        q = question.lower()
        if any(k in q for k in ["deadline", "grade", "submit"]): return "administrative"
        if any(k in q for k in ["optimize", "design", "scale"]): return "advanced"
        if any(k in q for k in ["what is", "define"]): return "basic"
        return "intermediate"


class AIService:
    def __init__(self, config: Optional[AIConfig] = None):
        self.config = config or AIConfig()
        self.provider = OpenAIProvider(self.config) if self.config.provider == AIProvider.OPENAI else LocalLLMProvider(self.config)
    
    async def generate_code_feedback(self, code: str, analysis_results: Dict[str, Any]) -> str:
        return await self.provider.generate_code_feedback(code, analysis_results)
    
    async def answer_question(self, question: str, context: str = "") -> Dict[str, Any]:
        return await self.provider.answer_question(question, context)
    
    async def categorize_question(self, question: str) -> str:
        return await self.provider.categorize_question(question)
    
    async def generate_response(self, prompt: str, system_prompt: str = "") -> str:
        return await self.provider.generate_response(prompt, system_prompt)


ai_service = AIService()

