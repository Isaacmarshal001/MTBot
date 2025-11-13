import fetch from "node-fetch";

export async function handler() {
  const BOT_TOKEN = process.env.BOT_TOKEN;
  const CHAT_ID = process.env.CHAT_ID;
  const message = `🌅 Good morning! Wishing you a productive trading day ahead.`;

  const url = `https://api.telegram.org/bot${BOT_TOKEN}/sendMessage`;
  const payload = { chat_id: CHAT_ID, text: message };

  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });

  const data = await res.json();
  return {
    statusCode: 200,
    body: JSON.stringify({ sent: true, data })
  };
}
