import { tokenizeService, GPTModels } from './services/index.js';

async function hello() {
  const token = await tokenizeService.create_new_token(1495307231);
  console.log(token);
  await tokenizeService.update_user_token(1495307231, 10000);
  const asd = await tokenizeService.get_user_tokens(1495307231);
  console.log(asd);
}

hello().catch(console.error);

