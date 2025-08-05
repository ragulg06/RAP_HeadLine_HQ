"""
Model management module for loading and managing AI models.
"""

import torch
import spacy
import warnings
from typing import Optional, Tuple
from transformers import AutoModelForCausalLM, AutoTokenizer
from .config import config

warnings.filterwarnings('ignore')


class ModelManager:
    """Manages loading and configuration of AI models."""
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.nlp = None
        self.device = config.device
        
    def load_models(self) -> bool:
        """Load all required models."""
        try:
            print("🔄 Loading models...")
            
            # Load main language model
            success = self._load_language_model()
            if not success:
                return False
                
            # Load NLP model
            success = self._load_nlp_model()
            if not success:
                return False
                
            print("✅ All models loaded successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Error loading models: {e}")
            return False
    
    def _load_language_model(self) -> bool:
        """Load the main language model."""
        try:
            print(f"🔄 Loading language model: {config.model.model_name}")
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                config.model.model_name,
                trust_remote_code=True
            )
            self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Load model with quantization
            quantization_config = config.model.get_quantization_config()
            
            self.model = AutoModelForCausalLM.from_pretrained(
                config.model.model_name,
                quantization_config=quantization_config,
                device_map="auto",
                trust_remote_code=True
            )
            
            print("✅ Language model loaded successfully!")
            return True
            
        except Exception as e:
            print(f"⚠️ GPU loading failed, trying CPU fallback: {e}")
            return self._load_cpu_fallback()
    
    def _load_cpu_fallback(self) -> bool:
        """Load model on CPU as fallback."""
        try:
            print("🔄 Loading CPU fallback model...")
            
            self.tokenizer = AutoTokenizer.from_pretrained(config.model.model_name)
            self.tokenizer.pad_token = self.tokenizer.eos_token
            
            self.model = AutoModelForCausalLM.from_pretrained(config.model.model_name)
            
            print("✅ CPU fallback model loaded!")
            return True
            
        except Exception as e:
            print(f"❌ CPU fallback failed: {e}")
            return False
    
    def _load_nlp_model(self) -> bool:
        """Load spaCy NLP model."""
        try:
            print("🔄 Loading NLP model...")
            
            # Try to load the model
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                print("⚠️ spaCy model not found. Please run: python -m spacy download en_core_web_sm")
                return False
            
            print("✅ NLP model loaded!")
            return True
            
        except Exception as e:
            print(f"❌ Error loading NLP model: {e}")
            return False
    
    def get_model_info(self) -> dict:
        """Get information about loaded models."""
        info = {
            "device": self.device,
            "gpu_memory_gb": config.gpu_memory,
            "model_name": config.model.model_name,
            "model_loaded": self.model is not None,
            "tokenizer_loaded": self.tokenizer is not None,
            "nlp_loaded": self.nlp is not None
        }
        
        if self.model:
            info["model_parameters"] = sum(p.numel() for p in self.model.parameters())
            
        return info
    
    def generate_response(self, prompt: str, max_length: int = None) -> str:
        """Generate response using the loaded model."""
        if not self.model or not self.tokenizer:
            raise RuntimeError("Models not loaded. Call load_models() first.")
        
        try:
            max_length = max_length or config.model.max_tokens
            
            # Tokenize input
            inputs = self.tokenizer.encode(
                prompt, 
                return_tensors='pt', 
                max_length=config.model.context_window, 
                truncation=True
            )
            
            # Generate response
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_new_tokens=max_length,
                    temperature=config.model.temperature,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    repetition_penalty=1.1,
                    length_penalty=1.0,
                    early_stopping=True
                )
            
            # Decode response
            response = self.tokenizer.decode(
                outputs[0][inputs.shape[1]:], 
                skip_special_tokens=True
            )
            
            return response.strip()
            
        except Exception as e:
            print(f"❌ Generation error: {e}")
            return f"Error generating response: {str(e)}"
    
    def extract_entities(self, text: str) -> list:
        """Extract named entities from text."""
        if not self.nlp:
            raise RuntimeError("NLP model not loaded.")
        
        try:
            doc = self.nlp(text)
            entities = []
            
            for ent in doc.ents:
                entities.append({
                    "text": ent.text,
                    "label": ent.label_,
                    "start": ent.start_char,
                    "end": ent.end_char
                })
            
            return entities
            
        except Exception as e:
            print(f"❌ Entity extraction error: {e}")
            return []
    
    def cleanup(self):
        """Clean up model resources."""
        if self.model:
            del self.model
        if self.tokenizer:
            del self.tokenizer
        if self.nlp:
            del self.nlp
        
        if torch.cuda.is_available():
            torch.cuda.empty_cache()


# Global model manager instance
model_manager = ModelManager() 