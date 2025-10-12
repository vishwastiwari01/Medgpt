import os
import requests
from typing import Optional

class LLMHandler:
    """
    Handles LLM inference with support for:
    - Ollama (local) – e.g., meditron, llama3.1, mistral
    - Anthropic Claude (optional via API key)
    - Fallback (no LLM)
    """
    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
        self.backend = self._detect_backend()
        self.recommended_models = ["meditron", "llama3.1:8b", "mistral:7b", "llama3.2:3b", "llama2:7b"]
        self.ollama_model = self._find_available_model()

    def _detect_backend(self) -> str:
        try:
            r = requests.get(f"{self.ollama_base_url}/api/tags", timeout=2)
            if r.status_code == 200:
                return "ollama"
        except Exception:
            pass
        if self.api_key:
            return "claude"
        return "fallback"

    def _find_available_model(self) -> Optional[str]:
        if self.backend != "ollama":
            return None
        try:
            r = requests.get(f"{self.ollama_base_url}/api/tags", timeout=2)
            if r.status_code == 200:
                available = [m["name"] for m in r.json().get("models", [])]
                for model in self.recommended_models:
                    if model in available:
                        print(f"✅ Using Ollama model: {model}")
                        return model
                    for avail in available:
                        if model.split(":")[0] in avail:
                            print(f"✅ Using Ollama model: {avail}")
                            return avail
                if available:
                    print(f"⚠️ Using available model: {available[0]}")
                    return available[0]
        except Exception as e:
            print(f"⚠️ Error detecting Ollama models: {e}")
        return None

    def generate_answer(self, question: str, context: str, enhanced_mode: bool = True) -> str:
        if self.backend == "ollama":
            return self._generate_ollama(question, context)
        elif self.backend == "claude":
            return self._generate_claude(question, context)
        return self._generate_fallback(question, context)

    def _generate_ollama(self, question: str, context: str) -> str:
        prompt = f"""You are a medical information assistant. Provide a concise, evidence-based answer using ONLY the information from the provided medical documents.

CRITICAL RULES:
1. Answer in 2-3 clear paragraphs maximum
2. Use ONLY information from the context below
3. If information is insufficient, state clearly that more guidance is required.
4. Include specific clinical details (drug names, doses, criteria) when present.
5. Be precise and clinical in tone.

MEDICAL CONTEXT:
{context}

QUESTION: {question}

ANSWER (2-3 paragraphs):"""
        try:
            r = requests.post(
                f"{self.ollama_base_url}/api/generate",
                json={
                    "model": self.ollama_model or "meditron:latest",
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,
                        "top_p": 0.9,
                        "top_k": 40,
                        "num_predict": 512,
                        "stop": ["\n\n\n", "QUESTION:", "CONTEXT:"]
                    }
                },
                timeout=30
            )
            if r.status_code == 200:
                ans = (r.json().get("response") or "").strip()
                ans = ans.replace("ANSWER:", "").replace("Answer:", "").strip()
                return ans or "I could not generate an answer."
            return self._generate_fallback(question, context)
        except Exception as e:
            print(f"⚠️ Ollama error: {e}")
            return self._generate_fallback(question, context)

    def _generate_claude(self, question: str, context: str, enhanced_mode: bool = True) -> str:
        prompt = f"""You are a medical information assistant. Provide a concise, evidence-based answer using ONLY the provided context.

Context:
{context}

Question: {question}

Provide a brief answer (2-3 paragraphs) with specific clinical details. If information is incomplete, acknowledge this."""
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)
            msg = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=512,
                temperature=0.1,
                messages=[{"role": "user", "content": prompt}],
            )
            return getattr(msg, "content", [{"text": ""}])[0].get("text", "").strip() or \
                   "Claude returned no content."
        except Exception as e:
            print(f"⚠️ Claude error: {e}")
            return self._generate_fallback(question, context)

    def _generate_fallback(self, question: str, context: str) -> str:
        lines = [ln.strip() for ln in context.splitlines() if ln.strip()]
        hits = []
        for ln in lines:
            low = ln.lower()
            if any(t in low for t in [
                "treatment", "therapy", "medication", "dose", "dosage",
                "criteria", "diagnosis", "target", "first-line",
                "guideline", "recommended", "contraindicat", "adverse"
            ]):
                hits.append(ln)
        if hits:
            return ("Based on the available medical documents:\n\n"
                    + " ".join(hits[:3])
                    + "\n\n⚠️ Note: This response is generated without full LLM reasoning.")
        return ("⚠️ Insufficient information found in the knowledge base to answer this query. "
                "Please consult clinical guidelines or a medical professional.")

    def get_status(self) -> dict:
        return {
            "backend": self.backend,
            "model": self.ollama_model if self.backend == "ollama" else self.backend,
            "ready": self.backend in ["ollama", "claude", "fallback"],
        }
