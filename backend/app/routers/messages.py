"""Contact form endpoint: "challenger approaching"."""

import logging

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Message
from app.schemas import MessageAck, MessageIn

router = APIRouter(prefix="/messages", tags=["messages"])

# Logs go to the terminal locally and to CloudWatch on AWS.
logger = logging.getLogger(__name__)


# 201 Created is the correct status for "a new resource was stored",
# instead of the default 200 OK.
@router.post("", response_model=MessageAck, status_code=status.HTTP_201_CREATED)
def send_message(payload: MessageIn, db: Session = Depends(get_db)):
    """
    Save a contact form submission.

    By the time this function runs, FastAPI has already validated the JSON body
    against MessageIn: the email is well-formed and the lengths are within limits.
    Invalid input never reaches this code; the sender gets a 422 instead.
    """
    # Honeypot check: humans never see the "website" field, so if it's filled
    # in, a bot sent this. Reply with success anyway so the bot doesn't learn
    # it was caught and try something smarter, but don't store anything.
    if payload.website:
        logger.info("Dropped a contact message that filled the honeypot field")
        return MessageAck()

    # Copy only the fields we want into a new row. Not passing the whole
    # payload means the honeypot field (and anything added later) can't end
    # up in the database by accident.
    message = Message(name=payload.name, email=payload.email, body=payload.body)

    # add() stages the row; commit() actually writes it in a transaction.
    # If commit fails, nothing is half-saved, and the session is closed
    # by get_db's `finally` block either way.
    db.add(message)
    db.commit()

    # Rate limiting (stopping someone from sending thousands of messages)
    # isn't done here: on Lambda each request may hit a different instance,
    # so an in-memory counter wouldn't work. It will be handled at the AWS
    # level (API Gateway throttling) when the site is deployed.
    return MessageAck()
