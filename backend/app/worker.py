from queue import Queue
from threading import Thread
from uuid import uuid4
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import or_
from database import SessionLocal
import models
import time
import pandas as pd
import torch
from ai import flatten_onehot_jsonb_fields, convert_image_blob_to_pil, run_model

# Global queue
submission_queue = Queue()

#Id2Label
id2label = {
 0: 'Eczema',
 1: 'Urticaria',
 2: 'Folliculitis',
 3: 'Psoriasis',
 4: 'Tinea',
 5: 'Acne',
 6: 'Tinea Versicolor',
 7: 'Stasis Dermatitis',
 8: 'Verruca vulgaris',
 9: 'Scar Condition',
 10: 'Seborrheic Dermatitis',
 11: 'Actinic Keratosis',
 12: 'SCC/SCCIS',
 13: 'SK/ISK',
 14: 'Basal Cell Carcinoma',
 15: 'Melanocytic Nevus',
 16: 'Hidradenitis',
 17: 'Cyst',
 18: 'Vitiligo',
 19: 'Melanoma'
}

# Worker function
def submission_worker():
    while True:
        submission_id = submission_queue.get()
        if submission_id is None:
            break
        try:
            time.sleep(1)
            process_submission(submission_id)
        except Exception as e:
            print(f"Error processing {submission_id}: {e}")
        finally:
            submission_queue.task_done()

# Processing logic
def process_submission(submission_id: str):

    db: Session = SessionLocal()

    submission = db.query(models.SubmissionQueue).filter_by(id=submission_id).first()

    if submission is None:
        db.close()
        return
    
    if submission.status != "IN QUEUE":
        db.close()
        return
    
    print(f"Processing submission: {submission.id}")
    
    df, image = get_submission_dataframe(submission_id, db)
    probs, image_bytes = run_model(df, image)
    result_id = save_result_to_db(db, image_bytes, probs)

    submission.status = "DONE" # type: ignore
    submission.result_id = result_id # type: ignore
    submission.completion_time = datetime.now(timezone.utc) # type: ignore
    db.commit()
    db.close()
    print(f"Completed processing for {submission.id}")


def save_result_to_db(db: Session, prediction_img_bytes: bytes, probs: list[float]):
    # Map probabilities to labels
    predictions = {id2label[i]: float(prob) for i, prob in enumerate(probs)}
    top_index = int(torch.tensor(probs).argmax().item())
    top_label = id2label[top_index]
    str_prediction = f"{top_label} - {probs[top_index]}"

    result = models.Result (
        id=uuid4(),
        report=prediction_img_bytes,
        raw_predictions=predictions,
        prediction=str_prediction
    )
    db.add(result)
    db.commit()
    db.refresh(result)

    return result.id

# On startup: enqueue unprocessed submissions
def preload_pending_submissions():
    db: Session = SessionLocal()
    pending = db.query(models.SubmissionQueue).filter(
    or_(
        models.SubmissionQueue.status == "IN QUEUE",
        models.SubmissionQueue.status == "PROCESSING"
    )
    ).all()
    for sub in pending:
        print(f"Enqueuing pending submission: {sub.id}")
        submission_queue.put(sub.id)
    db.close()

# Launch worker thread
def start_worker():
    preload_pending_submissions()
    print("Preloading pending tasks...")
    worker_thread = Thread(target=submission_worker, daemon=True)
    worker_thread.start()



def get_submission_dataframe(submission_id: str, db: Session):
    detail = (
        db.query(models.SubmissionDetail)
        .filter(models.SubmissionDetail.submission_id == submission_id)
        .first()
    )

    if not detail:
        raise ValueError("No submission detail found.")

    image_pil = convert_image_blob_to_pil(detail.image)

    row = {
        "weighted_skin_condition_label": {},  # if needed
        "age_group": detail.age_group,
        "sex_at_birth": detail.sex_at_birth,
        "condition_duration": detail.condition_duration,
    }

    row.update(flatten_onehot_jsonb_fields(detail))

    return pd.DataFrame([row]), image_pil
