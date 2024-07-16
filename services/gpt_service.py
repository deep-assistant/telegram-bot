from enum import Enum

from db import data_base, db_key


class GPTModels(Enum):
    GPT_4o = "gpt-4o"
    GPT_3_5 = "gpt-3.5"
    Nemotron_4_340b = "Nemotron_4_340b"
    Llama_3_70b = "Llama_3_70B"
    Qwen2_72b = "Qwen2_72B"
    CodeLlama_70b = "CodeLlama_70b"
    WizardLM_2_8_x22b = "WizardLM_2_8_x22b"
    Llama_3_8B = "Llama_3_8B"
    WizardLM_2_7B = "WizardLM_2_7B"


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
    GPTModels.Qwen2_72b.value: "Qwen/Qwen2-72B-Instruct",
    GPTModels.Nemotron_4_340b.value: "nvidia/Nemotron-4-340B-Instruct",
    GPTModels.Llama_3_70b.value: "meta-llama/Meta-Llama-3-70B-Instruct",
    GPTModels.CodeLlama_70b.value: "codellama/CodeLlama-70b-Instruct-hf",
    GPTModels.Llama_3_8B.value: "meta-llama/Meta-Llama-3-8B-Instruct",
    GPTModels.WizardLM_2_7B.value: "microsoft/WizardLM-2-7B"
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
        except Exception:
            self.set_current_model(user_id, GPTModels.GPT_4o)
            return GPTModels.GPT_4o

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
