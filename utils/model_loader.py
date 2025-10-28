from sentence_transformers import SentenceTransformer
from typing import Optional
from settings import settings


class ModelLoader:
    
    def __init__(self):
        self.model: Optional[SentenceTransformer] = None
    
    def initialize(self):
        print(f"Loading SentenceTransformer model: {settings.SENTENCE_TRANSFORMER_MODEL}...")
        self.model = SentenceTransformer(settings.SENTENCE_TRANSFORMER_MODEL)
        print("Model loaded successfully!")
    
    def get_model(self) -> SentenceTransformer:
        if self.model is None:
            raise RuntimeError("Model not loaded. Call initialize() first.")
        return self.model
    
    def is_ready(self) -> bool:
        return self.model is not None
    
    def encode(self, text: str, convert_to_tensor: bool = False):
        if not self.is_ready():
            raise RuntimeError("Model not loaded")
        return self.model.encode(text, convert_to_tensor=convert_to_tensor)
    
    def encode_batch(self, texts: list, batch_size: int = 128, convert_to_tensor: bool = False):
        if not self.is_ready():
            raise RuntimeError("Model not loaded")
        return self.model.encode(texts, batch_size=batch_size, convert_to_tensor=convert_to_tensor)


model_loader = ModelLoader()
