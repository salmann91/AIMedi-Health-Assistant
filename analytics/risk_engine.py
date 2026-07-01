from typing import Dict, List

class RiskEngine:
    def assess_risks(self, parsed_results: List[Dict]) -> Dict:
        risks = {
            'anemia': self._check_anemia(parsed_results),
            'diabetes': self._check_diabetes(parsed_results),
            'cholesterol': self._check_cholesterol(parsed_results),
            'kidney': self._check_kidney(parsed_results),
            'liver': self._check_liver(parsed_results),
            'thyroid': self._check_thyroid(parsed_results)
        }
        
        overall_risk_score = self._calculate_overall_risk(risks)
        
        return {
            'risks': risks,
            'overall_risk_score': overall_risk_score,
            'risk_level': self._get_risk_level(overall_risk_score)
        }
    
    def _check_anemia(self, results: List[Dict]) -> Dict:
        hb = self._get_parameter_value(results, 'hemoglobin')
        rbc = self._get_parameter_value(results, 'rbc')
        
        if not hb:
            return {'detected': False, 'score': 0}
        
        if hb['status'] == 'Low':
            if hb['value'] < 10:
                return {'detected': True, 'score': 8, 'severity': 'High', 'message': 'Severe anemia detected'}
            else:
                return {'detected': True, 'score': 5, 'severity': 'Moderate', 'message': 'Mild to moderate anemia'}
        
        return {'detected': False, 'score': 0}
    
    def _check_diabetes(self, results: List[Dict]) -> Dict:
        hba1c = self._get_parameter_value(results, 'hba1c')
        glucose = self._get_parameter_value(results, 'glucose')
        
        if hba1c and hba1c['value'] >= 6.5:
            return {'detected': True, 'score': 9, 'severity': 'High', 'message': 'Diabetes detected'}
        elif hba1c and hba1c['value'] >= 5.7:
            return {'detected': True, 'score': 5, 'severity': 'Moderate', 'message': 'Prediabetes detected'}
        elif glucose and glucose['value'] >= 126:
            return {'detected': True, 'score': 7, 'severity': 'High', 'message': 'High fasting glucose'}
        
        return {'detected': False, 'score': 0}
    
    def _check_cholesterol(self, results: List[Dict]) -> Dict:
        ldl = self._get_parameter_value(results, 'ldl')
        hdl = self._get_parameter_value(results, 'hdl')
        triglycerides = self._get_parameter_value(results, 'triglycerides')
        
        score = 0
        messages = []
        
        if ldl and ldl['value'] > 160:
            score += 7
            messages.append('High LDL cholesterol')
        elif ldl and ldl['value'] > 130:
            score += 4
            messages.append('Borderline high LDL')
        
        if hdl and hdl['value'] < 40:
            score += 5
            messages.append('Low HDL cholesterol')
        
        if triglycerides and triglycerides['value'] > 200:
            score += 5
            messages.append('High triglycerides')
        
        if score >= 10:
            return {'detected': True, 'score': score, 'severity': 'High', 'message': ', '.join(messages)}
        elif score > 0:
            return {'detected': True, 'score': score, 'severity': 'Moderate', 'message': ', '.join(messages)}
        
        return {'detected': False, 'score': 0}
    
    def _check_kidney(self, results: List[Dict]) -> Dict:
        creatinine = self._get_parameter_value(results, 'creatinine')
        bun = self._get_parameter_value(results, 'bun')
        
        if creatinine and creatinine['value'] > 2.0:
            return {'detected': True, 'score': 9, 'severity': 'High', 'message': 'Severe kidney dysfunction'}
        elif creatinine and creatinine['value'] > 1.5:
            return {'detected': True, 'score': 6, 'severity': 'Moderate', 'message': 'Mild kidney dysfunction'}
        
        return {'detected': False, 'score': 0}
    
    def _check_liver(self, results: List[Dict]) -> Dict:
        alt = self._get_parameter_value(results, 'alt')
        ast = self._get_parameter_value(results, 'ast')
        
        score = 0
        messages = []
        
        if alt and alt['value'] > 100:
            score += 7
            messages.append('Significantly elevated ALT')
        elif alt and alt['value'] > 56:
            score += 4
            messages.append('Mildly elevated ALT')
        
        if ast and ast['value'] > 100:
            score += 7
            messages.append('Significantly elevated AST')
        
        if score > 0:
            severity = 'High' if score >= 7 else 'Moderate'
            return {'detected': True, 'score': score, 'severity': severity, 'message': ', '.join(messages)}
        
        return {'detected': False, 'score': 0}
    
    def _check_thyroid(self, results: List[Dict]) -> Dict:
        tsh = self._get_parameter_value(results, 'tsh')
        
        if not tsh:
            return {'detected': False, 'score': 0}
        
        if tsh['value'] > 10:
            return {'detected': True, 'score': 7, 'severity': 'High', 'message': 'Hypothyroidism detected'}
        elif tsh['value'] > 4.5:
            return {'detected': True, 'score': 4, 'severity': 'Moderate', 'message': 'Subclinical hypothyroidism'}
        elif tsh['value'] < 0.1:
            return {'detected': True, 'score': 7, 'severity': 'High', 'message': 'Hyperthyroidism detected'}
        
        return {'detected': False, 'score': 0}
    
    def _get_parameter_value(self, results: List[Dict], parameter: str) -> Dict:
        for result in results:
            if result['parameter'] == parameter:
                return result
        return None
    
    def _calculate_overall_risk(self, risks: Dict) -> int:
        total_score = 0
        for risk in risks.values():
            if risk.get('detected'):
                total_score += risk['score']
        return min(total_score, 100)
    
    def _get_risk_level(self, score: int) -> str:
        if score >= 20:
            return 'Critical'
        elif score >= 15:
            return 'High'
        elif score >= 8:
            return 'Moderate'
        elif score > 0:
            return 'Low'
        return 'Minimal'
