from config import PROXY_URL, ADMIN_TOKEN
from services.utils import async_post, async_get


class ReferralsService:
    async def get_awards(self, user_id):
        params = {
            "masterToken": ADMIN_TOKEN,
            "userId": user_id,
        }

        response = await async_get(f"{PROXY_URL}/referral/award", params=params)

        return response.json()

    async def create_referral(self, user_id, referral_id=None):
        params = {
            "masterToken": ADMIN_TOKEN,
            "userId": user_id,
            "referralId": referral_id
        }

        response = await async_post(f"{PROXY_URL}/referral", params=params)

        if response.status_code == 400:
            return None

        return response.json()

    async def get_referral(self, user_id):
        params = {
            "masterToken": ADMIN_TOKEN,
            "userId": user_id,
        }

        response = await async_get(f"{PROXY_URL}/referral", params=params)

        return response.json()


referralsService = ReferralsService()
