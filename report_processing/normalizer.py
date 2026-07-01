from typing import Dict, List

class DataNormalizer:
    @staticmethod
    def normalize_to_json(parsed_results: List[Dict]) -> Dict:
        normalized = {
            'parameters': {},
            'abnormalities': [],
            'summary': {
                'total_tests': len(parsed_results),
                'abnormal_count': 0,
                'high_count': 0,
                'low_count': 0
            }
        }
        
        for result in parsed_results:
            param = result['parameter']
            normalized['parameters'][param] = {
                'value': result['value'],
                'unit': result.get('unit', ''),
                'status': result['status'],
                'reference_range': f"{result['reference_min']}-{result['reference_max']}"
            }
            
            if result['status'] != 'Normal':
                normalized['abnormalities'].append({
                    'parameter': param,
                    'value': result['value'],
                    'status': result['status']
                })
                normalized['summary']['abnormal_count'] += 1
                
                if result['status'] == 'High':
                    normalized['summary']['high_count'] += 1
                else:
                    normalized['summary']['low_count'] += 1
        
        return normalized
