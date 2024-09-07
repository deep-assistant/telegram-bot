from enum import Enum

from db import data_base, db_key


class GPTModels(Enum):
    GPT_4o = "gpt-4o"
    GPT_4o_mini = "gpt-4o-mini"
    GPT_3_5 = "gpt-3.5"
    Llama3_1_405B = "Llama3_1_405B"
    Llama3_1_70B = "Llama3_1_70B"
    Llama3_1_8B = "Llama3_1_8B"
    Llama_3_70b = "Llama_3_70B"


class SystemMessages(Enum):
    Default = "default"
    SoftwareDeveloper = "software_developer"
    Happy = "happy"
    QuestionAnswer = "question_answer"
    DeepPromt = "deep"

is_requesting = {}

gpt_models = {
    GPTModels.GPT_3_5.value: "gpt-3.5-turbo",
    GPTModels.GPT_4o.value: "gpt-4o-plus",
    GPTModels.GPT_4o_mini.value: 'gpt-4o-mini',
    GPTModels.Llama3_1_405B.value: "meta-llama/Meta-Llama-3.1-405B",
    GPTModels.Llama3_1_70B.value: "meta-llama/Meta-Llama-3.1-70B",
    GPTModels.Llama3_1_8B.value: "meta-llama/Meta-Llama-3.1-8B",
    GPTModels.Llama_3_70b.value: "meta-llama/Meta-Llama-3-70B-Instruct",
}


class GPTService:
    CURRENT_MODEL_KEY = "current_model"
    CURRENT_SYSTEM_MESSAGE_KEY = "current_system_message"

    def get_current_model(self, user_id: str) -> GPTModels:
        try:
            model = data_base[db_key(user_id, self.CURRENT_MODEL_KEY)].decode('utf-8')
            return GPTModels(model)
        except KeyError:
            self.set_current_model(user_id, GPTModels.GPT_4o_mini)
            return GPTModels.GPT_4o_mini
        except Exception:
            self.set_current_model(user_id, GPTModels.GPT_4o_mini)
            return GPTModels.GPT_4o_mini

    def set_current_model(self, user_id: str, model: GPTModels):
        with data_base.transaction():
            data_base[db_key(user_id, self.CURRENT_MODEL_KEY)] = model.value
        data_base.commit()

    def set_is_requesting(self, user_id, value: bool):
        is_requesting[user_id] = value

    def get_is_requesting(self, user_id):
        return False
        # if not (user_id in is_requesting):
        #     self.set_is_requesting(user_id, False)
        #     return False
        #
        # return is_requesting[user_id]

    def get_current_system_message(self, user_id: str) -> str:
        try:
            return data_base[db_key(user_id, self.CURRENT_SYSTEM_MESSAGE_KEY)].decode('utf-8')
        except KeyError:
            value = SystemMessages.Default.value
            self.set_current_system_message(user_id, value)
            return value

    def set_current_system_message(self, user_id: str, value: str):
        with data_base.transaction():
            data_base[db_key(user_id, self.CURRENT_SYSTEM_MESSAGE_KEY)] = value
        data_base.commit()

    def get_mapping_gpt_model(self, user_id: str):
        return gpt_models[self.get_current_model(user_id).value]


gptService = GPTService()
