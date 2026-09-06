import time
import os
import json
import urllib.request
import urllib.error
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List

class LLMProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, temperature: float = 0.0, max_tokens: int = 512) -> str:
        """Generates a text response from the given prompt."""
        pass
        
    @abstractmethod
    def health_check(self) -> bool:
        """Returns True if the provider is available and ready."""
        pass

class OpenAIProvider(LLMProvider):
    """Provider for OpenAI-compatible APIs (OpenAI, vLLM, Together, etc)."""
    def __init__(self, model_name: str = None, api_key: str = None, base_url: str = None):
        self.model_name = model_name or os.environ.get("LLM_MODEL", "gpt-4o-mini")
        self.api_key = api_key or os.environ.get("LLM_API_KEY", "")
        self.base_url = base_url or os.environ.get("LLM_BASE_URL", "https://api.openai.com/v1")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
    def generate(self, prompt: str, temperature: float = 0.0, max_tokens: int = 512) -> str:
        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=self.headers, method='POST')
        with urllib.request.urlopen(req, timeout=60) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data["choices"][0]["message"]["content"]
        
    def health_check(self) -> bool:
        try:
            url = f"{self.base_url}/models"
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=5) as resp:
                return resp.status == 200
        except Exception:
            return False

class OllamaProvider(LLMProvider):
    """Provider for Ollama local instances."""
    def __init__(self, model_name: str = None, base_url: str = "http://localhost:11434"):
        self.model_name = model_name or os.environ.get("LLM_MODEL", "llama3")
        self.base_url = base_url
        self.headers = {"Content-Type": "application/json"}
        
    def generate(self, prompt: str, temperature: float = 0.0, max_tokens: int = 512) -> str:
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=self.headers, method='POST')
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            return data.get("response", "")
        
    def health_check(self) -> bool:
        try:
            req = urllib.request.Request(f"{self.base_url}/api/tags")
            with urllib.request.urlopen(req, timeout=3) as resp:
                return resp.status == 200
        except Exception:
            return False

class LocalHuggingFaceProvider(LLMProvider):
    """
    Provider for local Hugging Face models using transformers.
    For evaluation on systems without API keys or Ollama.
    """
    def __init__(self, model_name: str = None):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
        
        self.model_name = model_name or os.environ.get("LLM_MODEL", "Qwen/Qwen2.5-1.5B-Instruct")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        t0 = time.perf_counter()
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
        )
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name, 
            quantization_config=bnb_config,
            device_map="auto"
        )
        self.init_time = time.perf_counter() - t0
        
    def generate(self, prompt: str, temperature: float = 0.01, max_tokens: int = 512) -> str:
        messages = [
            {"role": "system", "content": "You are a helpful educational assistant. Answer using ONLY the provided context and citations."},
            {"role": "user", "content": prompt}
        ]
        text = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)
        
        do_sample = temperature > 0.01
        
        outputs = self.model.generate(
            **inputs, 
            max_new_tokens=max_tokens, 
            temperature=temperature if do_sample else None,
            do_sample=do_sample,
            pad_token_id=self.tokenizer.eos_token_id
        )
        
        # Remove prompt from output
        generated_ids = outputs[0][len(inputs.input_ids[0]):]
        return self.tokenizer.decode(generated_ids, skip_special_tokens=True)
        
    def health_check(self) -> bool:
        return self.model is not None

def get_provider(provider_type: str = None, **kwargs) -> LLMProvider:
    provider_type = provider_type or os.environ.get("LLM_PROVIDER", "huggingface")
    provider_type = provider_type.lower()
    
    if provider_type == "openai":
        return OpenAIProvider(**kwargs)
    elif provider_type == "ollama":
        return OllamaProvider(**kwargs)
    elif provider_type == "huggingface":
        return LocalHuggingFaceProvider(**kwargs)
    else:
        raise ValueError(f"Unknown provider type: {provider_type}")
