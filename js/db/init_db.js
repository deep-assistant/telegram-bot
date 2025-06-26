import path from 'path';
import { Vedis } from 'vedis';

const dataBase = new Vedis(path.join(process.cwd(), 'data_base.db'));

export function dbKey(userId, key) {
  return `${userId}_${key}`;
}

export { dataBase };
