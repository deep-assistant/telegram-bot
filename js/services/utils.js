// HTTP helper functions using fetch API
export async function asyncPost(url, { data = null, json = null, headers = {}, params = {} } = {}) {
  const query = new URLSearchParams(params).toString();
  const fullUrl = query ? `${url}?${query}` : url;
  const options = { method: 'POST', headers: { ...headers } };
  if (json !== null) options.body = JSON.stringify(json);
  else if (data !== null) options.body = data;
  const response = await fetch(fullUrl, options);
  return response;
}

export async function asyncGet(url, { params = {}, headers = {} } = {}) {
  const query = new URLSearchParams(params).toString();
  const fullUrl = query ? `${url}?${query}` : url;
  const response = await fetch(fullUrl, { method: 'GET', headers });
  return response;
}

export async function asyncPut(url, { data = null, json = null, headers = {}, params = {} } = {}) {
  const query = new URLSearchParams(params).toString();
  const fullUrl = query ? `${url}?${query}` : url;
  const options = { method: 'PUT', headers: { ...headers } };
  if (json !== null) options.body = JSON.stringify(json);
  else if (data !== null) options.body = data;
  const response = await fetch(fullUrl, options);
  return response;
}

export async function asyncDelete(url, { params = {}, headers = {} } = {}) {
  const query = new URLSearchParams(params).toString();
  const fullUrl = query ? `${url}?${query}` : url;
  const response = await fetch(fullUrl, { method: 'DELETE', headers });
  return response;
}

// Utility find functions
export function findInList(lst, element) {
  return lst.includes(element) ? element : null;
}

export function findInListByField(lst, field, value) {
  return lst.find(item => item[field] === value) || null;
}
