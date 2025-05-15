import unittest
from models.algren_chriss import AlmgrenChriss

class TestAlmgrenChriss(unittest.TestCase):
    def setUp(self):
        self.model = AlmgrenChriss()
        self.test_book = {
            'bids': [[50000, 1.5], [49900, 2.0]],
            'asks': [[50100, 1.2], [50200, 3.0]]
        }
    
    def test_impact_calculation(self):
        result = self.model.calculate_impact(100, self.test_book)
        self.assertIn('total', result)
        self.assertGreater(result['total'], 0)