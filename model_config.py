from dataclasses import dataclass
from typing import Dict

@dataclass
class ModelPricing:
    input_price: float  # per 1M tokens
    cached_input_price: float  # per 1M tokens
    output_price: float  # per 1M tokens
    description: str

MODEL_PRICING: Dict[str, ModelPricing] = {
    "gpt-4.1": ModelPricing(
        input_price=2.00,
        cached_input_price=0.50,
        output_price=8.00,
        description="Smartest model for complex tasks"
    ),
    "gpt-4.1-mini": ModelPricing(
        input_price=0.40,
        cached_input_price=0.10,
        output_price=1.60,
        description="Affordable model balancing speed and intelligence"
    ),
    "gpt-4.1-nano": ModelPricing(
        input_price=0.100,
        cached_input_price=0.025,
        output_price=0.400,
        description="Fastest, most cost-effective model for low-latency tasks"
    ),
    "o3": ModelPricing(
        input_price=10.00,
        cached_input_price=2.50,
        output_price=40.00,
        description="Most powerful reasoning model with leading performance on coding, math, science, and vision"
    ),
    "o4-mini": ModelPricing(
        input_price=1.100,
        cached_input_price=0.275,
        output_price=4.400,
        description="Faster, cost-efficient reasoning model delivering strong performance on math, coding and vision"
    )
}

def get_model_info(model_name: str) -> ModelPricing:
    """Get pricing information for a specific model."""
    if model_name not in MODEL_PRICING:
        raise ValueError(f"Unknown model: {model_name}")
    return MODEL_PRICING[model_name]

def list_available_models() -> Dict[str, str]:
    """List all available models with their descriptions."""
    return {name: pricing.description for name, pricing in MODEL_PRICING.items()} 