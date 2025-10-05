import { Groq } from 'groq-sdk';

const groq = new Groq({
  apiKey: process.env.GROQ_API_KEY
});

export default async function handler(req, res) {
  if (req.method !== "POST") return res.status(405).json({ error: "Método não permitido" });

  const { prompt } = req.body;
  if (!prompt) return res.status(400).json({ error: "Faltou prompt" });

  try {
    const chatCompletion = await groq.chat.completions.create({
      model: "llama-3.3-70b-versatile",
      messages: [
        {
          role: "system",
          content: `Você é Aurora, uma pesquisadora especialista em problemas ambientais urbanos, 
          com conhecimento em sociologia aplicada. Sempre responda:
          1) um resumo de aproximadamente 10 linhas sobre o tema que o usuário enviar;
          2) uma frase final com a solução principal expressa em **uma palavra-chave**. 
          Seja clara, didática e objetiva.`
        },
        {
          role: "user",
          content: prompt
        }
      ],
      temperature: 0.7,
      max_completion_tokens: 1024,
      top_p: 1,
      stream: false
    });

    const text = chatCompletion.choices[0]?.message?.content || "Sem resposta";
    res.status(200).json({ resposta: text });

  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Erro interno do servidor" });
  }
}
