import re
from typing import Dict, Optional
from datetime import datetime

class PatientInfoExtractor:
    def __init__(self):
        self.patterns = {
            'name': [
                r'patient\s*name\s*:?\s*([A-Za-z\s\.]+)',
                r'name\s*:?\s*([A-Za-z\s\.]+)',
                r'patient\s*:?\s*([A-Za-z\s\.]+)',
                r'mr\.|mrs\.|ms\.\s*([A-Za-z\s\.]+)',
            ],
            'age': [
                r'age\s*:?\s*(\d+)\s*(?:years?|yrs?|y)?',
                r'(\d+)\s*(?:years?|yrs?|y)\s*(?:old)?',
                r'age\s*/\s*sex\s*:?\s*(\d+)',
            ],
            'gender': [
                r'sex\s*:?\s*(male|female|m|f)',
                r'gender\s*:?\s*(male|female|m|f)',
                r'age\s*/\s*sex\s*:?\s*\d+\s*/?\s*(male|female|m|f)',
            ],
            'date': [
                r'date\s*:?\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
                r'report\s*date\s*:?\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
                r'collection\s*date\s*:?\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
                r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
            ],
            'report_id': [
                r'report\s*(?:id|no|number)\s*:?\s*([A-Z0-9\-]+)',
                r'lab\s*no\s*:?\s*([A-Z0-9\-]+)',
                r'specimen\s*(?:id|no)\s*:?\s*([A-Z0-9\-]+)',
            ],
            'doctor': [
                r'(?:dr\.|doctor)\s*:?\s*([A-Za-z\s\.]+)',
                r'referred\s*by\s*:?\s*(?:dr\.|doctor)?\s*([A-Za-z\s\.]+)',
            ]
        }
    
    def extract_patient_info(self, text: str) -> Dict:
        """Extract patient information from report text"""
        text_lower = text.lower()
        
        patient_info = {
            'name': self._extract_name(text, text_lower),
            'age': self._extract_age(text_lower),
            'gender': self._extract_gender(text_lower),
            'report_date': self._extract_date(text_lower),
            'report_id': self._extract_report_id(text),
            'doctor': self._extract_doctor(text),
            'extracted_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return patient_info
    
    def _extract_name(self, text: str, text_lower: str) -> Optional[str]:
        """Extract patient name"""
        for pattern in self.patterns['name']:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                # Clean up and capitalize
                name = ' '.join([word.capitalize() for word in name.split()])
                # Remove common false matches
                if len(name) > 3 and not any(skip in name.lower() for skip in ['test', 'report', 'lab', 'blood', 'sample']):
                    return name
        return None
    
    def _extract_age(self, text_lower: str) -> Optional[int]:
        """Extract patient age"""
        for pattern in self.patterns['age']:
            match = re.search(pattern, text_lower)
            if match:
                try:
                    age = int(match.group(1))
                    if 0 < age < 120:  # Reasonable age range
                        return age
                except:
                    continue
        return None
    
    def _extract_gender(self, text_lower: str) -> Optional[str]:
        """Extract patient gender"""
        for pattern in self.patterns['gender']:
            match = re.search(pattern, text_lower)
            if match:
                gender = match.group(1).strip().lower()
                if gender in ['m', 'male']:
                    return 'Male'
                elif gender in ['f', 'female']:
                    return 'Female'
        return None
    
    def _extract_date(self, text_lower: str) -> Optional[str]:
        """Extract report date"""
        for pattern in self.patterns['date']:
            match = re.search(pattern, text_lower)
            if match:
                date_str = match.group(1).strip()
                try:
                    # Try to parse and format date
                    for fmt in ['%d-%m-%Y', '%d/%m/%Y', '%d-%m-%y', '%d/%m/%y']:
                        try:
                            date_obj = datetime.strptime(date_str, fmt)
                            return date_obj.strftime('%Y-%m-%d')
                        except:
                            continue
                    return date_str  # Return as-is if can't parse
                except:
                    continue
        return None
    
    def _extract_report_id(self, text: str) -> Optional[str]:
        """Extract report ID"""
        for pattern in self.patterns['report_id']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                report_id = match.group(1).strip()
                if len(report_id) > 2:
                    return report_id.upper()
        return None
    
    def _extract_doctor(self, text: str) -> Optional[str]:
        """Extract referring doctor name"""
        for pattern in self.patterns['doctor']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                doctor = match.group(1).strip()
                doctor = ' '.join([word.capitalize() for word in doctor.split()])
                if len(doctor) > 3:
                    return doctor
        return None
    
    def format_patient_card(self, patient_info: Dict) -> str:
        """Format patient info for display"""
        info_parts = []
        
        if patient_info.get('name'):
            info_parts.append(f"**Name:** {patient_info['name']}")
        
        if patient_info.get('age'):
            info_parts.append(f"**Age:** {patient_info['age']} years")
        
        if patient_info.get('gender'):
            info_parts.append(f"**Gender:** {patient_info['gender']}")
        
        if patient_info.get('report_date'):
            info_parts.append(f"**Report Date:** {patient_info['report_date']}")
        
        if patient_info.get('report_id'):
            info_parts.append(f"**Report ID:** {patient_info['report_id']}")
        
        if patient_info.get('doctor'):
            info_parts.append(f"**Referred By:** Dr. {patient_info['doctor']}")
        
        return " | ".join(info_parts) if info_parts else "Patient information not found"
