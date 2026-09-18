import os
import firebase_admin
from firebase_admin import credentials

if not firebase_admin._apps:
    service_account_json = os.getenv("FIREBASE_SERVICE_ACCOUNT")

    if not service_account_json:
        raise RuntimeError("FIREBASE_SERVICE_ACCOUNT non configurata")

    import json

    cred = credentials.Certificate(
        json.loads(service_account_json)
    )

    firebase_admin.initialize_app(cred)