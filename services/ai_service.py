"""GPT 호출과 시스템 프롬프트 구성(컨텍스트 주입)."""
from openai import OpenAI

from config import OPENAI_API_KEY, OPENAI_MODEL

_client: OpenAI | None = None


def _get_client() -> OpenAI:
    global _client
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY가 설정되지 않았습니다.")
    if _client is None:
        _client = OpenAI(api_key=OPENAI_API_KEY, timeout=30)
    return _client


def build_system_prompt(summary: dict) -> str:
    """요약 정보를 시스템 프롬프트에 넣습니다. 이것이 '컨텍스트 주입'입니다."""
    if summary["count"] == 0:
        data_block = "- 저장된 데이터가 아직 없습니다."
    else:
        m = summary["metrics"]
        data_block = (
            f"- 데이터 기간: {summary['period']}\n"
            f"- 총 레코드: {summary['count']}개\n"
            f"- 주요 지표: 합계 {m['total']:,}, 평균 {m['average']:,}, "
            f"최대 {m['max']:,}, 최소 {m['min']:,}\n"
            f"- 최고 기록: {summary['best']['date']} ({summary['best']['value']:,})\n"
            f"- 최신 기록: {summary['latest']['date']} ({summary['latest']['value']:,})\n"
            f"- 최근 트렌드: {summary['trend']}"
        )

    return (
        "당신은 데이터 분석 비서입니다.\n\n"
        "[사용자 데이터 요약]\n"
        f"{data_block}\n\n"
        "위 데이터를 기반으로 맞춤형 답변을 제공하세요. "
        "요약에 없는 수치는 지어내지 말고, 모른다고 답하세요. "
        "한국어로 간결하게 답하세요."
    )


def ask_gpt(system_prompt: str, history: list[dict], user_message: str) -> str:
    messages = [
        {"role": "system", "content": system_prompt},
        *history,
        {"role": "user", "content": user_message},
    ]
    response = _get_client().chat.completions.create(
        model=OPENAI_MODEL,
        messages=messages,
        max_tokens=500,  # 비용 통제: 응답 길이 상한
        temperature=0.3,
    )
    return (response.choices[0].message.content or "").strip()
