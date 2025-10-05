// /api/chat.js
import { Groq } from 'groq-sdk';

const groq = new Groq({
  apiKey: process.env.GROQ_API_KEY
});

export default async function handler(req, res) {
  if (req.method !== "POST") return res.status(405).json({ error: "Método não permitido" });

  const { prompt } = req.body;
  if (!prompt) return res.status(400).json({ error: "Faltou prompt" });

  try {
    // Criar a requisição de chat com streaming
    const chatCompletion = await groq.chat.completions.create({
      messages: [
        { role: "user", content: prompt }
      ],
      model: "llama-3.3-70b-versatile",
      temperature: 1,
      max_completion_tokens: 1024,
      top_p: 1,
      stream: false // ⚠️ streaming só funciona no Node, não no fetch do browser
    });

    // Pega o texto completo
    const text = chatCompletion.choices[0]?.message?.content || "Sem resposta";
    res.status(200).json({ resposta: text });

  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Erro interno do servidor" });
  }
}

