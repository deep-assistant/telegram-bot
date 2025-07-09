import fs from 'fs';
import path from 'path';
import YAML from 'yaml';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const LOCALES_DIR = path.join(__dirname, 'locales');
const cache = {};

function loadLocale(locale) {
  if (cache[locale]) return cache[locale];
  const filenames = [`${locale}.yml`, `${locale}.yaml`, `${locale}.json`];
  for (const fname of filenames) {
    const fp = path.join(LOCALES_DIR, fname);
    if (fs.existsSync(fp)) {
      const txt = fs.readFileSync(fp, 'utf8');
      const data = fname.endsWith('.json') ? JSON.parse(txt) : YAML.parse(txt);
      cache[locale] = data;
      return data;
    }
  }
  cache[locale] = {};
  return {};
}

function getNested(obj, key) {
  return key.split('.').reduce((o, k) => (o ? o[k] : undefined), obj);
}

export function translate(locale, key) {
  const data = loadLocale(locale);
  const val = getNested(data, key) ?? data[key];
  if (val) return val;
  if (locale !== 'ru') {
    const fallback = loadLocale('ru');
    const fb = getNested(fallback, key) ?? fallback[key];
    if (fb) return fb;
  }
  return `{${key}}`;
}

export function createI18nMiddleware(defaultLocale = 'ru') {
  return async (ctx, next) => {
    const code = ctx.from?.language_code?.split('-')[0] || defaultLocale;
    ctx.locale = code;
    ctx.t = (k) => translate(code, k);
    await next();
  };
} 