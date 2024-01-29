from firebase_admin import App, firestore
import discord
import datetime


class FirestoreManager:
    warn_collection = 'warns'

    def __init__(self, app: App) -> None:
        self.app_firestore = firestore.client(app)

    async def list_warn(self, user: str) -> list | None:
        doc_ref = self.app_firestore.collection(self.warn_collection).document(user)
        if(doc_ref.get().exists):
            return doc_ref.get().to_dict()['warns']
        return []

    async def remove_warn(self, warn_id: int, user: str) -> int | None:
        doc_ref = self.app_firestore.collection(self.warn_collection).document(user)
        warn_data = doc_ref.get().to_dict()['warns']
        try:
            warn_data.pop(warn_id)
            doc_ref.set({self.warn_collection: warn_data})
            return len(list(warn_data))

        except IndexError as error:
            print(error)
            return None

    async def add_warn(self, user: str, author: str, reason: str) -> int:
        timestamp_atual = datetime.datetime.now().strftime("%d/%m/%Y")
        doc_ref = self.app_firestore.collection(self.warn_collection).document(user)
        dados = {
            self.warn_collection: firestore.ArrayUnion([{
                "motivo": reason,
                "author": author,
                "data": timestamp_atual
            }])
        }

        doc_ref.set(dados, merge=True)

        return len(doc_ref.get().to_dict()['warns'])
