from pydantic import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    asr_model_path: Path
    gpt2_model_path: Path
    trie_pickle_path: Path
    device: str = "cuda"

    class Config:
        env_file = ".env"

settings = Settings()
