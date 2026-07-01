from typing import Dict

class SeverityClassifier:
    def __init__(self):
        self.severity_thresholds = {
            'hemoglobin': {
                'critical_low': 7.0, 'severe_low': 9.0, 'moderate_low': 11.0,
                'moderate_high': 18.0, 'severe_high': 20.0
            },
            'hba1c': {
                'normal': 5.6, 'mild': 6.4, 'moderate': 7.9, 'severe': 9.0
            },
            'glucose': {
                'low': 70, 'prediabetes': 125, 'diabetes': 200, 'severe': 300
            },
            'ldl': {
                'optimal': 100, 'near_optimal': 129, 'borderline': 159, 'high': 189
            },
            'creatinine': {
                'mild': 1.5, 'moderate': 3.0, 'severe': 5.0
            }
        }
    
    def classify(self, parameter: str, value: float, status: str) -> Dict:
        if status == 'Normal':
            return {'severity': 'Normal', 'level': 0, 'color': 'green'}
        
        severity_map = self._get_severity_level(parameter, value, status)
        return severity_map
    
    def _get_severity_level(self, parameter: str, value: float, status: str) -> Dict:
        if parameter == 'hemoglobin' and status == 'Low':
            if value < 7.0:
                return {'severity': 'Critical', 'level': 5, 'color': 'red'}
            elif value < 9.0:
                return {'severity': 'Severe', 'level': 4, 'color': 'darkred'}
            elif value < 11.0:
                return {'severity': 'Moderate', 'level': 3, 'color': 'orange'}
            else:
                return {'severity': 'Mild', 'level': 2, 'color': 'yellow'}
        
        elif parameter == 'hba1c':
            if value > 9.0:
                return {'severity': 'Severe', 'level': 4, 'color': 'red'}
            elif value > 7.9:
                return {'severity': 'Moderate', 'level': 3, 'color': 'orange'}
            elif value > 6.4:
                return {'severity': 'Mild', 'level': 2, 'color': 'yellow'}
            else:
                return {'severity': 'Normal', 'level': 0, 'color': 'green'}
        
        elif parameter == 'ldl' and status == 'High':
            if value > 189:
                return {'severity': 'Severe', 'level': 4, 'color': 'red'}
            elif value > 159:
                return {'severity': 'Moderate', 'level': 3, 'color': 'orange'}
            elif value > 129:
                return {'severity': 'Mild', 'level': 2, 'color': 'yellow'}
            else:
                return {'severity': 'Normal', 'level': 0, 'color': 'green'}
        
        elif parameter == 'creatinine' and status == 'High':
            if value > 5.0:
                return {'severity': 'Critical', 'level': 5, 'color': 'red'}
            elif value > 3.0:
                return {'severity': 'Severe', 'level': 4, 'color': 'darkred'}
            elif value > 1.5:
                return {'severity': 'Moderate', 'level': 3, 'color': 'orange'}
            else:
                return {'severity': 'Mild', 'level': 2, 'color': 'yellow'}
        
        return {'severity': 'Mild', 'level': 2, 'color': 'yellow'}
