async function apiFetch(path, options = {}) {
  const token = getToken();
  const headers = options.headers || {};

  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(window.API_BASE + path, {
    ...options,
    headers
  });

  const contentType = res.headers.get("content-type") || "";
  const payload = contentType.includes("application/json")
    ? await res.json()
    : await res.text();

  if (!res.ok) {
    throw new Error(typeof payload === "string" ? payload : JSON.stringify(payload));
  }

  return payload;
}