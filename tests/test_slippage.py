import pytest
from models.slippage import SlippageModel

def test_slippage_calculation():
    model = SlippageModel()
    book_depth = [
        ("100.0", "10.0"),
        ("100.1", "5.0"),
        ("100.2", "20.0")
    ]
    
    # Test baseline calculation
    slippage = model._baseline_slippage(15.0, book_depth)
    expected = ((10.0*100.0 + 5.0*100.1)/15.0 - 100.0)/100.0 * 100
    assert abs(slippage - expected) < 0.001
    
    # Test model prediction
    model.train([10, 20, 30], [0.1, 0.2, 0.3])
    assert model.predict(15.0, book_depth) is not None