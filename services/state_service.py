from enum import Enum
import time

from db import data_base, db_key


class StateTypes(Enum):
    Default = "default"
    SystemMessageEditing = "system_message_editing"


    Image = "image"
    ImageEditing = "image_editing"

    Dalle3 = "dalle3"
    Midjourney = "midjourney"
    Suno = "suno"
    SunoStyle = "suno_style"
    Flux = "flux"


    Transcribe = "transcribation"

 
class StateService:
    CURRENT_STATE = "current_state"
    SYSTEM_MESSAGE_EDITING_TIMESTAMP = "system_message_editing_timestamp"
    SYSTEM_MESSAGE_EDITING_TIMEOUT = 300  # 5 minutes timeout

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
            # Set timestamp when entering SystemMessageEditing mode
            if state == StateTypes.SystemMessageEditing:
                data_base[db_key(user_id, self.SYSTEM_MESSAGE_EDITING_TIMESTAMP)] = str(int(time.time()))
            # Clear timestamp when leaving SystemMessageEditing mode
            elif state != StateTypes.SystemMessageEditing:
                try:
                    del data_base[db_key(user_id, self.SYSTEM_MESSAGE_EDITING_TIMESTAMP)]
                except KeyError:
                    pass
        data_base.commit()

    def is_default_state(self, user_id: str) -> bool:
        current_state = self.get_current_state(user_id)
        return current_state.value == StateTypes.Default.value

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

    def is_suno_style_state(self, user_id: str) -> bool:
        current_state = self.get_current_state(user_id)
        return current_state.value == StateTypes.SunoStyle.value

    def is_image_editing_state(self, user_id: str) -> bool:
        current_state = self.get_current_state(user_id)
        return current_state.value == StateTypes.ImageEditing.value

    def is_system_message_editing_state(self, user_id: str) -> bool:
        current_state = self.get_current_state(user_id)
        return current_state.value == StateTypes.SystemMessageEditing.value

    def check_and_handle_editing_timeout(self, user_id: str) -> bool:
        """
        Check if the system message editing has timed out and reset state if needed.
        Returns True if timeout occurred and state was reset, False otherwise.
        """
        if not self.is_system_message_editing_state(user_id):
            return False
        
        try:
            timestamp_str = data_base[db_key(user_id, self.SYSTEM_MESSAGE_EDITING_TIMESTAMP)].decode('utf-8')
            timestamp = int(timestamp_str)
            current_time = int(time.time())
            
            if current_time - timestamp > self.SYSTEM_MESSAGE_EDITING_TIMEOUT:
                # Timeout occurred, reset to default state
                self.set_current_state(user_id, StateTypes.Default)
                return True
        except (KeyError, ValueError):
            # If timestamp is missing or invalid, reset to default state
            self.set_current_state(user_id, StateTypes.Default)
            return True
        
        return False


stateService = StateService()
