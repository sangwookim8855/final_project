from fastapi import APIRouter, HTTPException, Response

from schemas import DataIn, DataOut, SummaryOut
from services import data_service
from services.analysis import build_summary

router = APIRouter(prefix="/api/data", tags=["data"])


@router.get("", response_model=list[DataOut])
def list_data():
    return data_service.list_data()


@router.get("/summary", response_model=SummaryOut)
def get_summary():
    return build_summary(data_service.list_data())


@router.post("", response_model=DataOut, status_code=201)
def create_data(item: DataIn):
    return data_service.create_data(item)


@router.put("/{doc_id}", response_model=DataOut)
def update_data(doc_id: str, item: DataIn):
    result = data_service.update_data(doc_id, item)
    if result is None:
        raise HTTPException(status_code=404, detail="데이터를 찾을 수 없습니다.")
    return result


@router.delete("/{doc_id}", status_code=204)
def delete_data(doc_id: str):
    if not data_service.delete_data(doc_id):
        raise HTTPException(status_code=404, detail="데이터를 찾을 수 없습니다.")
    return Response(status_code=204)
