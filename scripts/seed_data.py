"""분석할 데이터를 Firestore data 컬렉션에 업로드합니다.

사용법:
  python scripts/seed_data.py              # 샘플 데이터 120일 생성
  python scripts/seed_data.py my_data.csv  # CSV 업로드 (헤더: date,value,memo)
"""
import csv
import random
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from db import db  # noqa: E402


def sample_rows(days: int = 120) -> list[dict]:
    random.seed(42)
    start = date(2026, 7, 1)
    rows = []
    for i in range(days):
        d = start + timedelta(days=i)
        base = 2_000_000 + i * 25_000          # 완만한 상승 추세
        weekend = 1.2 if d.weekday() >= 5 else 1.0
        value = int(base * weekend * random.uniform(0.85, 1.15))
        rows.append({"date": d.isoformat(), "value": value, "memo": "샘플 일별 매출"})
    return rows


def csv_rows(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return [
            {"date": r["date"], "value": int(r["value"]), "memo": r.get("memo", "")}
            for r in csv.DictReader(f)
        ]


def main() -> None:
    rows = csv_rows(sys.argv[1]) if len(sys.argv) > 1 else sample_rows()
    col = db.collection("data")
    for row in rows:
        col.document().set(row)
    print(f"{len(rows)}개 데이터를 저장했습니다.")


if __name__ == "__main__":
    main()
