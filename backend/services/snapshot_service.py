# import json
import logging

from pydantic import ValidationError

from core import teracyte_client as client
from core.database import insert_snapshot, get_latest_image_id #, get_snapshot
from services.image_processor import apply_canny_edges, is_valid_image
from models.schemas import ImagePayload, ResultsPayload

logger = logging.getLogger(__name__)

def fetch_and_store() -> tuple[ImagePayload, ResultsPayload] | None:
    """
    Pull the latest image + results from TeraCyte.
    If image_id is unchanged, returns None (caller skips update).
    Otherwise persists to DB and returns (ImagePayload, ResultsPayload).
    """
    try:
        image = client.get_image()
    except ValidationError as exc:
        logger.warning("Skipping poll - malformed image response from upstream: %s", exc)
        return None

    cached_id = get_latest_image_id()
    if image.image_id == cached_id:
        logger.debug("image_id unchanged (%s) - skipping", image.image_id)
        return None

    # Validate image data before doing anything with it
    if not is_valid_image(image.image_data_base64):
        logger.warning("Skipping snapshot %s - image data is incomplete or corrupt", image.image_id)
        return None

    try:
        results = client.get_results()
    except ValidationError as exc:
        logger.warning("Skipping snapshot %s - malformed results from upstream: %s", image.image_id, exc)
        return None

    # Reject unexpected histogram sizes
    if len(results.histogram) != 256:
        logger.warning("Skipping snapshot %s - histogram has %d bins, expected 256", image.image_id, len(results.histogram))
        return None

    # Results may not be ready yet for a freshly captured image
    if not results.is_complete():
        logger.warning("Skipping snapshot %s - results not ready yet", image.image_id)
        return None

    # Process image
    try:
        processed_b64 = apply_canny_edges(image.image_data_base64)
    except Exception as exc:
        logger.warning("Image processing failed: %s", exc)
        processed_b64 = None

    # Save to DB
    insert_snapshot(
        image_id=image.image_id,
        timestamp=image.timestamp,
        intensity_average=results.intensity_average,
        focus_score=results.focus_score,
        classification_label=results.classification_label,
        histogram=results.histogram,
        image_data_base64=image.image_data_base64,
        processed_data_base64=processed_b64,
    )
    logger.info("Snapshot saved: %s", image.image_id)

    return (
        ImagePayload(
            image_id=image.image_id,
            timestamp=image.timestamp,
            image_data_base64=image.image_data_base64,
            processed_data_base64=processed_b64,
        ),
        ResultsPayload(
            image_id=results.image_id,
            intensity_average=results.intensity_average,
            focus_score=results.focus_score,
            classification_label=results.classification_label,
            histogram=results.histogram,
        ),
    )

#? Scrapped the idea of a separate get_snapshot_by_id() endpoint for now, since the frontend can just use /history to fetch past snapshots
# def load_from_db(image_id: str) -> tuple[ImagePayload, ResultsPayload] | None:
#     """Return a previously stored snapshot by image_id."""
#     row = get_snapshot(image_id)
#     if not row:
#         return None
#     img = ImagePayload(
#         image_id=row.image_id,
#         timestamp=row.timestamp,
#         image_data_base64=row.image_data_base64,
#         processed_data_base64=row.processed_data_base64,
#     )
#     res = ResultsPayload(
#         image_id=row.image_id,
#         intensity_average=row.intensity_average,
#         focus_score=row.focus_score,
#         classification_label=row.classification_label,
#         histogram=json.loads(row.histogram_json or "[]"),
#     )
#     return img, res
