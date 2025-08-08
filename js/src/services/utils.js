// HTTP helper functions using fetch API
export async function asyncPost(url, { data = null, json = null, headers = {}, params = {}, timeout = 0, files = null } = {}) {
  const controller = new AbortController();
  if (timeout > 0) {
    setTimeout(() => controller.abort(), timeout);
  }
  const query = new URLSearchParams(params).toString();
  const fullUrl = query ? `${url}?${query}` : url;
  const options = { method: 'POST', headers: { ...headers }, signal: controller.signal };

  if (files) {
    const formData = new FormData();
    if (json) {
      for (const [key, val] of Object.entries(json)) {
        formData.append(key, val);
      }
    }
    for (const [key, file] of Object.entries(files)) {
      formData.append(key, file);
    }
    options.body = formData;
    delete options.headers['Content-Type'];
  } else if (json !== null) {
    options.body = JSON.stringify(json);
  } else if (data !== null) {
    options.body = data;
  }

  const response = await fetch(fullUrl, options);
  return response;
}

export async function asyncPut(url, { data = null, json = null, headers = {}, params = {}, timeout = 0, files = null } = {}) {
  const controller = new AbortController();
  if (timeout > 0) {
    setTimeout(() => controller.abort(), timeout);
  }
  const query = new URLSearchParams(params).toString();
  const fullUrl = query ? `${url}?${query}` : url;
  const options = { method: 'PUT', headers: { ...headers }, signal: controller.signal };

  if (files) {
    const formData = new FormData();
    if (json) {
      for (const [key, val] of Object.entries(json)) {
        formData.append(key, val);
      }
    }
    for (const [key, file] of Object.entries(files)) {
      formData.append(key, file);
    }
    options.body = formData;
    delete options.headers['Content-Type'];
  } else if (json !== null) {
    options.body = JSON.stringify(json);
  } else if (data !== null) {
    options.body = data;
  }

  const response = await fetch(fullUrl, options);
  return response;
}

export async function asyncDelete(url, { params = {}, headers = {}, timeout = 0 } = {}) {
  const controller = new AbortController();
  if (timeout > 0) {
    setTimeout(() => controller.abort(), timeout);
  }
  const query = new URLSearchParams(params).toString();
  const fullUrl = query ? `${url}?${query}` : url;
  const options = { method: 'DELETE', headers: { ...headers }, signal: controller.signal };

  const response = await fetch(fullUrl, options);
  return response;
}

export async function asyncGet(url, { params = {}, headers = {}, timeout = 0 } = {}) {
  const controller = new AbortController();
  if (timeout > 0) {
    setTimeout(() => controller.abort(), timeout);
  }
  const query = new URLSearchParams(params).toString();
  const fullUrl = query ? `${url}?${query}` : url;
  const options = { method: 'GET', headers: { ...headers }, signal: controller.signal };

  const response = await fetch(fullUrl, options);
  return response;
}

// Utility find functions
export function findInList(lst, element) {
  return lst.includes(element) ? element : null;
}

export function findInListByField(lst, field, value) {
  return lst.find(item => item[field] === value) || null;
}
