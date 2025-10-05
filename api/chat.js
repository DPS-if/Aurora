export default async function handler(req, res) {
  const { prompt } = req.body;

  const resposta = await fetch("https://api.groq.com/openai/v1/chat/completions", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${process.env.GROQ_API_KEY}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      model: "llama3-70b-8192",
      messages: [
        { role: "system", content: "Você é um assistente da NASA que explica ciência e espaço de forma divertida e educativa." },
        { role: "user", content: prompt }
      ],
    }),
  });

  const data = await resposta.json();
  res.status(200).json({
    resposta: data.choices[0].message.content
  });
}
