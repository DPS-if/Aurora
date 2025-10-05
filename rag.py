# rag.py
import json, os
from huggingface_hub import InferenceClient

HF_TOKEN = os.getenv("HF_TOKEN", "")
MODEL_ID = os.getenv("MODEL_ID", "mistralai/Mistral-7B-Instruct-v0.1")
client = InferenceClient(token=HF_TOKEN)

def carregar_base():
    caminho = os.path.join("data", "nasa_dataset.json")
    with open(caminho, "r", encoding="utf-8") as f:
        return json.load(f)

def gerar_resposta(prompt: str) -> str:
    try:
        data = carregar_base()
        relacionados = [
            item["description"]
            for item in data
            if prompt.lower() in item["description"].lower()
        ][:3]
        contexto = "\n".join(relacionados) if relacionados else "Nenhum dado relevante encontrado."

        entrada = f"Base de dados:\n{contexto}\n\nPergunta: {prompt}"

        resposta = client.text_generation(
            model=MODEL_ID,
            prompt=entrada,
            max_new_tokens=200,
            temperature=0.7
        )
        return resposta or "[Erro: resposta vazia do modelo]"
    except Exception as e:
        print("Erro no gerar_resposta:", e)
        return f"[Erro ao gerar resposta: {e}]"