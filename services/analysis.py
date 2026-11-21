"""시계열 데이터를 요약(기간, 개수, 기본 통계, 최근 추세)으로 바꿉니다."""
from statistics import mean


def _pct_change(new: float, old: float) -> float:
    return (new - old) / old * 100 if old else 0.0


def build_summary(rows: list[dict]) -> dict:
    if not rows:
        return {
            "period": None,
            "count": 0,
            "metrics": None,
            "trend": "데이터 없음",
            "latest": None,
            "best": None,
        }

    rows = sorted(rows, key=lambda r: r["date"])
    values = [r["value"] for r in rows]
    n = len(values)

    max_row = max(rows, key=lambda r: r["value"])
    min_row = min(rows, key=lambda r: r["value"])

    # 최근 구간 평균 vs 직전 같은 길이 구간 평균으로 추세를 판단
    window = min(30, n // 2)
    if window >= 1:
        recent = mean(values[-window:])
        previous = mean(values[-2 * window : -window])
        change = _pct_change(recent, previous)
        if change > 3:
            label = "상승"
        elif change < -3:
            label = "하락"
        else:
            label = "유지"
        trend = f"{label} (최근 {window}일 평균 {change:+.1f}% vs 직전 {window}일)"
    else:
        trend = "데이터가 부족해 추세를 계산할 수 없음"

    return {
        "period": f"{rows[0]['date']} ~ {rows[-1]['date']}",
        "count": n,
        "metrics": {
            "total": sum(values),
            "average": round(mean(values)),
            "max": max_row["value"],
            "min": min_row["value"],
        },
        "trend": trend,
        "latest": {"date": rows[-1]["date"], "value": rows[-1]["value"]},
        "best": {"date": max_row["date"], "value": max_row["value"]},
    }
