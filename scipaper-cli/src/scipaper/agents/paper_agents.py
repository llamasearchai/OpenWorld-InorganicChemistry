import os
import httpx
from typing import Dict, Any
from scipaper.agents.tools import get_tools


class OllamaModel:
    """Lightweight wrapper; Ollama is optional and used if import succeeds.

    The generate method is async to match the agent interface, but it calls the
    sync Ollama client under the hood if available.
    """

    def __init__(self, model_name: str = "llama3.1"):
        self.model_name = model_name
        try:
            import ollama  # type: ignore
            self._ollama = ollama
            self.client = ollama.Client()
        except Exception:
            self._ollama = None
            self.client = None
        # Tools are resolved dynamically via get_tools() to allow test patching

    async def generate(self, prompt: str, context: Dict[str, Any]) -> str:
        # If Ollama isn't available, return a deterministic guidance message
        if self.client is None:
            # Try to handle simple tool routing heuristically
            lower = prompt.lower()
            if lower.startswith("search "):
                tools = get_tools()
                return await tools["tool_search"]["function"](
                    prompt.split("search ", 1)[1], context)
            if lower.startswith("fetch "):
                tools = get_tools()
                return await tools["tool_fetch"]["function"](
                    prompt.split("fetch ", 1)[1], context)
            return (
                "Local model unavailable. Install 'ollama' and run a model, or set "
                "OPENAI_API_KEY to use the OpenAI Agents backend.")

        # Call the sync client; do not await
        response = self.client.generate(
            model=self.model_name,
            prompt=prompt,
            stream=False,
        )

        text = response.get("response", "") if isinstance(response, dict) else str(response)
        lower = text.lower()
        if "tool_search" in lower or prompt.lower().startswith("search "):
            tools = get_tools()
            return await tools["tool_search"]["function"](
                prompt.split("search ", 1)[1] if "search " in prompt.lower() else text, context)
        if "tool_fetch" in lower or prompt.lower().startswith("fetch "):
            tools = get_tools()
            return await tools["tool_fetch"]["function"](
                prompt.split("fetch ", 1)[1] if "fetch " in prompt.lower() else text, context)
        return text

try:
    from agents import Agent, Runner, ModelSettings  # type: ignore
    from openai import AsyncOpenAI  # type: ignore
    from agents.models.openai_responses import OpenAIResponsesModel  # type: ignore
    AGENTS_AVAILABLE = True
except Exception:
    AGENTS_AVAILABLE = False

    # Define lightweight shims so tests can patch attributes without the SDK
    class _RunnerShim:  # pragma: no cover - used only when SDK missing
        @staticmethod
        async def run(*args, **kwargs):  # type: ignore[no-untyped-def]
            raise RuntimeError("Agents SDK not available")

    class _AgentShim:  # pragma: no cover
        def __init__(self, *args, **kwargs):  # type: ignore[no-untyped-def]
            pass

    class _ModelSettingsShim:  # pragma: no cover
        def __init__(self, *args, **kwargs):  # type: ignore[no-untyped-def]
            pass

    class _OpenAIResponsesModelShim:  # pragma: no cover
        def __init__(self, *args, **kwargs):  # type: ignore[no-untyped-def]
            pass

    class _AsyncOpenAIShim:  # pragma: no cover
        def __init__(self, *args, **kwargs):  # type: ignore[no-untyped-def]
            pass

    Runner = _RunnerShim  # type: ignore[assignment]
    Agent = _AgentShim  # type: ignore[assignment]
    ModelSettings = _ModelSettingsShim  # type: ignore[assignment]
    OpenAIResponsesModel = _OpenAIResponsesModelShim  # type: ignore[assignment]
    AsyncOpenAI = _AsyncOpenAIShim  # type: ignore[assignment]


async def run_agent(prompt: str, http_client: httpx.AsyncClient) -> str:
    context = {"http": http_client}

    # Fallback to local model unless full Agents stack and key are present
    # If either the SDK is missing or key is absent, fallback to local model/tools
    if not os.getenv("OPENAI_API_KEY"):
        return await OllamaModel().generate(prompt, context)
    if not AGENTS_AVAILABLE:
        # Minimal direct OpenAI fallback using responses client
        try:
            from openai import AsyncOpenAI  # type: ignore
        except Exception:
            return await OllamaModel().generate(prompt, context)
        client = AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"])  # type: ignore[no-untyped-call]
        # Simple completion with tool guidance; no tool-calling if SDK missing
        resp = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],  # type: ignore[list-item]
            temperature=0.2,
        )
        return resp.choices[0].message.content or ""

    model = OpenAIResponsesModel(
        model="gpt-4.1-mini",
        openai_client=AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"]))

    agent = Agent(
        name="PaperOps",
        instructions=(
            "Prefer open-access sources (arXiv). Use tools to search and fetch. "
            "Summarize concisely."),
        model=model,
        model_settings=ModelSettings(
            temperature=0.2,
            parallel_tool_calls=True),
        tools=list(get_tools().values()),
    )
    res = await Runner.run(agent, input=prompt, context=context)
    return res.final_output
