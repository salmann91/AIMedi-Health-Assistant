import pytesseract
from PIL import Image
import cv2
import numpy as np
from pdf2image import convert_from_path
import os
from typing import Optional, List
import tempfile

class OCRProcessor:
    def __init__(self, tesseract_path: Optional[str] = None):
        self._set_tesseract_path(tesseract_path)

    def _set_tesseract_path(self, tesseract_path: Optional[str] = None):
        """Set tesseract path - called at init and before each OCR operation"""
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
            return
        # Try common Windows installation paths
        if os.name == 'nt':
            common_paths = [
                r'C:\Program Files\Tesseract-OCR\tesseract.exe',
                r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
                r'C:\Users\{}\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'.format(os.getenv('USERNAME'))
            ]
            for path in common_paths:
                if os.path.exists(path):
                    pytesseract.pytesseract.tesseract_cmd = path
                    print(f"Tesseract found at: {path}")
                    return
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for better OCR results"""
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()

        # Upscale small images
        height, width = gray.shape
        if height < 1500 or width < 1500:
            scale = max(1500 / height, 1500 / width)
            gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

        # Denoise
        gray = cv2.fastNlMeansDenoising(gray, h=10)

        # Sharpen
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        gray = cv2.filter2D(gray, -1, kernel)

        # Otsu binarization (better than adaptive for printed reports)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return thresh
    
    def extract_text_from_image(self, image_path: str) -> str:
        """Extract text from image file"""
        self._set_tesseract_path()  # Re-set path before every OCR call
        try:
            print(f"Loading image from: {image_path}")
            
            # Try multiple methods to load the image
            img = None
            
            # Method 1: OpenCV
            img = cv2.imread(image_path)
            
            # Method 2: PIL if OpenCV fails
            if img is None:
                print("OpenCV failed, trying PIL...")
                pil_img = Image.open(image_path)
                img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
            
            if img is None:
                print("Failed to load image!")
                return ""
            
            print(f"Image loaded: {img.shape}")
            
            results = []

            # Strategy 1: preprocessed (Otsu)
            processed = self.preprocess_image(img)
            results.append(pytesseract.image_to_string(processed, config='--psm 6 --oem 3'))

            # Strategy 2: grayscale only
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
            results.append(pytesseract.image_to_string(gray, config='--psm 6 --oem 3'))

            # Strategy 3: original colour image
            results.append(pytesseract.image_to_string(img, config='--psm 6 --oem 3'))

            # Strategy 4: psm 4 (single column)
            results.append(pytesseract.image_to_string(processed, config='--psm 4 --oem 3'))

            # Pick longest result
            text = max(results, key=len)
            print(f"Best OCR result length: {len(text)} chars")
            print(f"OCR text preview:\n{text[:500]}")
            return text
            
        except Exception as e:
            print(f"Error in image OCR: {e}")
            import traceback
            traceback.print_exc()
            return ""
    
    def extract_text_from_pdf_images(self, pdf_path: str) -> str:
        """Extract text from scanned PDF by converting to images"""
        self._set_tesseract_path()  # Re-set path before every OCR call
        try:
            # Convert PDF to images
            images = convert_from_path(pdf_path, dpi=300)
            
            all_text = []
            for i, image in enumerate(images):
                # Convert PIL Image to numpy array
                img_array = np.array(image)
                
                # Convert RGB to BGR (OpenCV format)
                img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                
                # Preprocess
                processed = self.preprocess_image(img_bgr)
                
                # Extract text
                text = pytesseract.image_to_string(processed, config='--psm 6')
                all_text.append(text)
            
            return "\n\n".join(all_text)
        except Exception as e:
            print(f"Error in PDF OCR: {e}")
            import traceback
            traceback.print_exc()
            return ""
    
    def process_uploaded_file(self, file_path: str, file_type: str) -> str:
        """
        Process uploaded file (image or PDF)
        file_type: 'image' or 'pdf'
        """
        if file_type == 'image':
            return self.extract_text_from_image(file_path)
        elif file_type == 'pdf':
            return self.extract_text_from_pdf_images(file_path)
        else:
            return ""
    
    def is_scanned_pdf(self, text: str) -> bool:
        """Check if PDF appears to be scanned (has little/no text)"""
        # If extracted text is very short or empty, likely scanned
        clean_text = text.strip()
        return len(clean_text) < 100  # Threshold for minimal text
