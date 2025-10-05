# rag.py
import json
import os
from transformers import pipeline

# Carrega o modelo uma vez (cache no Hugging Face Hub)
print("DEBUG: Carregando modelo DistilGPT-2...")
generator = pipeline("text-generation", model="distilgpt2", device=-1)  # device=-1 para CPU
print("DEBUG: Modelo carregado com sucesso!")

def carregar_base():
    caminho = os.path.join("data", "nasa_dataset.json")
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            print("DEBUG: Base de dados carregada")
            return json.load(f)
    except Exception as e:
        print(f"DEBUG: Erro ao carregar base: {e}")
        return []

def gerar_resposta(prompt: str) -> str:
    try:
        data = carregar_base()
        relacionados = [
            item["description"]
            for item in data
            if prompt.lower() in item["description"].lower()
        ][:3]
        contexto = "\n".join(relacionados) if relacionados else "Nenhum dado relevante encontrado."

        entrada = f"Contexto: {contexto}\nPergunta: {prompt}\nResposta:"
        
        # Gera texto com o modelo local
        response = generator(
            entrada,
            max_new_tokens=200,
            temperature=0.7,
            do_sample=True,
            pad_token_id=generator.tokenizer.eos_token_id
        )
        texto = response[0]["generated_text"][len(entrada):].strip()  # Remove a entrada da resposta
        print(f"DEBUG: Resposta gerada: {texto}")
        return texto or "[Erro: resposta vazia do modelo]"
    except Exception as e:
        print(f"DEBUG: Erro em gerar_resposta: {e}")
        return f"[Erro ao gerar resposta: {e}]"