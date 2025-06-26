import { dataBase, dbKey } from '../db/init_db.js';

class AgreementService {
  constructor() {
    this.AGREEMENT_STATUS = 'agreement-status';
  }

  async getAgreementStatus(userId) {
    try {
      const buf = await dataBase.get(dbKey(userId, this.AGREEMENT_STATUS));
      const val = buf.toString('utf-8');
      // stored as 'False' or truthy
      return val !== 'False';
    } catch {
      // initialize to false if not set
      await this.setAgreementStatus(userId, false);
      return false;
    }
  }

  async setAgreementStatus(userId, value) {
    // TODO: store agreement status in database
    await dataBase.set(dbKey(userId, this.AGREEMENT_STATUS), value);
    await dataBase.commit();
  }
}

export const agreementService = new AgreementService();
