import pdfplumber
import re
from typing import Dict, List, Optional

# Import OCR processor
try:
    from .ocr_processor import OCRProcessor
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    print("OCR not available. Install pytesseract and pdf2image for image support.")

# Import patient info extractor
try:
    from .patient_info import PatientInfoExtractor
except ImportError:
    PatientInfoExtractor = None

class BloodReportExtractor:
    def __init__(self):
        self.parameters = {
            'hemoglobin': ['hemoglobin', 'haemoglobin', 'hb', 'hgb'],
            'hba1c': ['hba1c', 'hba lc', 'hba-1c', 'hba 1c', 'glycated hemoglobin', 'glycohemoglobin'],
            'glucose': ['glucose', 'blood sugar', 'fasting glucose', 'fasting blood sugar', 'fbs', 'rbs', 'ppbs', 'random glucose', 'blood glucose'],
            'cholesterol': ['total cholesterol', 'cholesterol total', 'serum cholesterol', 'cholesterol'],
            'ldl': ['ldl', 'ldl cholesterol', 'ldl-c', 'low density lipoprotein'],
            'hdl': ['hdl', 'hdl cholesterol', 'hdl-c', 'high density lipoprotein'],
            'triglycerides': ['triglycerides', 'triglyceride', 'serum triglycerides', 'tg', 'tgl'],
            'rbc': ['rbc', 'red blood cell', 'red cell count', 'erythrocyte', 'r.b.c'],
            'wbc': ['wbc', 'white blood cell', 'total wbc', 'total leucocyte', 'tlc', 'leukocyte', 'w.b.c'],
            'platelets': ['platelets', 'platelet count', 'platelet', 'plt'],
            'creatinine': ['creatinine', 'serum creatinine', 's. creatinine', 's.creatinine', 'creat'],
            'bun': ['bun', 'blood urea nitrogen', 'blood urea', 'urea nitrogen', 'urea'],
            'vitamin_d': ['vitamin d', 'vit d', '25-hydroxy vitamin d', '25-oh vitamin d', '25(oh)d', 'vitamin d3'],
            'tsh': ['tsh', 'thyroid stimulating hormone', 't.s.h'],
            't3': ['t3', 'triiodothyronine', 'total t3', 'serum t3'],
            't4': ['t4', 'thyroxine', 'total t4', 'serum t4'],
            'alt': ['alt', 'sgpt', 'alanine aminotransferase', 'alanine transaminase', 's.g.p.t'],
            'ast': ['ast', 'sgot', 'aspartate aminotransferase', 'aspartate transaminase', 's.g.o.t']
        }

        self.ocr_processor = OCRProcessor() if OCR_AVAILABLE else None
        self.patient_extractor = PatientInfoExtractor() if PatientInfoExtractor else None
        self._last_extracted_text = ""
        self._last_ocr_text = ""

    def extract_text_from_pdf(self, pdf_path: str, use_ocr: bool = False) -> str:
        text = ""
        try:
            if not use_ocr:
                with pdfplumber.open(pdf_path) as pdf:
                    text = "\n".join(page.extract_text() or "" for page in pdf.pages)

            if (use_ocr or (self.ocr_processor and len(text.strip()) < 100)) and self.ocr_processor:
                ocr_text = self.ocr_processor.extract_text_from_pdf_images(pdf_path)
                if ocr_text:
                    text = ocr_text
                    self._last_ocr_text = text

            self._last_extracted_text = text
            return text
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return ""

    def extract_from_pdf(self, pdf_path: str, use_ocr: bool = False) -> Dict:
        text = self.extract_text_from_pdf(pdf_path, use_ocr=use_ocr)
        return self._parse_text(text)

    def extract_from_image(self, image_path: str) -> Dict:
        if not self.ocr_processor:
            print("OCR processor not available")
            return {}

        text = self.ocr_processor.extract_text_from_image(image_path)
        self._last_extracted_text = text
        self._last_ocr_text = text
        return self._parse_text(text)

    def _parse_text(self, text: str) -> Dict:
        results = {}

        if not text or not isinstance(text, str):
            return results

        text = self._clean_ocr_text(text)
        lines = text.split('\n')

        for line in lines:
            if len(line.strip()) < 3:
                continue
            normalized_line = self._normalize_text_for_matching(line)
            for param_key, keywords in self.parameters.items():
                if param_key in results:
                    continue
                if self._line_matches_keywords(normalized_line, keywords):
                    value = self._extract_value(line)
                    if value is not None:
                        results[param_key] = {
                            'value': value,
                            'unit': self._extract_unit(line),
                            'raw_text': line.strip()
                        }
                        break

        if len(results) < 3:
            paragraphs = [p for p in text.split('\n\n') if len(p.strip()) > 3]
            for para in paragraphs:
                normalized_para = self._normalize_text_for_matching(para.replace('\n', ' '))
                for param_key, keywords in self.parameters.items():
                    if param_key in results:
                        continue
                    if self._line_matches_keywords(normalized_para, keywords):
                        value = self._extract_value(para)
                        if value is not None:
                            results[param_key] = {
                                'value': value,
                                'unit': self._extract_unit(para),
                                'raw_text': para.strip()
                            }
                            break

        return results

    def _normalize_text_for_matching(self, text: str) -> str:
        if not text:
            return ""
        text = text.lower()
        text = re.sub(r'[^a-z0-9]+', ' ', text)
        return re.sub(r'\s+', ' ', text).strip()

    def _line_matches_keywords(self, text: str, keywords: List[str]) -> bool:
        normalized_keywords = [self._normalize_text_for_matching(keyword) for keyword in keywords if keyword]
        return any(keyword and keyword in text for keyword in normalized_keywords)

    def _clean_ocr_text(self, text: str) -> str:
        if not text:
            return text
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r'hba\s+lc', 'hba1c', text, flags=re.IGNORECASE)
        text = re.sub(r'(\d)\s+(\d)', r'\1\2', text)
        return text

    def _extract_value(self, text: str) -> Optional[float]:
        if not text:
            return None
        if re.search(r'\d+\s*[-–]\s*\d+', text):
            text = re.sub(r'\d+\s*[-–]\s*\d+', ' ', text)

        patterns = [
            r'(\d+\.?\d*)\s*(?:mg/dl|g/dl|%|mmol/l|cells/μl|/cmm|/μl|u/l|iu/ml|ng/dl|ng/ml|μiu/ml)',
            r'[:=]\s*(\d+\.?\d*)',
            r'<\s*(\d+\.?\d*)',
            r'>\s*(\d+\.?\d*)',
            r'\b(\d+\.?\d*)\b'
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text, flags=re.IGNORECASE)
            if matches:
                for match in matches:
                    try:
                        value = float(match)
                        if 0.001 < value < 100000:
                            return value
                    except (ValueError, IndexError):
                        continue
        return None

    def _extract_unit(self, text: str) -> str:
        units = ['mg/dl', 'g/dl', '%', 'mmol/l', 'μiu/ml', 'ng/ml', 'ng/dl', 'cells/μl', 'u/l']
        lower_text = text.lower()
        for unit in units:
            if unit in lower_text:
                return unit
        return ""
