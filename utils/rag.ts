import fs from 'fs';
import path from 'path';
import { HfInference } from '@huggingface/inference';


const HF_TOKEN = process.env.HF_TOKEN || '';
const MODEL_ID = process.env.MODEL_ID || 'mistralai/Mistral-7B-Instruct-v0.1';


if (!HF_TOKEN) {
console.warn('AVISO: HF_TOKEN não configurado. O serviço falhará sem o token.');
}


const hf = new HfInference(HF_TOKEN);


export async function generateFromPrompt(prompt: string) {
// Carrega dataset local
const datasetPath = path.join(process.cwd(), 'data', 'nasa_dataset.json');
let data: any[] = [];
try {
const raw = fs.readFileSync(datasetPath, 'utf-8');
data = JSON.parse(raw);
} catch (err) {
console.error('Falha ao ler dataset local:', err);
// continuar com data vazia
}


// Busca simples: procura ocorrências do texto no campo description/title
const q = prompt.toLowerCase().trim();
const related = data
.filter(item => {
const text = ((item.title || '') + ' ' + (item.description || '')).toLowerCase();
return text.includes(q);
})
.slice(0, 3)
.map(i => `- ${i.title}: ${i.description}`)
.join('\n');


const systemPrompt = `Você é Aurora v7 — assistente técnico para o NASA Space Apps. Use apenas as informações fornecidas na seção 'dados' para responder quando possível. Se nada for relevante, responda de forma clara, indicando que não há dados suficientes e forneça sugestões de como obter as informações.`;


const inputs = `SYSTEM:\n${systemPrompt}\n\nDADOS RELEVANTES:\n${related || 'Nenhum dado relevante encontrado no dataset.'}\n\nPERGUNTA:\n${prompt}`;


try {
const out = await hf.textGeneration({
model: MODEL_ID,
inputs,
parameters: {
max_new_tokens: 256,
temperature: 0.2
}
});


// A resposta pode estar em diferentes campos dependendo da versão do SDK
const text = (out as any)?.generated_text || (Array.isArray(out) ? out[0]?.generated_text : undefined) || JSON.stringify(out);


return text;
} catch (err: any) {
console.error('Erro ao chamar Hugging Face:', err);
throw new Error('Falha ao gerar resposta via modelo de IA: ' + (err?.message || 'Desconhecido'));
}
}