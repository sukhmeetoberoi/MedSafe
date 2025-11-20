"""
OCR Service for extracting text from medical reports
Supports PDFs, images, and scanned documents
"""

import os
import io
import cv2
import numpy as np
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
from typing import Optional, List, Dict, Any
import fitz  # PyMuPDF for PDF processing
from core.logging import logger
from core.config import settings

# Configure Tesseract
if settings.TESSERACT_CMD:
    pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD

class OCRService:
    """Service for OCR text extraction from medical documents"""

    def __init__(self):
        self.supported_formats = ['.pdf', '.jpg', '.jpeg', '.png', '.tiff', '.tif']

    async def extract_text_from_file(self, file_path: str) -> Dict[str, Any]:
        """
        Extract text from uploaded file

        Args:
            file_path: Path to the uploaded file

        Returns:
            Dictionary containing extracted text and metadata
        """
        try:
            file_ext = os.path.splitext(file_path)[1].lower()

            if file_ext not in self.supported_formats:
                raise ValueError(f"Unsupported file format: {file_ext}")

            if file_ext == '.pdf':
                return await self._extract_from_pdf(file_path)
            else:
                return await self._extract_from_image(file_path)

        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {e}")
            raise

    async def _extract_from_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """Extract text from PDF file using PyMuPDF and OCR as fallback"""
        try:
            doc = fitz.open(pdf_path)
            extracted_text = []
            pages_metadata = []

            for page_num in range(len(doc)):
                page = doc[page_num]

                # First try to extract text directly
                text = page.get_text()

                if not text.strip():
                    # If no text found, try OCR on the page image
                    pix = page.get_pixmap()
                    img_data = pix.tobytes("png")
                    image = Image.open(io.BytesIO(img_data))
                    text = await self._ocr_image(image)

                extracted_text.append(text)
                pages_metadata.append({
                    "page_number": page_num + 1,
                    "text_length": len(text),
                    "has_text": bool(text.strip())
                })

            doc.close()

            return {
                "text": "\n\n".join(extracted_text),
                "pages_count": len(extracted_text),
                "total_characters": sum(len(text) for text in extracted_text),
                "pages_metadata": pages_metadata,
                "extraction_method": "direct_text_with_ocr_fallback"
            }

        except Exception as e:
            logger.error(f"Error processing PDF {pdf_path}: {e}")
            raise

    async def _extract_from_image(self, image_path: str) -> Dict[str, Any]:
        """Extract text from image file using OCR"""
        try:
            image = Image.open(image_path)
            text = await self._ocr_image(image)

            return {
                "text": text,
                "pages_count": 1,
                "total_characters": len(text),
                "pages_metadata": [{
                    "page_number": 1,
                    "text_length": len(text),
                    "has_text": bool(text.strip())
                }],
                "extraction_method": "ocr_only"
            }

        except Exception as e:
            logger.error(f"Error processing image {image_path}: {e}")
            raise

    async def _ocr_image(self, image: Image.Image) -> str:
        """
        Perform OCR on a PIL Image object with preprocessing
        """
        try:
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')

            # Preprocess the image for better OCR accuracy
            processed_image = self._preprocess_image(image)

            # Configure Tesseract for medical documents
            custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ.,;:!?()[]{}"\'+-/=%&@#$*<>\n\s'

            # Extract text
            text = pytesseract.image_to_string(
                processed_image,
                config=custom_config,
                lang='eng'
            )

            # Clean up the text
            cleaned_text = self._clean_extracted_text(text)

            return cleaned_text

        except Exception as e:
            logger.error(f"Error during OCR processing: {e}")
            raise

    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Preprocess image to improve OCR accuracy
        """
        # Convert to OpenCV format
        img_array = np.array(image)

        # Convert to grayscale
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array

        # Apply adaptive thresholding for better text extraction
        binary = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )

        # Noise reduction
        denoised = cv2.medianBlur(binary, 3)

        # Convert back to PIL Image
        processed_image = Image.fromarray(denoised)

        # Enhance contrast
        enhancer = ImageEnhance.Contrast(processed_image)
        processed_image = enhancer.enhance(2.0)

        # Enhance sharpness
        enhancer = ImageEnhance.Sharpness(processed_image)
        processed_image = enhancer.enhance(1.5)

        return processed_image

    def _clean_extracted_text(self, text: str) -> str:
        """
        Clean and normalize extracted text
        """
        if not text:
            return ""

        # Remove excessive whitespace
        cleaned = ' '.join(text.split())

        # Remove common OCR artifacts
        artifacts = [
            '|', 'I', 'l', '1',  # Common character confusions
            '•', '·',          # Bullet points
            '□', '■',          # Box characters
            '→', '←',          # Arrows
        ]

        for artifact in artifacts:
            cleaned = cleaned.replace(artifact, '')

        # Fix common medical term OCR errors
        replacements = {
            'rn': 'm',
            'cl': 'd',
            'vv': 'w',
            '0O': 'Q',
            '8B': 'B'
        }

        for old, new in replacements.items():
            cleaned = cleaned.replace(old, new)

        return cleaned.strip()

    async def extract_medical_fields(self, text: str) -> Dict[str, Any]:
        """
        Extract common medical fields from OCR text
        """
        medical_patterns = {
            "patient_name": r"Patient:?\s*([A-Za-z\s]+)",
            "date_of_birth": r"DOB:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
            "date": r"Date:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
            "patient_id": r"Patient ID:?\s*([A-Za-z0-9-]+)",
            "physician": r(?:Physician|Doctor|Dr\.?):?\s*([A-Za-z\s\.]+)",
            "diagnosis": r"(?:Diagnosis|Assessment):?\s*([^.\n]+)",
            "medications": r"(?:Medications|Drugs|Rx):?\s*([^.\n]+)",
            "allergies": r"(?:Allergies|Allergy):?\s*([^.\n]+)"
        }

        import re
        extracted_fields = {}

        for field, pattern in medical_patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                extracted_fields[field] = match.group(1).strip()

        return {
            "extracted_fields": extracted_fields,
            "confidence": len(extracted_fields) / len(medical_patterns)
        }

# Singleton instance
ocr_service = OCRService()