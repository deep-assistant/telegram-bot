import { dataBase, dbKey } from '../db/init_db.js';

class AgreementService {
  constructor() {
    this.AGREEMENT_STATUS = 'agreement-status';
  }

  async getAgreementStatus(userId) {
    // TODO: implement persistent storage lookup
    // Stub: always return true
    return true;
  }

  async setAgreementStatus(userId, value) {
    // TODO: store agreement status in database
    await dataBase.set(dbKey(userId, this.AGREEMENT_STATUS), value);
    await dataBase.commit();
  }
}

export const agreementService = new AgreementService();
