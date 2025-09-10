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

/**
 * Extract a human-readable filename from a URL, especially for Discord CDN URLs.
 * 
 * Takes a URL like:
 * https://cdn.discordapp.com/attachments/1334433356263194676/1335313374656860181/deborah_ua1077041_anime_girl_2e86d324-0275-412f-9413-b5298dc1593f.png?ex=679fb6fd&is=679e657d&hm=c58ae42143406364740aea7627649988d709ec47c86eacf9340a366a874bdd76&
 * 
 * And returns: deborah_anime_girl.png
 * 
 * @param {string} url - The URL to extract filename from
 * @returns {string} Human-readable filename
 */
export function extractHumanReadableFilename(url) {
  try {
    // Parse URL and get the path
    const urlObj = new URL(url);
    const path = decodeURIComponent(urlObj.pathname);
    
    // Get filename from path
    const pathParts = path.split('/');
    const filename = pathParts[pathParts.length - 1];
    
    if (!filename) {
      return 'image.png';
    }
    
    // Split filename and extension
    const lastDotIndex = filename.lastIndexOf('.');
    let namePart = filename;
    let ext = '.png';
    
    if (lastDotIndex !== -1) {
      namePart = filename.substring(0, lastDotIndex);
      ext = filename.substring(lastDotIndex);
    }
    
    // For Discord CDN URLs, apply human-readable extraction
    if (url.includes('cdn.discordapp.com') || url.toLowerCase().includes('discord')) {
      return extractDiscordFilename(namePart, ext);
    }
    
    // For other URLs, try to clean up the filename
    return cleanFilename(namePart, ext);
    
  } catch (error) {
    // Fallback to generic name if anything goes wrong
    return 'image.png';
  }
}

/**
 * Extract human-readable name from Discord CDN filename.
 * 
 * Example: deborah_ua1077041_anime_girl_2e86d324-0275-412f-9413-b5298dc1593f
 * Returns: deborah_anime_girl
 * 
 * @param {string} namePart - The name part without extension
 * @param {string} ext - The file extension
 * @returns {string} Cleaned filename with extension
 */
function extractDiscordFilename(namePart, ext) {
  // Remove UUID-like patterns (hexadecimal with dashes)
  // Pattern for UUID: 8-4-4-4-12 hex digits
  namePart = namePart.replace(/_[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}/g, '');
  
  // Remove other hex patterns and numbers at the end
  namePart = namePart.replace(/_[0-9a-fA-F]{6,}$/g, '');
  namePart = namePart.replace(/_\d{10,}/g, ''); // Remove long numbers like timestamps
  
  // Split by underscores and keep meaningful words
  const parts = namePart.split('_');
  const meaningfulParts = [];
  
  for (const part of parts) {
    // Skip parts that are purely numeric or very short
    if (part.length < 2 || /^\d+$/.test(part)) {
      continue;
    }
    // Skip parts that look like user IDs or codes (starts with letters followed by mostly numbers)
    // But keep common words that might have some numbers mixed in
    if (/^[a-zA-Z]+\d{3,}/.test(part)) {  // Skip things like "user123", "id456" etc
      continue;
    }
    meaningfulParts.push(part);
  }
  
  // Take first few meaningful parts
  const resultParts = meaningfulParts.slice(0, 3); // Limit to avoid very long names
  
  if (resultParts.length === 0) {
    return `image${ext}`;
  }
  
  const resultName = resultParts.join('_');
  return `${resultName}${ext}`;
}

/**
 * Clean up a generic filename to make it more human-readable.
 * 
 * @param {string} namePart - The name part without extension
 * @param {string} ext - The file extension
 * @returns {string} Cleaned filename with extension
 */
function cleanFilename(namePart, ext) {
  // Remove query parameters and fragments that might be in the name
  namePart = namePart.replace(/[?#].*$/, '');
  
  // Check for a meaningful prefix before a long hex sequence
  const prefixBeforeHex = namePart.match(/^([a-zA-Z]{2,})[0-9a-fA-F]{16,}$/);
  if (prefixBeforeHex) {
    namePart = prefixBeforeHex[1];
  } else {
    // Remove very long hex sequences (16+ characters) from the end
    namePart = namePart.replace(/[0-9a-fA-F]{16,}$/, '');
  }
  
  // If the name is empty or too short after cleaning, use a default
  if (namePart.length < 2) {
    namePart = 'image';
  }
  
  return `${namePart}${ext}`;
}
