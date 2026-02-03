"""
API Router for Configuration
"""

from fastapi import APIRouter
from typing import Dict, Optional
import os
import yaml

router = APIRouter()


def get_default_config() -> Dict:
    """Read default config from config.yaml."""
    config_path = os.path.join(
        os.path.dirname(__file__), 
        '..', '..', '..', 'config.yaml'
    )
    
    defaults = {
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-3.5-turbo"
    }
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                if config and 'llm' in config:
                    llm_config = config['llm']
                    if llm_config.get('base_url'):
                        defaults['base_url'] = llm_config['base_url']
                    if llm_config.get('model'):
                        defaults['model'] = llm_config['model']
        except Exception:
            pass
    
    return defaults


@router.get("/defaults")
async def get_config_defaults():
    """Get default configuration values (no API key)."""
    return get_default_config()


@router.get("/models")
async def get_available_models():
    """Get list of available models."""
    return {
        "models": [
            {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo"},
            {"id": "gpt-4", "name": "GPT-4"},
            {"id": "gpt-4-turbo", "name": "GPT-4 Turbo"},
            {"id": "DeepSeek-V3", "name": "DeepSeek V3"}
        ]
    }
