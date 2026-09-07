export async function ping({ baseUrl, apiKey }) {
  const r = await fetch(`${baseUrl.replace(/\/$/, "")}/health`, {
    headers: { "X-API-Key": apiKey },
  });
  const data = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(data.detail || `HTTP ${r.status}`);
  return data;
}

export async function sendChat({ baseUrl, apiKey, text }) {
  const r = await fetch(`${baseUrl.replace(/\/$/, "")}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": apiKey,
    },
    body: JSON.stringify({ text }),
  });
  const data = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(data.detail || `HTTP ${r.status}`);
  return data.reply || "";
}
