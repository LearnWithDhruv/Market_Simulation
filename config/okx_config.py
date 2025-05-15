import yaml
from dataclasses import dataclass

@dataclass
class OKXConfig:
    ws_url: str = "wss://ws.okx.com:8443/ws/v5/public"
    symbols: list = None
    fee_tiers: dict = None
    
    @classmethod
    def load(cls, path='config/settings.yaml'):
        with open(path) as f:
            data = yaml.safe_load(f)
        return cls(
            symbols=data['okx']['symbols'],
            fee_tiers=data['okx']['fee_tiers']
        )