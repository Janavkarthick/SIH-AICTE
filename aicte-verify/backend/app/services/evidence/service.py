"""Visual Evidence Package and Highlight Annotation Service.

Produces rendered document pages with highlighted bounding boxes around discrepancy zones,
along with blended Error Level Analysis (ELA) forensic heatmap overlays.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
import cv2
import numpy as np

from app.models.document import Document, ExtractedData
from app.services.forensics.service import forensics_service
from app.services.ocr.service import ocr_service


class EvidenceService:
    """Renders page visual evidence, overlays bounding boxes, and composites ELA heatmaps."""

    def build_evidence_view(
        self,
        document: Document,
        extracted_data: List[ExtractedData],
        page_num: int = 1,
        highlight_field: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate rendered base page image, annotated bounding box image, and ELA heatmap."""
        # 1. Render base page
        base_page_path = ocr_service.render_page_image(
            file_path=document.file_path, page_num=page_num
        )
        base_p = Path(base_page_path)
        out_dir = base_p.parent / "evidence_output"
        out_dir.mkdir(parents=True, exist_ok=True)

        annotated_path = str(out_dir / f"doc_{document.id}_p{page_num}_annotated.png")
        overlay_path = str(out_dir / f"doc_{document.id}_p{page_num}_ela_overlay.png")

        img = cv2.imread(base_page_path)
        if img is None:
            return {
                "document_id": document.id,
                "page_num": page_num,
                "error": "Failed to read rendered page image",
            }

        annotated_img = img.copy()
        annotations = []

        # 2. Draw bounding boxes for relevant fields
        for item in extracted_data:
            if item.page_number == page_num and item.bbox_json:
                try:
                    bbox = json.loads(item.bbox_json)
                    if len(bbox) == 4:
                        x, y, w, h = [int(v) for v in bbox]
                        is_target = highlight_field and (highlight_field.lower() in item.field_name.lower())
                        color = (0, 0, 255) if is_target else (0, 165, 255)  # Red for target, orange for others
                        cv2.rectangle(annotated_img, (x, y), (x + w, y + h), color, 2)
                        label = f"{item.field_name}: {item.field_value[:20] if item.field_value else ''}"
                        cv2.putText(
                            annotated_img,
                            label,
                            (x, max(15, y - 5)),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.4,
                            color,
                            1,
                        )
                        annotations.append({
                            "field_name": item.field_name,
                            "field_value": item.field_value,
                            "bbox": bbox,
                            "confidence": item.confidence,
                        })
                except Exception:
                    continue

        cv2.imwrite(annotated_path, annotated_img)

        # 3. Generate ELA heatmap and blend with base image
        try:
            ela_raw_path = forensics_service.generate_ela_heatmap(base_page_path)
            ela_img = cv2.imread(ela_raw_path)
            if ela_img is not None:
                # Resize if dimensions differ
                if ela_img.shape[:2] != img.shape[:2]:
                    ela_img = cv2.resize(ela_img, (img.shape[1], img.shape[0]))
                blended = cv2.addWeighted(img, 0.5, ela_img, 0.5, 0)
                cv2.imwrite(overlay_path, blended)
        except Exception:
            overlay_path = None

        return {
            "document_id": document.id,
            "document_type": document.document_type,
            "page_num": page_num,
            "base_image_path": base_page_path,
            "annotated_image_path": annotated_path,
            "ela_overlay_path": overlay_path,
            "annotations": annotations,
            "metadata": {
                "total_annotations": len(annotations),
                "is_current": document.is_current,
                "version": document.version,
            },
        }


# Singleton instance
evidence_service = EvidenceService()
