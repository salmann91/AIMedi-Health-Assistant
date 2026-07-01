import pdfplumber
import re
from typing import Dict, List, Optional, Tuple
import os
import sys

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
            'hemoglobin': ['hemoglobin', 'haemoglobin', 'hb ', 'hb-', 'hb(', 'hgb'],
            'hba1c': ['hba1c', 'hba lc', 'hba-1c', 'hba 1c', 'glycated hemoglobin', 'glycosylated hemoglobin', 'glycohemoglobin'],
            'glucose': ['glucose', 'blood sugar', 'fasting glucose', 'fasting blood sugar', 'fbs', 'rbs', 'ppbs', 'random blood sugar', 'random glucose', 'blood glucose'],
            'cholesterol': ['total cholesterol', 't. cholesterol', 'cholesterol total', 'serum cholesterol', 'cholesterol'],
            'ldl': ['ldl', 'ldl cholesterol', 'ldl-c', 'low density lipoprotein'],
            'hdl': ['hdl', 'hdl cholesterol', 'hdl-c', 'high density lipoprotein'],
            'triglycerides': ['triglycerides', 'triglyceride', 'serum triglycerides', 'tg ', 'tgl'],
            'rbc': ['rbc', 'red blood cell', 'red cell count', 'erythrocyte', 'r.b.c'],
            'wbc': ['wbc', 'white blood cell', 'total wbc', 'total leucocyte', 'tlc', 'leukocyte', 'w.b.c'],
            'platelets': ['platelets', 'platelet count', 'platelet', 'thrombocyte', 'plt'],
            'creatinine': ['creatinine', 'serum creatinine', 's. creatinine', 's.creatinine', 'creat'],
            'bun': ['bun', 'blood urea nitrogen', 'blood urea', 'serum urea', 'urea nitrogen', 'urea'],
            'vitamin_d': ['vitamin d', 'vit d', '25-hydroxy vitamin d', '25-oh vitamin d', '25(oh)d', 'vitamin d3'],
            'tsh': ['tsh', 'thyroid stimulating hormone', 't.s.h'],
            't3': ['t3', 'triiodothyronine', 'total t3', 'serum t3'],
            't4': ['t4', 'thyroxine', 'total t4', 'serum t4'],
            'alt': ['alt', 'sgpt', 'alanine aminotransferase', 'alanine transaminase', 's.g.p.t'],
            'ast': ['ast', 'sgot', 'aspartate aminotransferase', 'aspartate transaminase', 's.g.o.t']
        }
        
        # Initialize OCR if available
        self.ocr_processor = OCRProcessor() if OCR_AVAILABLE else None
        
        # Initialize patient info extractor
        self.patient_extractor = PatientInfoExtractor() if PatientInfoExtractor else None
    
    def extract_from_pdf(self, pdf_path: str, use_ocr: bool = False) -> Dict:
        """Extract data from PDF, with optional OCR for scanned documents"""
        text = ""
        
        try:
            # Try standard text extraction first
            if not use_ocr:
                with pdfplumber.open(pdf_path) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text() or ""
                        text += page_text
            
            # If text is minimal or use_ocr is True, try OCR
            if (use_ocr or (self.ocr_processor and len(text.strip()) < 100)) and self.ocr_processor:
                print("Using OCR to extract text from scanned PDF...")
                ocr_text = self.ocr_processor.extract_text_from_pdf_images(pdf_path)
                if ocr_text:
                    text = ocr_text
                    print(f"OCR extracted {len(text)} characters")
            
            # Debug output
            if text:
                print(f"Total text extracted: {len(text)} characters")
                print(f"First 500 chars: {text[:500]}")
            
            # Extract parameters
            parameters = self._parse_text(text)
            
            # Ensure we return a dict - unwrap tuples
            if isinstance(parameters, tuple):
                print(f"Warning: _parse_text returned tuple, converting to dict")
                # Try to find dict in tuple
                for item in parameters:
                    if isinstance(item, dict):
                        parameters = item
                        break
                else:
                    parameters = {}
            elif not isinstance(parameters, dict):
                print(f"Warning: _parse_text returned {type(parameters)}, converting to dict")
                parameters = {} if parameters is None else dict(parameters) if isinstance(parameters, (list, tuple)) else {}
            
            return parameters
        except Exception as e:
            print(f"Error extracting from PDF: {e}")
            import traceback
            traceback.print_exc()
            return {}
    
    def extract_from_image(self, image_path: str) -> Dict:
        """Extract data from image file using OCR"""
        if not self.ocr_processor:
            print("OCR processor not available")
            return {}
        
        try:
            print(f"Extracting text from image: {image_path}")
            text = self.ocr_processor.extract_text_from_image(image_path)
            
            # Debug output
            if text:
                print(f"OCR extracted {len(text)} characters")
                print(f"Full OCR text:\n{text}")
            else:
                print("No text extracted from image!")
            
            # Store for external access (patient info extraction)
            self._last_ocr_text = text
            
            # Extract parameters
            parameters = self._parse_text(text)
            print(f"Extracted parameters: {list(parameters.keys()) if isinstance(parameters, dict) else 'N/A'}")
            
            # Ensure we return a dict - unwrap tuples
            if isinstance(parameters, tuple):
                print(f"Warning: _parse_text returned tuple, converting to dict")
                # Try to find dict in tuple
                for item in parameters:
                    if isinstance(item, dict):
                        parameters = item
                        break
                else:
                    parameters = {}
            elif not isinstance(parameters, dict):
                print(f"Warning: _parse_text returned {type(parameters)}, converting to dict")
                parameters = {} if parameters is None else dict(parameters) if isinstance(parameters, (list, tuple)) else {}
            
            return parameters
        except Exception as e:
            print(f"Error extracting from image: {e}")
            import traceback
            traceback.print_exc()
            return {}
    
    def _parse_text(self, text: str) -> Dict:
        """Parse text to extract blood parameters - Enhanced OCR handling"""
        results = {}
        
        if not text or not isinstance(text, str):
            print(f"Warning: text is not a string or is empty. Type: {type(text)}")
            return results
        
        try:
            # Clean OCR text first
            text = self._clean_ocr_text(text)
            
            # Convert to lowercase for searching
            text_lower = text.lower()
            
            # Method 1: Line-by-line parsing (for well-formatted reports)
            lines = text_lower.split('\n')
            for line in lines:
                # Skip empty lines and headers
                if len(line.strip()) < 3:
                    continue
                    
                for param_key, keywords in self.parameters.items():
                    if param_key in results:  # Already found this parameter
                        continue
                    # Check if any keyword matches
                    if any(keyword in line for keyword in keywords):
                        value = self._extract_value(line)
                        if value is not None:
                            results[param_key] = {
                                'value': value,
                                'unit': self._extract_unit(line),
                                'raw_text': line.strip()
                            }
                            print(f"Found {param_key}: {value} from line: {line[:80]}")
                            break  # Move to next line after finding a param
            
            # Method 2: Paragraph-based extraction (for poorly formatted OCR)
            if len(results) < 3:  # If we found very few parameters, try alternate method
                print("Using paragraph-based extraction for better OCR matching...")
                paragraphs = text_lower.split('\n\n')
                for para in paragraphs:
                    para = para.replace('\n', ' ')  # Combine multi-line paragraphs
                    for param_key, keywords in self.parameters.items():
                        if param_key in results:  # Already found this parameter
                            continue
                        for keyword in keywords:
                            if keyword in para:
                                # Find numbers near the keyword
                                # Get the substring containing the keyword and nearby text
                                idx = para.find(keyword)
                                context = para[max(0, idx-50):min(len(para), idx+100)]
                                value = self._extract_value(context)
                                if value is not None:
                                    results[param_key] = {
                                        'value': value,
                                        'unit': self._extract_unit(context),
                                        'raw_text': context.strip()
                                    }
                                    print(f"Found {param_key}: {value} from context: {context[:80]}")
                                    break
        except Exception as e:
            print(f"Error in _parse_text: {e}")
            import traceback
            traceback.print_exc()
        
        return results
    
    def _clean_ocr_text(self, text: str) -> str:
        """Clean OCR extracted text to improve parameter detection"""
        if not text:
            return text

        # Normalize whitespace (preserve newlines for line-by-line parsing)
        text = re.sub(r'[ \t]+', ' ', text)

        # Fix "hba lc" -> "hba1c" (common OCR split)
        text = re.sub(r'hba\s+lc', 'hba1c', text, flags=re.IGNORECASE)

        # Fix numbers split by spaces like "1 2 . 3" -> "12.3"
        text = re.sub(r'(\d)\s+(\d)', r'\1\2', text)

        return text
    
    def _extract_value(self, text: str) -> Optional[float]:
        """Extract numeric value from text - Enhanced for OCR"""
        if not text:
            return None
        
        # Multiple patterns to handle different formats
        patterns = [
            r'(\d+\.?\d*)\s*(?:mg/dl|g/dl|%|mmol/l|cells|/cmm|/μl|u/l|iu/ml)',  # With units
            r':\s*(\d+\.?\d*)',  # After colon
            r'(\d+\.?\d*)\s*-\s*\d+\.?\d*',  # Range format: 120-150
            r'<\s*(\d+\.?\d*)',  # Less than format
            r'>\s*(\d+\.?\d*)',  # Greater than format
            r'\s+(\d+\.?\d*)\s+',  # Surrounded by spaces
            r'\b(\d+\.?\d*)\b',  # Any number (last resort)
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            if matches:
                for match in matches:
                    try:
                        value = float(match)
                        # Filter out unrealistic values (too small or too large)
                        if 0.001 < value < 100000:  # Reasonable range (TSH can be 0.01, platelets can be 500000)
                            return value
                    except (ValueError, IndexError):
                        continue
        
        return None
    
    def _extract_unit(self, text: str) -> str:
        units = ['mg/dl', 'g/dl', '%', 'mmol/l', 'μiu/ml', 'ng/ml', 'cells/μl', 'u/l']
        for unit in units:
            if unit in text:
                return unit
        return ""
