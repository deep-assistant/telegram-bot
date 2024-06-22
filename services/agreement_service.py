from db import data_base, db_key


class AgreementService:
    AGREEMENT_STATUS = "agreement-status"

    def get_agreement_status(self, user_id: str) -> bool:
        return True
        # try:
        #     value = data_base[db_key(user_id, self.AGREEMENT_STATUS)].decode('utf-8')
        #     if value == "False":
        #         return False
        #     return True
        # except KeyError:
        #     self.set_agreement_status(user_id, False)
        #     return False

    def set_agreement_status(self, user_id: str, value: bool):
        with data_base.transaction():
            data_base[db_key(user_id, self.AGREEMENT_STATUS)] = value
        data_base.commit()


agreementService = AgreementService()
