"""
api/data.py
Data endpoints: live poll, history, per-snapshot lookup, and aggregate stats.
All live data goes through snapshot_service which fetches, processes, and persists it.
"""
import json
import logging
from flask import Blueprint, jsonify, request
from core.teracyte_client import AuthError, UpstreamError
from core.database import get_history, get_stats
from services.snapshot_service import fetch_and_store #, load_from_db

logger = logging.getLogger(__name__)
data_bp = Blueprint("data", __name__, url_prefix="/api")

#? swapped with /poll to unify image + results retrieval, to avoid frontend inconsistencies
# @data_bp.get("/image")
# def get_image():
#     logger.info("getting image")
#     try:
#         result = fetch_and_store()
#         if result is None:
#             return jsonify({"status": "unchanged"}), 204
#         image, _ = result
#         return jsonify(image.model_dump()), 200
#     except AuthError as exc:
#         return jsonify({"error": str(exc)}), 401
#     except UpstreamError as exc:
#         return jsonify({"error": str(exc)}), exc.status
#     except Exception as exc:
#         logger.exception("Unexpected error in /api/image")
#         return jsonify({"error": str(exc)}), 500

# @data_bp.get("/results")
# def get_results():
#     try:
#         result = fetch_and_store()
#         if result is None:
#             return jsonify({"status": "unchanged"}), 204
#         _, results = result
#         return jsonify(results.model_dump()), 200
#     except AuthError as exc:
#         return jsonify({"error": str(exc)}), 401
#     except UpstreamError as exc:
#         return jsonify({"error": str(exc)}), exc.status
#     except Exception as exc:
#         logger.exception("Unexpected error in /api/results")
#         return jsonify({"error": str(exc)}), 500

@data_bp.get("/poll")
def poll():
    """Get polling endpoint that returns both image and results together, to ensure frontend consistency"""
    try:
        result = fetch_and_store()
        if result is None:
            return jsonify({"status": "unchanged"}), 204
        image, results = result
        return jsonify({
            "image": image.model_dump(),
            "results": results.model_dump(),
        }), 200
    except AuthError as exc:
        return jsonify({"error": str(exc), "code": "AUTH_ERROR"}), 401
    except UpstreamError as exc:
        return jsonify({"error": str(exc)}), exc.status
    except Exception as exc:
        logger.exception("Unexpected error in /api/poll")
        return jsonify({"error": str(exc)}), 500

@data_bp.get("/history")
def history():
    limit = min(int(request.args.get("limit", 50)), 200)
    rows = get_history(limit)
    items = [
        {
            "image_id":              r.image_id,
            "timestamp":             r.timestamp,
            "intensity_average":     r.intensity_average,
            "focus_score":           r.focus_score,
            "classification_label":  r.classification_label,
            "histogram":             json.loads(r.histogram_json or "[]"),
            "image_data_base64":     r.image_data_base64,
            "processed_data_base64": r.processed_data_base64,
        }
        for r in rows
    ]
    return jsonify(items), 200

#? data for the image already comes from history and saved locally, so this endpoint is not needed for now. Can be re-added later if we want to support fetching specific past snapshots by image_id
# @data_bp.get("/snapshot/<image_id>")
# def get_snapshot_by_id(image_id):
#     logger.info("Fetching snapshot for image_id: %s", image_id)
#     try:
#         result = load_from_db(image_id)
#         if result is None:
#             return jsonify({"error": f"Snapshot '{image_id}' not found"}), 404
#         image, results = result
#         return jsonify({
#             "image": image.model_dump(),
#             "results": results.model_dump(),
#         }), 200
#     except Exception as exc:
#         logger.exception("Unexpected error in /api/snapshot/%s", image_id)
#         return jsonify({"error": str(exc)}), 500

@data_bp.get("/stats")
def stats():
    return jsonify(get_stats()), 200
