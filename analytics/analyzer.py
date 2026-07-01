from .severity import SeverityClassifier
from .risk_engine import RiskEngine
from typing import Dict, List

class HealthAnalyzer:
    def __init__(self):
        self.severity_classifier = SeverityClassifier()
        self.risk_engine = RiskEngine()
    
    def analyze(self, parsed_results: List[Dict]) -> Dict:
        enriched_results = []
        
        for result in parsed_results:
            severity_info = self.severity_classifier.classify(
                result['parameter'],
                result['value'],
                result['status']
            )
            result.update(severity_info)
            enriched_results.append(result)
        
        risk_assessment = self.risk_engine.assess_risks(parsed_results)
        
        return {
            'results': enriched_results,
            'risk_assessment': risk_assessment,
            'critical_findings': self._get_critical_findings(enriched_results)
        }
    
    def _get_critical_findings(self, results: List[Dict]) -> List[Dict]:
        critical = [r for r in results if r.get('level', 0) >= 4]
        return sorted(critical, key=lambda x: x.get('level', 0), reverse=True)
