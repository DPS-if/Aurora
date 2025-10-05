import { Groq } from "groq-sdk";

const groq = new Groq({
  apiKey: process.env.GROQ_API_KEY
});

export default async function handler(req, res) {
  if (req.method !== "POST") {
    return res.status(405).json({ error: "Method not allowed" });
  }

  const { message } = req.body;

  try {
    const completion = await groq.chat.completions.create({
      model: "llama-3.3-70b-versatile",
      messages: [
        {
          role: "system",
          content: `
You are Aurora — a researcher and environmental specialist with deep knowledge in urban environmental issues, always linking your insights to sociology. 
You must always respond in clear, academic, and fluent **English**, regardless of the user's language. 
When asked to summarize, you must write around **10 lines** and finish with a **single keyword** that represents the main solution.
`
        },
        {
          role: "user",
          content: message
        }
      ],
      temperature: 0.8,
      max_completion_tokens: 1024,
      top_p: 1
    });

    const reply = completion.choices[0]?.message?.content || "No response.";
    res.status(200).json({ reply });
  } catch (error) {
    console.error("Error:", error);
    res.status(500).json({ error: "Internal server error." });
  }
}
