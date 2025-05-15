from typing import Dict, List
import yaml
from pathlib import Path

class FeeModel:
    def __init__(self, config_path: str = "config/settings.yaml"):
        self.config = self._load_config(config_path)
        self.fee_schedules = self.config['fee_schedules']

    def _load_config(self, config_path: str) -> Dict:
        with open(Path(__file__).parent.parent / config_path) as f:
            return yaml.safe_load(f)

    def calculate_fee(self, exchange: str, tier: int, notional: float, 
                     is_maker: bool = False) -> float:
        schedule = next(
            s for s in self.fee_schedules[exchange] 
            if s['tier'] == tier
        )
        rate = schedule['maker'] if is_maker else schedule['taker']
        return notional * rate

    def get_available_tiers(self, exchange: str) -> List[int]:
        return [s['tier'] for s in self.fee_schedules.get(exchange, [])]