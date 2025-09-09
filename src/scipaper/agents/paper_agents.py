"""AI agents for paper analysis and processing."""

import os
from typing import Any

from loguru import logger

from ..config import is_ollama_available, is_openai_available, settings
from ..exceptions import AgentError, NetworkError, RateLimitError

# Optional dependency for Ollama HTTP client
try:
    import httpx  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    httpx = None  # type: ignore[assignment]

# Check for OpenAI Agents SDK availability
try:
    from openai import AsyncOpenAI
    AGENTS_AVAILABLE = True
except ImportError:
    AGENTS_AVAILABLE = False
    logger.warning("OpenAI package not available. Install with: pip install openai")


class PaperAgent:
    """AI agent for paper analysis using OpenAI or Ollama fallback."""

    MIN_ANALYSIS_LEN = 50

    def __init__(self):
        self.openai_available = is_openai_available()
        self.ollama_available = is_ollama_available()

        if not self.openai_available and not self.ollama_available:
            logger.warning(
                "Neither OpenAI nor Ollama is configured. "
                "Agent functionality will be limited."
            )

    def _validate_analysis(self, analysis: str, analysis_type: str) -> bool:
        """Validate the generated analysis for quality."""
        if not analysis:
            return False
        if len(analysis) < self.MIN_ANALYSIS_LEN:
            return False
        # Check for relevant keywords based on analysis_type
        keywords = {
            "summary": ["summary", "overview", "key points"],
            "comprehensive_analysis": ["analysis", "insights", "detailed", "comparison"],
            "advanced_summary": ["advanced summary", "in-depth", "refined", "comprehensive review"]
        }
        relevant_keywords = keywords.get(analysis_type, [])
        return any(keyword in analysis.lower() for keyword in relevant_keywords)

    async def advanced_summarization(
        self, papers: list[dict[str, Any]], refinement_level: int = 3
    ) -> str:
        """Advanced paper summarization with recursive refinement."""
        logger_ctx = logger.bind(papers_count=len(papers), refinement_level=refinement_level)
        if not papers:
            raise AgentError("No papers provided for summarization")

        initial_analysis = await self.analyze_papers(papers, "comprehensive_analysis")
        analysis = initial_analysis

        for level in range(1, refinement_level + 1):
            logger_ctx.info(f"Refinement level {level}/{refinement_level}")
            if self._validate_analysis(analysis, "advanced_summary"):
                logger_ctx.info(f"Refinement successful at level {level}")
                break
            # Recursive refinement
            feedback = "Refine the analysis to be more comprehensive and detailed."
            refined_prompt = (
                "Refine this analysis with more depth: "
                f"{analysis}\nFeedback: {feedback}"
            )
            if self.openai_available:
                analysis = await self._analyze_with_openai(
                    papers, "advanced_summary", refined_prompt=refined_prompt
                )
            elif self.ollama_available:
                analysis = await self._analyze_with_ollama(
                    papers, "advanced_summary", refined_prompt=refined_prompt
                )
            else:
                logger_ctx.warning("No AI backend available for refinement")
                break

        logger_ctx.info("Advanced summarization completed")
        return analysis

    async def analyze_papers(
        self, papers: list[dict[str, Any]], analysis_type: str = "summary"
    ) -> str:
        """Analyze a list of papers using AI."""
        logger_ctx = logger.bind(papers_count=len(papers), analysis_type=analysis_type)
        try:
            if self.openai_available:
                return await self._analyze_with_openai(papers, analysis_type)
            elif self.ollama_available:
                return await self._analyze_with_ollama(papers, analysis_type)
            else:
                return "Analysis unavailable: No AI backend configured"
        except AgentError:
            raise
        except Exception as e:
            logger_ctx.error(f"Paper analysis failed: {e}")
            raise AgentError(
                f"Paper analysis failed: {e}",
                details={"papers_count": len(papers), "type": analysis_type},
            ) from e

    async def _analyze_with_openai(
        self,
        papers: list[dict[str, Any]],
        analysis_type: str,
        refined_prompt: str | None = None,
    ) -> str:
        """Analyze papers using OpenAI API."""
        logger_ctx = logger.bind(backend="openai", papers_count=len(papers))
        try:
            client = AsyncOpenAI(api_key=settings.openai_api_key)

            # Create analysis prompt
            papers_text = "\n".join(
                [
                    (
                        "- "
                        f"{p.get('title', 'Unknown')} by "
                        f"{', '.join(p.get('authors', ['Unknown']))} "
                        f"({p.get('date', 'Unknown')})"
                    )
                    for p in papers
                ]
            )

            prompt = refined_prompt or (
                "Analyze the following papers and provide a "
                f"{analysis_type}:\n\n{papers_text}\n\nAnalysis:"
            )

            response = await client.chat.completions.create(
                model=settings.openai_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=settings.openai_temperature,
            )

            analysis = response.choices[0].message.content or "No analysis generated"
            if not self._validate_analysis(analysis, analysis_type):
                logger_ctx.warning("Analysis validation failed, retrying...")
                # Recursive retry for validation
                return await self._analyze_with_openai(papers, analysis_type)
            logger_ctx.info("OpenAI analysis completed successfully")
            return analysis

        except RateLimitError as e:
            logger_ctx.error(f"OpenAI rate limit exceeded: {e}")
            raise
        except NetworkError as e:
            logger_ctx.error(f"OpenAI network error: {e}")
            raise
        except Exception as e:
            logger_ctx.error(f"OpenAI analysis failed: {e}")
            raise AgentError(
                f"OpenAI analysis failed: {e}", details={"prompt_length": len(prompt)}
            ) from e

    async def _analyze_with_ollama(
        self,
        papers: list[dict[str, Any]],
        analysis_type: str,
        refined_prompt: str | None = None,
    ) -> str:
        """Analyze papers using Ollama."""
        logger_ctx = logger.bind(backend="ollama", papers_count=len(papers))
        try:
            ollama = OllamaModel()

            papers_text = "\n".join(
                [
                    (
                        "- "
                        f"{p.get('title', 'Unknown')} by "
                        f"{', '.join(p.get('authors', ['Unknown']))} "
                        f"({p.get('date', 'Unknown')})"
                    )
                    for p in papers
                ]
            )

            prompt = refined_prompt or (
                "Analyze the following papers and provide a "
                f"{analysis_type}:\n\n{papers_text}\n\nAnalysis:"
            )

            analysis = await ollama.generate(prompt, context="paper_analysis")
            if not self._validate_analysis(analysis, analysis_type):
                logger_ctx.warning("Analysis validation failed, retrying...")
                # Recursive retry for validation
                return await self._analyze_with_ollama(papers, analysis_type)
            logger_ctx.info("Ollama analysis completed successfully")
            return analysis

        except RateLimitError as e:
            logger_ctx.error(f"Ollama rate limit exceeded: {e}")
            raise
        except NetworkError as e:
            logger_ctx.error(f"Ollama network error: {e}")
            raise
        except Exception as e:
            logger_ctx.error(f"Ollama analysis failed: {e}")
            raise AgentError(
                f"Ollama analysis failed: {e}", details={"prompt_length": len(prompt)}
            ) from e


class OllamaModel:
    """Fallback Ollama model for local AI processing."""

    def __init__(self):
        self.host = settings.ollama_host
        self.port = settings.ollama_port
        self.model = settings.ollama_model
        self.RATE_LIMIT_STATUS = 429
        self.SERVER_ERROR_MIN = 500

    async def generate(self, prompt: str, context: str = "") -> str:
        """Generate text using Ollama."""
        logger_ctx = logger.bind(model=self.model, prompt_length=len(prompt))
        try:
            if httpx is None:
                raise ImportError
            async with httpx.AsyncClient() as client:  # type: ignore[attr-defined]
                response = await client.post(
                    f"http://{self.host}:{self.port}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": f"{context}\n\n{prompt}" if context else prompt,
                        "stream": False,
                    },
                    timeout=60.0,
                )
                if response.status_code == self.RATE_LIMIT_STATUS:
                    raise RateLimitError("Ollama rate limit exceeded")
                if response.status_code >= self.SERVER_ERROR_MIN:
                    raise NetworkError("Ollama server error")
                response.raise_for_status()
                data = response.json()
                analysis = data.get("response", "No response generated")
                logger_ctx.info("Ollama generation completed successfully")
                return analysis

        except ImportError:
            error_msg = "Ollama client not available. Install httpx: pip install httpx"
            logger_ctx.error(error_msg)
            raise AgentError(error_msg) from None
        except Exception as e:
            logger_ctx.error(f"Ollama generation failed: {e}")
            raise AgentError(
                f"Ollama generation failed: {e}", details={"prompt_length": len(prompt)}
            ) from e


SNIPPET_LEN = 50


async def run_agent(prompt: str, **kwargs: Any) -> str:
    """Run the AI agent with the given prompt."""
    logger_ctx = logger.bind(
        prompt=(prompt[:SNIPPET_LEN] + "..." if len(prompt) > SNIPPET_LEN else prompt),
        kwargs=kwargs,
    )
    try:
        if AGENTS_AVAILABLE and os.environ.get("OPENAI_API_KEY"):
            client = AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"])  # type: ignore[no-untyped-call]
            resp = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],  # type: ignore[list-item]
                temperature=0.2,
            )
            return resp.choices[0].message.content or ""

        logger_ctx.warning("Falling back to Ollama: OpenAI Agents unavailable or not configured")
        return await OllamaModel().generate(prompt, context="agent_fallback")
    except AgentError:
        raise
    except Exception as e:
        logger_ctx.error(f"Agent execution failed: {e}")
        raise AgentError(
            f"Agent execution failed: {e}", details={"prompt_length": len(prompt)}
        ) from e


# Convenience function for backward compatibility
async def generate_response(prompt: str, **kwargs: Any) -> str:
    """Generate a response using the available AI backend."""
    return await run_agent(prompt, **kwargs)
