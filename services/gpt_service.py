from enum import Enum

from db import data_base, db_key


class GPTModels(Enum):
    GPT_4o = "gpt-4o"
    GPT_3_5 = "gpt-3.5"


is_requesting = {}


class GPTService:
    CURRENT_MODEL_KEY = "current_model"

    def get_current_model(self, user_id: str) -> GPTModels:
        try:
            model = data_base[db_key(user_id, self.CURRENT_MODEL_KEY)].decode('utf-8')
            return GPTModels(model)
        except KeyError:
            self.set_current_model(user_id, GPTModels.GPT_4o)
            return GPTModels.GPT_4o

    def set_current_model(self, user_id: str, model: GPTModels):
        with data_base.transaction():
            data_base[db_key(user_id, self.CURRENT_MODEL_KEY)] = model.value
        data_base.commit()

    def set_is_requesting(self, user_id, value: bool):
        is_requesting[user_id] = value

    def get_is_requesting(self, user_id):
        if not (user_id in is_requesting):
            self.set_is_requesting(user_id, False)
            return False

        return is_requesting[user_id]


gptService = GPTService()
