import json

import firebase_admin
from firebase_admin import credentials, firestore

from config import FIREBASE_SERVICE_ACCOUNT_JSON, FIREBASE_SERVICE_ACCOUNT_PATH


def _init_firebase() -> None:
    """서비스 계정 키를 환경 변수에서 읽어 Firebase 앱을 초기화합니다."""
    if firebase_admin._apps:
        return

    if FIREBASE_SERVICE_ACCOUNT_JSON:
        cred = credentials.Certificate(json.loads(FIREBASE_SERVICE_ACCOUNT_JSON))
    elif FIREBASE_SERVICE_ACCOUNT_PATH:
        cred = credentials.Certificate(FIREBASE_SERVICE_ACCOUNT_PATH)
    else:
        raise RuntimeError(
            "FIREBASE_SERVICE_ACCOUNT_JSON 또는 FIREBASE_SERVICE_ACCOUNT_PATH를 설정하세요."
        )

    firebase_admin.initialize_app(cred)


_init_firebase()
db = firestore.client()
