import unittest
from unittest.mock import MagicMock, patch
import numpy as np
import sys
import os

# Adicionar diretório pai ao path para importar app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.detector import PPEDetector

class TestPPEDetector(unittest.TestCase):
    def setUp(self):
        self.detector = PPEDetector(model_path="dummy_path.pt")
        
    @patch('app.services.detector.YOLO')
    def test_load_model(self, mock_yolo):
        self.detector.load_model()
        self.assertTrue(self.detector.is_loaded)
        mock_yolo.assert_called_once_with("dummy_path.pt")
        
    @patch('app.services.detector.YOLO')
    def test_detect(self, mock_yolo):
        # Mock do resultado do YOLO
        mock_result = MagicMock()
        mock_box = MagicMock()
        mock_box.xyxy = [[10, 10, 100, 100]]
        mock_box.conf = [0.9]
        mock_box.cls = [0]
        
        mock_result.boxes = [mock_box]
        mock_yolo.return_value.names = {0: 'Hardhat', 1: 'NO-Hardhat'}
        mock_yolo.return_value.return_value = [mock_result]
        
        self.detector.load_model()
        
        frame = np.zeros((640, 640, 3), dtype=np.uint8)
        result = self.detector.detect(frame)
        
        self.assertEqual(len(result['detections']), 1)
        self.assertEqual(result['detections'][0]['class_name'], 'Hardhat')
        self.assertEqual(result['detections'][0]['confidence'], 0.9)
        self.assertEqual(result['detections'][0]['bbox'], [10, 10, 100, 100])
        
    def test_get_violations(self):
        detections = [
            {'class_name': 'Hardhat', 'confidence': 0.9},
            {'class_name': 'NO-Hardhat', 'confidence': 0.8},
            {'class_name': 'Safety Vest', 'confidence': 0.95}
        ]
        
        violations = self.detector.get_violations(detections)
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0]['class_name'], 'NO-Hardhat')

if __name__ == '__main__':
    unittest.main()
