from config import PROXY_URL, ADMIN_TOKEN
from services.utils import async_post, async_get


class AgreementService:
    async def get_agreement_status(self, user_id: str) -> bool:
        params = {
            "masterToken": ADMIN_TOKEN,
            "userId": str(user_id),
        }
        
        try:
            response = await async_get(f"{PROXY_URL}/agreement", params=params)
            
            if response.status_code == 404:
                # User hasn't agreed yet, set initial status to False
                await self.set_agreement_status(user_id, False)
                return False
            elif response.status_code == 200:
                data = response.json()
                return data.get("agreed", False)
            else:
                # For other errors, assume not agreed for safety
                return False
        except Exception:
            # If API is unavailable, assume not agreed for safety
            return False

    async def set_agreement_status(self, user_id: str, value: bool):
        params = {
            "masterToken": ADMIN_TOKEN,
            "userId": str(user_id),
        }
        
        json_data = {
            "agreed": value
        }
        
        try:
            response = await async_post(f"{PROXY_URL}/agreement", params=params, json=json_data)
            return response.status_code in [200, 201]
        except Exception:
            # If API is unavailable, return False to indicate failure
            return False


agreementService = AgreementService()
