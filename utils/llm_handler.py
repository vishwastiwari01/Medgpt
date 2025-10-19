"""
LLM Handler - Fixed Groq API and Ollama integration
Natural clinical responses without artificial persona
"""
import os
import requests
from typing import Optional

class LLMHandler:
    def __init__(self):
        """Initialize LLM handler with Groq or Ollama"""
        self.backend = "fallback"
        self.model = None
        self.groq_client = None
        
        # Try Groq first (cloud, fast)
        groq_key = os.getenv("GROQ_API_KEY")
        if groq_key:
            try:
                from groq import Groq
                # ✅ FIXED: Use correct base URL
                self.groq_client = Groq(
                    api_key=groq_key,
                    base_url="https://api.groq.com"  # Without /openai/v1
                )
                # Test connection
                self.groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": "test"}],
                    max_tokens=10
                )
                self.backend = "groq"
                self.model = "llama-3.3-70b-versatile"
                print("✅ Groq connected: llama-3.1-70b-versatile")
                return
            except Exception as e:
                print(f"⚠️ Groq init failed: {e}")
        
        # Try Ollama (local)
        if self._check_ollama():
            self.backend = "ollama"
            print(f"✅ Using Ollama: {self.model}")
            return
        
        # Fallback
        print("⚠️ No LLM available - using fallback mode")
    
    def _check_ollama(self) -> bool:
        """Check if Ollama is available"""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            if response.status_code == 200:
                models = response.json().get("models", [])
                # Prefer specific models
                preferred = ["meditron", "llama3.1", "llama3", "mistral"]
                
                for pref in preferred:
                    for m in models:
                        name = m.get("name", "").lower()
                        if pref in name:
                            self.model = m.get("name")
                            return True
                
                # Use first available
                if models:
                    self.model = models[0].get("name")
                    return True
        except:
            pass
        return False
    
    def generate_answer(self, question: str, context: str) -> str:
        """Generate professional clinical answer"""
        if self.backend == "groq":
            return self._generate_groq(question, context)
        elif self.backend == "ollama":
            return self._generate_ollama(question, context)
        else:
            return self._generate_fallback(question, context)
    
    def _generate_groq(self, question: str, context: str) -> str:
        """Generate using Groq Cloud API"""
        try:
            # Professional clinical prompt
            prompt = f"""Based on the medical literature provided, answer this clinical question accurately and professionally.

Structure your response with clear paragraphs. Include specific clinical details like drug names, dosages, diagnostic criteria, and treatment protocols when present in the context.

Medical Literature:
{context}

Clinical Question: {question}

Provide a comprehensive, evidence-based response:"""
            
            completion = self.groq_client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a medical knowledge assistant. Provide accurate, evidence-based clinical information using professional medical terminology. Structure responses clearly with well-organized paragraphs."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=1024,
                top_p=0.9,
            )
            
            answer = completion.choices[0].message.content.strip()
            return answer if answer else "Unable to generate response."
            
        except Exception as e:
            print(f"⚠️ Groq error: {e}")
            return self._generate_fallback(question, context)
    
    def _generate_ollama(self, question: str, context: str) -> str:
        """Generate using local Ollama"""
        try:
            prompt = f"""Based on the medical literature below, provide a clear, evidence-based answer to the clinical question.

Use professional medical terminology and structure your response in organized paragraphs. Include specific details like drug names, dosages, and diagnostic criteria when available.

Medical Literature:
{context}

Question: {question}

Answer:"""
            
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "num_predict": 512,
                        "top_p": 0.9
                    }
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json().get("response", "").strip()
                return result if result else "Unable to generate response."
            else:
                return self._generate_fallback(question, context)
                
        except requests.exceptions.Timeout:
            print("⚠️ Ollama timeout - using fallback")
            return self._generate_fallback(question, context)
        except Exception as e:
            print(f"⚠️ Ollama error: {e}")
            return self._generate_fallback(question, context)
    
    def _generate_fallback(self, question: str, context: str) -> str:
        """Simple extractive fallback"""
        sentences = context.split('. ')
        relevant = []
        
        query_keywords = set(question.lower().split())
        for sentence in sentences[:20]:
            sentence_lower = sentence.lower()
            if any(keyword in sentence_lower for keyword in query_keywords):
                relevant.append(sentence.strip())
                if len(relevant) >= 4:
                    break
        
        if relevant:
            result = '. '.join(relevant)
            if not result.endswith('.'):
                result += '.'
            return result + "\n\n⚠️ Limited response mode. Configure GROQ_API_KEY for enhanced responses."
        
        return "Insufficient information in the knowledge base to answer this query."
    
    def get_status(self) -> dict:
        """Get LLM status"""
        return {
            "backend": self.backend,
            "model": self.model if self.model else "fallback",
            "ready": True,
        }


def pick_groq_model() -> str:
    """Pick best available Groq model"""
    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key:
        try:
            from groq import Groq
            # ✅ FIXED: Use correct base URL
            client = Groq(
                api_key=groq_key,
                base_url="https://api.groq.com"
            )
            # Test with best model
            client.chat.completions.create(
                model="llama-3.1-70b-versatile",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            return "llama-3.1-70b-versatile"
        except:
            pass
    return "not configured"