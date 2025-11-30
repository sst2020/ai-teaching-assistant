"""
AI Service - Handles AI/LLM integration for grading and Q&A
Supports OpenAI API and local LLM models
"""
import time
import logging
from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

from openai import AsyncOpenAI
from core.config import settings

logger = logging.getLogger(__name__)


class AIProvider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
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
    """Enhanced AI Service with extended functionality."""

    def __init__(self, config: Optional[AIConfig] = None):
        self.config = config or AIConfig()
        self.provider = OpenAIProvider(self.config) if self.config.provider == AIProvider.OPENAI else LocalLLMProvider(self.config)
        self._interaction_history: List[Dict[str, Any]] = []

    async def generate_code_feedback(self, code: str, analysis_results: Dict[str, Any]) -> str:
        return await self.provider.generate_code_feedback(code, analysis_results)

    async def answer_question(self, question: str, context: str = "") -> Dict[str, Any]:
        return await self.provider.answer_question(question, context)

    async def categorize_question(self, question: str) -> str:
        return await self.provider.categorize_question(question)

    async def generate_response(self, prompt: str, system_prompt: str = "") -> str:
        return await self.provider.generate_response(prompt, system_prompt)

    async def explain_code(
        self,
        code: str,
        language: str = "python",
        detail_level: str = "medium",
        student_level: str = "intermediate"
    ) -> Dict[str, Any]:
        """
        Explain code to a student at their level.

        Args:
            code: The code to explain
            language: Programming language
            detail_level: basic, medium, or detailed
            student_level: beginner, intermediate, or advanced

        Returns:
            Dictionary with explanation, key concepts, and resources
        """
        start_time = time.time()

        system_prompt = f"""You are an expert programming tutor explaining {language} code.
Adjust your explanation for a {student_level} level student.
Provide a {detail_level} level of detail."""

        prompt = f"""Explain this {language} code:

```{language}
{code}
```

Provide:
1. A clear explanation of what the code does
2. Key concepts used in the code
3. Any complexity notes (time/space complexity if relevant)
4. Suggested learning resources or topics to explore"""

        response = await self.generate_response(prompt, system_prompt)
        latency_ms = (time.time() - start_time) * 1000

        # Log interaction
        self._log_interaction("explain_code", prompt, response, latency_ms)

        return {
            "success": True,
            "explanation": response,
            "key_concepts": self._extract_concepts(response),
            "complexity_notes": None,
            "learning_resources": [],
            "latency_ms": latency_ms
        }

    async def suggest_improvements(
        self,
        code: str,
        language: str = "python",
        focus_areas: List[str] = None,
        max_suggestions: int = 5,
        include_refactored_code: bool = True
    ) -> Dict[str, Any]:
        """
        Suggest improvements for code.

        Args:
            code: The code to improve
            language: Programming language
            focus_areas: Specific areas to focus on
            max_suggestions: Maximum number of suggestions
            include_refactored_code: Whether to include refactored code

        Returns:
            Dictionary with suggestions and optionally refactored code
        """
        start_time = time.time()

        focus_str = ", ".join(focus_areas) if focus_areas else "general improvements"

        system_prompt = f"""You are an expert code reviewer for {language}.
Focus on: {focus_str}
Provide actionable, specific suggestions."""

        prompt = f"""Review this {language} code and suggest up to {max_suggestions} improvements:

```{language}
{code}
```

For each suggestion:
1. Describe the issue
2. Explain why it matters
3. Show how to fix it
{"4. Provide a refactored version of the code" if include_refactored_code else ""}"""

        response = await self.generate_response(prompt, system_prompt)
        latency_ms = (time.time() - start_time) * 1000

        self._log_interaction("suggest_improvements", prompt, response, latency_ms)

        return {
            "success": True,
            "suggestions": self._parse_suggestions(response),
            "refactored_code": self._extract_code_block(response) if include_refactored_code else None,
            "improvement_summary": response[:500] if len(response) > 500 else response,
            "latency_ms": latency_ms
        }

    async def answer_student_question(
        self,
        question: str,
        code: Optional[str] = None,
        language: str = "python",
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Answer a student's question about code or programming.

        Args:
            question: The student's question
            code: Optional related code
            language: Programming language
            context: Additional context

        Returns:
            Dictionary with answer, related concepts, and follow-up questions
        """
        start_time = time.time()

        system_prompt = """You are a helpful teaching assistant.
Provide clear, educational answers that help students learn.
Include examples when helpful."""

        prompt = f"Question: {question}\n"
        if code:
            prompt += f"\nRelated code:\n```{language}\n{code}\n```\n"
        if context:
            prompt += f"\nContext: {context}\n"

        prompt += "\nProvide a clear answer and suggest related concepts to explore."

        response = await self.generate_response(prompt, system_prompt)
        latency_ms = (time.time() - start_time) * 1000

        self._log_interaction("answer_question", prompt, response, latency_ms)

        return {
            "success": True,
            "answer": response,
            "related_concepts": self._extract_concepts(response),
            "code_examples": [],
            "follow_up_questions": self._generate_follow_ups(question),
            "latency_ms": latency_ms
        }

    def _log_interaction(
        self,
        interaction_type: str,
        prompt: str,
        response: str,
        latency_ms: float
    ):
        """Log an AI interaction for history tracking."""
        self._interaction_history.append({
            "type": interaction_type,
            "prompt_length": len(prompt),
            "response_length": len(response),
            "latency_ms": latency_ms,
            "timestamp": time.time()
        })
        # Keep only last 100 interactions in memory
        if len(self._interaction_history) > 100:
            self._interaction_history = self._interaction_history[-100:]

    def _extract_concepts(self, text: str) -> List[str]:
        """Extract key concepts from AI response."""
        concepts = []
        keywords = ["concept", "principle", "pattern", "technique", "method"]
        lines = text.split("\n")
        for line in lines:
            line_lower = line.lower()
            if any(kw in line_lower for kw in keywords):
                # Clean up the line
                clean = line.strip("- *#").strip()
                if len(clean) > 5 and len(clean) < 100:
                    concepts.append(clean)
        return concepts[:5]

    def _parse_suggestions(self, text: str) -> List[Dict[str, str]]:
        """Parse suggestions from AI response."""
        suggestions = []
        lines = text.split("\n")
        current_suggestion = None

        for line in lines:
            if line.strip().startswith(("1.", "2.", "3.", "4.", "5.", "-", "*")):
                if current_suggestion:
                    suggestions.append(current_suggestion)
                current_suggestion = {
                    "title": line.strip("0123456789.-* ").strip(),
                    "description": ""
                }
            elif current_suggestion:
                current_suggestion["description"] += line + " "

        if current_suggestion:
            suggestions.append(current_suggestion)

        return suggestions[:5]

    def _extract_code_block(self, text: str) -> Optional[str]:
        """Extract code block from AI response."""
        import re
        pattern = r"```[\w]*\n(.*?)```"
        matches = re.findall(pattern, text, re.DOTALL)
        return matches[-1].strip() if matches else None

    def _generate_follow_ups(self, question: str) -> List[str]:
        """Generate follow-up questions based on the original question."""
        q_lower = question.lower()
        follow_ups = []

        if "how" in q_lower:
            follow_ups.append("What are the alternatives to this approach?")
        if "why" in q_lower:
            follow_ups.append("What would happen if we did it differently?")
        if "error" in q_lower or "bug" in q_lower:
            follow_ups.append("How can I prevent this issue in the future?")
        if "function" in q_lower or "method" in q_lower:
            follow_ups.append("How can I test this function effectively?")

        if not follow_ups:
            follow_ups = ["Can you explain this in more detail?"]

        return follow_ups[:3]

    def get_interaction_stats(self) -> Dict[str, Any]:
        """Get statistics about AI interactions."""
        if not self._interaction_history:
            return {"total_interactions": 0}

        total = len(self._interaction_history)
        avg_latency = sum(i["latency_ms"] for i in self._interaction_history) / total

        by_type = {}
        for interaction in self._interaction_history:
            t = interaction["type"]
            by_type[t] = by_type.get(t, 0) + 1

        return {
            "total_interactions": total,
            "average_latency_ms": avg_latency,
            "by_type": by_type
        }


ai_service = AIService()

