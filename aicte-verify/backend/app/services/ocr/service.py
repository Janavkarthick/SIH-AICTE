"""OCR and Document Text Extraction Service.

Extracts native digital text and OCR text from PDF documents and scanned images.
Implements OpenCV preprocessing (grayscale, denoise, threshold, deskew) and multi-language
Tesseract support (eng+tam+hin) with automatic fallback.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import cv2
try:
    import fitz  # PyMuPDF
    HAS_FITZ = True
except ImportError:
    fitz = None
    HAS_FITZ = False
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import pytesseract
import pypdf


class OCRService:
    """Provides high-accuracy document OCR, layout block segmentation, and page rendering."""

    def __init__(self):
        # Default languages supported
        self.default_lang = "eng+tam+hin"
        self.fallback_lang = "eng"

    def preprocess_image(self, img_bgr: np.ndarray) -> np.ndarray:
        """Preprocess an image for OCR: grayscale, denoise, threshold, and deskew."""
        # 1. Grayscale
        if len(img_bgr.shape) == 3:
            gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        else:
            gray = img_bgr

        # 2. Denoise
        denoised = cv2.GaussianBlur(gray, (3, 3), 0)

        # 3. Threshold (Otsu binarization)
        _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # 4. Deskew
        try:
            coords = np.column_stack(np.where(thresh == 0))
            if len(coords) > 50:
                angle = cv2.minAreaRect(coords)[-1]
                if angle < -45:
                    angle = -(90 + angle)
                else:
                    angle = -angle
                if abs(angle) > 0.5 and abs(angle) < 45.0:
                    (h, w) = thresh.shape[:2]
                    center = (w // 2, h // 2)
                    m = cv2.getRotationMatrix2D(center, angle, 1.0)
                    thresh = cv2.warpAffine(
                        thresh, m, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE
                    )
        except Exception:
            pass  # Retain thresholded image if deskew fails

        return thresh

    def render_page_image(
        self,
        file_path: str,
        page_num: int = 1,
        output_path: Optional[str] = None,
        dpi: int = 150,
    ) -> str:
        """Render a single page of a PDF or load an image file and save as PNG."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if not output_path:
            out_dir = path.parent / "rendered_pages"
            out_dir.mkdir(parents=True, exist_ok=True)
            output_path = str(out_dir / f"{path.stem}_p{page_num}.png")

        if path.suffix.lower() == ".pdf":
            if HAS_FITZ and fitz:
                doc = fitz.open(str(path))
                if page_num < 1 or page_num > len(doc):
                    page_idx = 0
                else:
                    page_idx = page_num - 1

                page = doc.load_page(page_idx)
                zoom = dpi / 72.0
                mat = fitz.Matrix(zoom, zoom)
                pix = page.get_pixmap(matrix=mat, alpha=False)
                pix.save(output_path)
                doc.close()
            else:
                # Render canvas via Pillow
                img = Image.new("RGB", (800, 1100), color=(255, 255, 255))
                draw = ImageDraw.Draw(img)
                reader = pypdf.PdfReader(str(path))
                idx = max(0, min(page_num - 1, len(reader.pages) - 1))
                page_text = reader.pages[idx].extract_text() or ""
                y = 40
                for line in page_text.splitlines()[:45]:
                    draw.text((40, y), line[:80], fill=(20, 20, 20))
                    y += 22
                img.save(output_path)
        else:
            # Already an image, copy/normalize to PNG
            img = cv2.imread(str(path))
            if img is None:
                raise ValueError(f"Unable to read image at: {file_path}")
            cv2.imwrite(output_path, img)

        return output_path

    def _extract_native_pdf_blocks(
        self, doc: Any
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """Extract digital text and bounding blocks using native PyMuPDF."""
        full_text_parts = []
        blocks_data = []

        for page_idx, page in enumerate(doc):
            page_num = page_idx + 1
            # "blocks" format: (x0, y0, x1, y1, "text", block_no, block_type)
            page_blocks = page.get_text("blocks")
            for b in page_blocks:
                if len(b) >= 5 and b[4].strip():
                    text = b[4].strip()
                    bbox = [float(b[0]), float(b[1]), float(b[2] - b[0]), float(b[3] - b[1])]
                    blocks_data.append({
                        "page": page_num,
                        "text": text,
                        "bbox": bbox,
                        "confidence": 0.98,
                        "method": "native",
                    })
                    full_text_parts.append(text)

        return "\n".join(full_text_parts), blocks_data

    def _ocr_image_tesseract(
        self, img_bgr: np.ndarray, page_num: int = 1
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """Run OCR on preprocessed image using Tesseract with language fallbacks."""
        preprocessed = self.preprocess_image(img_bgr)
        pil_img = Image.fromarray(preprocessed)

        # Attempt multi-language first, fallback to English if pack not installed
        data = None
        for lang in [self.default_lang, self.fallback_lang]:
            try:
                data = pytesseract.image_to_data(
                    pil_img, lang=lang, output_type=pytesseract.Output.DICT
                )
                break
            except Exception:
                continue

        if not data:
            return "", []

        n_boxes = len(data["text"])
        blocks_data = []
        full_words = []

        for i in range(n_boxes):
            word = data["text"][i].strip()
            conf_str = data["conf"][i]
            try:
                conf = float(conf_str) / 100.0
            except (ValueError, TypeError):
                conf = 0.5

            if word and conf > 0.2:
                x, y, w, h = data["left"][i], data["top"][i], data["width"][i], data["height"][i]
                blocks_data.append({
                    "page": page_num,
                    "text": word,
                    "bbox": [float(x), float(y), float(w), float(h)],
                    "confidence": max(0.1, min(1.0, conf)),
                    "method": "ocr",
                })
                full_words.append(word)

        return " ".join(full_words), blocks_data

    def process_document(self, file_path: str) -> Dict[str, Any]:
        """Execute full extraction pipeline: PyMuPDF native first, fallback to Tesseract."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        extracted_text = ""
        blocks: List[Dict[str, Any]] = []
        method = "native"

        if path.suffix.lower() == ".pdf":
            try:
                if HAS_FITZ and fitz:
                    doc = fitz.open(str(path))
                    text, native_blocks = self._extract_native_pdf_blocks(doc)
                    if len(text.strip()) > 80:
                        extracted_text = text
                        blocks = native_blocks
                        method = "native"
                    else:
                        # Scanned PDF, render pages and run OCR
                        method = "ocr"
                        all_text = []
                        for page_idx, page in enumerate(doc):
                            page_num = page_idx + 1
                            pix = page.get_pixmap(dpi=150)
                            img_np = np.frombuffer(pix.samples, dtype=np.uint8).reshape(
                                pix.h, pix.w, pix.n
                            )
                            if pix.n == 4:
                                img_np = cv2.cvtColor(img_np, cv2.COLOR_RGBA2BGR)
                            elif pix.n == 1:
                                img_np = cv2.cvtColor(img_np, cv2.COLOR_GRAY2BGR)
                            else:
                                img_np = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

                            page_text, page_blocks = self._ocr_image_tesseract(img_np, page_num)
                            all_text.append(page_text)
                            blocks.extend(page_blocks)
                        extracted_text = "\n".join(all_text)
                    doc.close()
                else:
                    reader = pypdf.PdfReader(str(path))
                    all_text = []
                    for idx, page in enumerate(reader.pages):
                        page_num = idx + 1
                        page_text = page.extract_text() or ""
                        all_text.append(page_text)
                        for line in page_text.splitlines():
                            if line.strip():
                                blocks.append({
                                    "page": page_num,
                                    "text": line.strip(),
                                    "bbox": [50.0, 50.0, 400.0, 20.0],
                                    "confidence": 0.98,
                                    "method": "native",
                                })
                    extracted_text = "\n".join(all_text)
                    method = "native"
            except Exception as e:
                # Direct fallback
                method = "fallback_empty"
                extracted_text = f"Extraction note: {str(e)}"
        else:
            # Image file
            method = "ocr"
            img = cv2.imread(str(path))
            if img is not None:
                extracted_text, blocks = self._ocr_image_tesseract(img, page_num=1)

        return {
            "text": extracted_text,
            "blocks": blocks,
            "method": method,
            "total_blocks": len(blocks),
        }


# Singleton instance
ocr_service = OCRService()
