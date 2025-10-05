import { NextRequest, NextResponse } from 'next/server';
import { generateFromPrompt } from '../../utils/rag';


export const runtime = 'edge';


export async function POST(req: NextRequest) {
try {
const body = await req.json();
const prompt = body?.prompt;


if (!prompt || typeof prompt !== 'string') {
return NextResponse.json({ error: "Campo 'prompt' é obrigatório e deve ser uma string." }, { status: 400 });
}


const result = await generateFromPrompt(prompt);


return NextResponse.json({ response: result });
} catch (err: any) {
console.error('Erro na API /api/generate:', err);
return NextResponse.json({ error: 'Erro interno ao gerar resposta.', details: err?.message || 'Desconhecido' }, { status: 500 });
}
}