from typing import Dict, List

class ReportParser:
    def __init__(self):
        self.reference_ranges = {
            'hemoglobin': {'male': (13.5, 17.5), 'female': (12.0, 15.5), 'unit': 'g/dL'},
            'hba1c': {'normal': (4.0, 5.6), 'unit': '%'},
            'glucose': {'fasting': (70, 100), 'unit': 'mg/dL'},
            'cholesterol': {'normal': (0, 200), 'unit': 'mg/dL'},
            'ldl': {'optimal': (0, 100), 'unit': 'mg/dL'},
            'hdl': {'male': (40, 999), 'female': (50, 999), 'unit': 'mg/dL'},
            'triglycerides': {'normal': (0, 150), 'unit': 'mg/dL'},
            'rbc': {'male': (4.5, 5.9), 'female': (4.0, 5.2), 'unit': 'million/μL'},
            'wbc': {'normal': (4.5, 11.0), 'unit': 'thousand/μL'},
            'platelets': {'normal': (150, 400), 'unit': 'thousand/μL'},
            'creatinine': {'male': (0.7, 1.3), 'female': (0.6, 1.1), 'unit': 'mg/dL'},
            'bun': {'normal': (7, 20), 'unit': 'mg/dL'},
            'vitamin_d': {'normal': (30, 100), 'unit': 'ng/mL'},
            'tsh': {'normal': (0.4, 4.0), 'unit': 'μIU/mL'},
            't3': {'normal': (80, 200), 'unit': 'ng/dL'},
            't4': {'normal': (5.0, 12.0), 'unit': 'μg/dL'},
            'alt': {'normal': (7, 56), 'unit': 'U/L'},
            'ast': {'normal': (10, 40), 'unit': 'U/L'}
        }
    
    def parse_report(self, extracted_data, gender: str = 'male') -> List[Dict]:
        parsed_results = []
        
        # Handle both dict and tuple returns from extractor
        if isinstance(extracted_data, tuple):
            print(f"Warning: parse_report received tuple, attempting to unwrap...")
            # If it's a tuple, try to find and extract the dict with blood parameters
            for i, item in enumerate(extracted_data):
                if isinstance(item, dict) and any(key in item for key in ['hemoglobin', 'rbc', 'glucose', 'hba1c']):
                    extracted_data = item
                    print(f"  Found blood parameters dict at element {i}")
                    break
            else:
                # If no dict with blood params found, use first element if it's a dict
                if len(extracted_data) > 0 and isinstance(extracted_data[0], dict):
                    extracted_data = extracted_data[0]
                    print(f"  Using first element (dict)")
                else:
                    print(f"  No valid dict found in tuple")
                    return []
        
        # Ensure extracted_data is a dictionary
        if not isinstance(extracted_data, dict):
            print(f"Warning: extracted_data is {type(extracted_data)}, expected dict")
            return []
        
        for param, data in extracted_data.items():
            if param in self.reference_ranges:
                # Handle if data is not a dict
                if not isinstance(data, dict):
                    continue
                    
                result = self._analyze_parameter(param, data['value'], gender)
                result['unit'] = data.get('unit', self.reference_ranges[param]['unit'])
                result['raw_text'] = data.get('raw_text', '')
                parsed_results.append(result)
        
        return parsed_results
    
    def _analyze_parameter(self, param: str, value: float, gender: str) -> Dict:
        ranges = self.reference_ranges[param]
        
        if gender in ranges:
            min_val, max_val = ranges[gender]
        elif 'normal' in ranges:
            min_val, max_val = ranges['normal']
        elif 'optimal' in ranges:
            min_val, max_val = ranges['optimal']
        else:
            min_val, max_val = list(ranges.values())[0]
        
        status = 'Normal'
        if value < min_val:
            status = 'Low'
        elif value > max_val:
            status = 'High'
        
        return {
            'parameter': param,
            'value': value,
            'status': status,
            'reference_min': min_val,
            'reference_max': max_val
        }
