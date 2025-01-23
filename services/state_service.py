from enum import Enum

from db import data_base, db_key


class StateTypes(Enum):
    Default = "default"
    SystemMessageEditing = "system_message_editing"


    Image = "image"
    ImageEditing = "image_editing"

    Dalle3 = "dalle3"
    Midjourney = "midjourney"
    Suno = "suno"
    Flux = "flux"


    Transcribe = "transcribation"

 
class StateService:
    CURRENT_STATE = "current_state"

    def get_current_state(self, user_id: str) -> StateTypes:
        try:
            model = data_base[db_key(user_id, self.CURRENT_STATE)].decode('utf-8')
            return StateTypes(model)
        except KeyError:
            self.set_current_state(user_id, StateTypes.Default)
            return StateTypes.Default

    def set_current_state(self, user_id: str, state: StateTypes):
        with data_base.transaction():
            data_base[db_key(user_id, self.CURRENT_STATE)] = state.value
        data_base.commit()

    def is_image_state(self, user_id: str) -> bool:
        current_state = self.get_current_state(user_id)
        return current_state.value == StateTypes.Image.value

    def is_flux_state(self, user_id: str) -> bool:
        current_state = self.get_current_state(user_id)
        return current_state.value == StateTypes.Flux.value

    def is_dalle3_state(self, user_id: str) -> bool:
        current_state = self.get_current_state(user_id)
        return current_state.value == StateTypes.Dalle3.value

    def is_midjourney_state(self, user_id: str) -> bool:
        current_state = self.get_current_state(user_id)
        return current_state.value == StateTypes.Midjourney.value

    def is_suno_state(self, user_id: str) -> bool:
        current_state = self.get_current_state(user_id)
        return current_state.value == StateTypes.Suno.value

    def is_image_editing_state(self, user_id: str) -> bool:
        current_state = self.get_current_state(user_id)
        return current_state.value == StateTypes.ImageEditing.value


stateService = StateService()
