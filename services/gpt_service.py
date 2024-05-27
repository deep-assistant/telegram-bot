from enum import Enum

from db import data_base, db_key


class GPTModels(Enum):
    GPT_4o = "gpt-4o"
    GPT_3_5 = "gpt-3.5"


class SystemMessages(Enum):
    Default = "default"
    SoftwareDeveloper = "software_developer"
    Happy = "happy"


is_requesting = {}

gpt_models = {
    GPTModels.GPT_3_5.value: "gpt-35-16k",
    GPTModels.GPT_4o.value: "gpt-4o"
}


class GPTService:
    CURRENT_MODEL_KEY = "current_model"
    CURRENT_SYSTEM_MESSAGE_KEY = "current_system_message"

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

    def get_current_system_message(self, user_id: str) -> str:
        try:
            return data_base[db_key(user_id, self.CURRENT_SYSTEM_MESSAGE_KEY)].decode('utf-8')
        except KeyError:
            value = SystemMessages.Default.value
            self.set_current_system_message(user_id, value)
            return value

    def set_current_system_message(self, user_id: str, value: str) -> str:
        with data_base.transaction():
            data_base[db_key(user_id, self.CURRENT_SYSTEM_MESSAGE_KEY)] = value
        data_base.commit()

    def get_mapping_gpt_model(self, user_id: str):
        return gpt_models[self.get_current_model(user_id).value]


gptService = GPTService()
