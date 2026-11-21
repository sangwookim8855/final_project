"""data 컬렉션 CRUD. 라우터는 HTTP만, Firestore 접근은 여기서만 합니다."""
from db import db
from schemas import DataIn

COLLECTION = "data"


def _to_out(doc_id: str, data: dict) -> dict:
    return {
        "id": doc_id,
        "date": data["date"],
        "value": data["value"],
        "memo": data.get("memo", ""),
    }


def _to_doc(item: DataIn) -> dict:
    return {"date": item.date.isoformat(), "value": item.value, "memo": item.memo}


def list_data() -> list[dict]:
    docs = db.collection(COLLECTION).order_by("date").stream()
    return [_to_out(doc.id, doc.to_dict()) for doc in docs]


def create_data(item: DataIn) -> dict:
    ref = db.collection(COLLECTION).document()
    data = _to_doc(item)
    ref.set(data)
    return _to_out(ref.id, data)


def update_data(doc_id: str, item: DataIn) -> dict | None:
    ref = db.collection(COLLECTION).document(doc_id)
    if not ref.get().exists:
        return None
    data = _to_doc(item)
    ref.set(data)
    return _to_out(doc_id, data)


def delete_data(doc_id: str) -> bool:
    ref = db.collection(COLLECTION).document(doc_id)
    if not ref.get().exists:
        return False
    ref.delete()
    return True
