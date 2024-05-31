import logging
import threading
import time

import schedule

max_tokens = 50000


class TokenizeService:
    token_dict = {}

    def is_available_context(self, user_id):
        logging.log(logging.INFO, self.token_dict)

        if user_id in self.token_dict:
            return self.token_dict[user_id] < max_tokens

        self.token_dict[user_id] = 0
        return True

    def update_tokens(self, user_id, tokens: int):
        self.token_dict[user_id] = self.token_dict[user_id] + tokens

    def reset_token_dict(self):
        self.token_dict = {}

    def init_reset(self):
        schedule.every().day.at("00:00").do(self.reset_token_dict)

        while True:
            logging.log(logging.INFO, self.token_dict)
            schedule.run_pending()
            time.sleep(1)


tokenizeService = TokenizeService()


def run_init_reset():
    schedule_thread = threading.Thread(target=tokenizeService.init_reset)
    schedule_thread.start()
