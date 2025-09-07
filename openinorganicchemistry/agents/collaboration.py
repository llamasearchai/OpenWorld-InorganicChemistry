from __future__ import annotations

import logging
import json
import os
from fastapi import WebSocket
from ..core.storage import RunRecord, load_run, save_run
import uuid
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)

def share_run(run_id: str, collaborator_email: str) -> str:
    """Share a run with collaborator via email notification and JSON export."""
    logger.info("Sharing run %s with %s", run_id, collaborator_email)
    try:
        record = load_run(run_id)
        if not record:
            raise ValueError(f"Run {run_id} not found")
        json_data = record.__dict__
        json_path = f"shared/{run_id}.json"
        os.makedirs(os.path.dirname(json_path), exist_ok=True)
        with open(json_path, "w") as f:
            json.dump(json_data, f, indent=4)
        # Email notification (demo, use env for smtp)
        msg = MIMEMultipart()
        msg['From'] = 'oic@local'
        msg['To'] = collaborator_email
        msg['Subject'] = f"Shared OIC Run {run_id}"
        msg.attach(MIMEText(f"Run shared: {json_path}"))
        # Placeholder no-op email sending for tests; integrate real SMTP in production
        output = f"Run {run_id} shared with {collaborator_email}, JSON: {json_path}"
        logger.info("Share completed")
    except Exception as e:
        logger.error("Share failed", exc_info=True)
        raise ValueError(f"Failed to share run {run_id}. Error: {e}") from e
    print("\n=== Collaboration Share Result ===\n")
    print(output)
    share_id = str(uuid.uuid4())
    save_run(
        RunRecord(
            id=share_id,
            kind="collaboration",
            input=run_id,
            output=output,
            meta={"collaborator": collaborator_email, "shared_file": json_path}
        )
    )
    print(f"\n[share_id] {share_id}")
    return share_id

async def websocket_share(websocket: WebSocket, run_id: str):
    """Real-time sharing via WebSocket."""
    await websocket.accept()
    record = load_run(run_id)
    if record:
        await websocket.send_text(json.dumps(record.__dict__))
        logger.info("Shared via WebSocket")
    else:
        await websocket.send_text("Run not found")
    await websocket.close()