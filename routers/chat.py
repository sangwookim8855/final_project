import logging

from fastapi import APIRouter, HTTPException

from schemas import ChatRequest, ChatResponse
from services import conversation_service, data_service
from services.ai_service import ask_gpt, build_system_prompt
from services.analysis import build_summary

router = APIRouter(prefix="/api/chat", tags=["chat"])
logger = logging.getLogger(__name__)

HISTORY_LIMIT = 10  # 최근 메시지 몇 개까지 이어서 보낼지


@router.post("", response_model=ChatResponse)
def chat(body: ChatRequest):
    # 1) 데이터 요약 조회
    summary = build_summary(data_service.list_data())

    # 2) 이어가는 대화라면 기존 메시지 불러오기
    history: list[dict] = []
    conv = None
    if body.conversation_id:
        conv = conversation_service.get_conversation(body.conversation_id)
        if conv is None:
            raise HTTPException(status_code=404, detail="대화를 찾을 수 없습니다.")
        history = [
            {"role": m["role"], "content": m["content"]}
            for m in conv.get("messages", [])[-HISTORY_LIMIT:]
        ]

    # 3) 요약을 시스템 프롬프트에 넣고 GPT 호출
    system_prompt = build_system_prompt(summary)
    try:
        reply = ask_gpt(system_prompt, history, body.message)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception:
        logger.exception("OpenAI 호출 실패")
        raise HTTPException(
            status_code=502, detail="AI 응답을 가져오지 못했습니다. 잠시 후 다시 시도해주세요."
        )

    # 4) 대화 자동 저장
    new_messages = [
        {"role": "user", "content": body.message},
        {"role": "assistant", "content": reply},
    ]
    if conv is None:
        conv_id = conversation_service.create_conversation(
            title=body.message[:30], messages=new_messages
        )
    else:
        conv_id = body.conversation_id
        conversation_service.append_messages(conv_id, new_messages)

    return ChatResponse(conversation_id=conv_id, reply=reply)
