import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
from model_config import ModelPricing

class CostMonitor:
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Set up logging
        self.setup_logging()
        
        # Initialize cost tracking
        self.total_cost = 0.0
        self.cost_by_model: Dict[str, float] = {}
        self.cost_by_file: Dict[str, float] = {}
        
    def setup_logging(self):
        """Set up logging configuration."""
        log_file = self.log_dir / f"cost_monitor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def calculate_cost(self, model_info: ModelPricing, input_tokens: int, output_tokens: int, is_cached: bool = False) -> float:
        """Calculate the cost for a given number of tokens."""
        input_cost = (input_tokens / 1_000_000) * (model_info.cached_input_price if is_cached else model_info.input_price)
        output_cost = (output_tokens / 1_000_000) * model_info.output_price
        return input_cost + output_cost
    
    def log_request(self, model_name: str, file_path: str, input_tokens: int, output_tokens: int, 
                   is_cached: bool = False, model_info: ModelPricing = None) -> float:
        """Log a request and calculate its cost."""
        if model_info is None:
            from model_config import get_model_info
            model_info = get_model_info(model_name)
        
        cost = self.calculate_cost(model_info, input_tokens, output_tokens, is_cached)
        
        # Update cost tracking
        self.total_cost += cost
        self.cost_by_model[model_name] = self.cost_by_model.get(model_name, 0) + cost
        self.cost_by_file[file_path] = self.cost_by_file.get(file_path, 0) + cost
        
        # Log the request
        self.logger.info(
            f"📝 요청 처리 완료 - 모델: {model_name}, 파일: {file_path}, "
            f"입력 토큰: {input_tokens}, 출력 토큰: {output_tokens}, "
            f"비용: ${cost:.4f}"
        )
        
        return cost
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of all costs."""
        return {
            "total_cost": self.total_cost,
            "cost_by_model": self.cost_by_model,
            "cost_by_file": self.cost_by_file,
            "timestamp": datetime.now().isoformat()
        }
    
    def save_summary(self, output_file: str = "cost_summary.json"):
        """Save the cost summary to a JSON file."""
        summary = self.get_summary()
        with open(output_file, 'w') as f:
            json.dump(summary, f, indent=2)
        self.logger.info(f"💰 비용 요약이 {output_file}에 저장되었습니다") 