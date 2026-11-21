from fastapi import APIRouter, HTTPException, Response

from schemas import ConversationIn
from services import conversation_service

router = APIRouter(prefix="/api/conversations", tags=["conversations"])


@router.get("")
def list_conversations():
    return conversation_service.list_conversations()


@router.post("", status_code=201)
def create_conversation(body: ConversationIn):
    conv_id = conversation_service.create_conversation(
        body.title, [m.model_dump() for m in body.messages]
    )
    return conversation_service.get_conversation(conv_id)


@router.get("/{conv_id}")
def get_conversation(conv_id: str):
    conv = conversation_service.get_conversation(conv_id)
    if conv is None:
        raise HTTPException(status_code=404, detail="대화를 찾을 수 없습니다.")
    return conv


@router.delete("/{conv_id}", status_code=204)
def delete_conversation(conv_id: str):
    if not conversation_service.delete_conversation(conv_id):
        raise HTTPException(status_code=404, detail="대화를 찾을 수 없습니다.")
    return Response(status_code=204)
