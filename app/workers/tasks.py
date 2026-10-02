from app.workers.celery_app import celery_app


@celery_app.task
def process_sighting(sighting_id: int) -> dict:
    return {
        "sighting_id": sighting_id,
        "status": "processed",
    }