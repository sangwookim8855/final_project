"""conversations 컬렉션 CRUD."""
from datetime import datetime, timezone

from google.cloud.firestore import Query

from db import db

COLLECTION = "conversations"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def list_conversations() -> list[dict]:
    """목록에는 messages 전체를 빼고 메시지 개수만 돌려줍니다 (옵션 A)."""
    docs = (
        db.collection(COLLECTION)
        .order_by("updated_at", direction=Query.DESCENDING)
        .stream()
    )
    result = []
    for doc in docs:
        data = doc.to_dict()
        result.append(
            {
                "id": doc.id,
                "title": data.get("title", ""),
                "updated_at": data.get("updated_at"),
                "message_count": len(data.get("messages", [])),
            }
        )
    return result


def get_conversation(conv_id: str) -> dict | None:
    snap = db.collection(COLLECTION).document(conv_id).get()
    if not snap.exists:
        return None
    return {"id": snap.id, **snap.to_dict()}


def create_conversation(title: str, messages: list[dict]) -> str:
    ref = db.collection(COLLECTION).document()
    now = _now()
    ref.set({"title": title, "messages": messages, "created_at": now, "updated_at": now})
    return ref.id


def append_messages(conv_id: str, new_messages: list[dict]) -> None:
    ref = db.collection(COLLECTION).document(conv_id)
    snap = ref.get()
    messages = snap.to_dict().get("messages", []) + new_messages
    ref.update({"messages": messages, "updated_at": _now()})


def delete_conversation(conv_id: str) -> bool:
    ref = db.collection(COLLECTION).document(conv_id)
    if not ref.get().exists:
        return False
    ref.delete()
    return True
