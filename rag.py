# rag.py
import json
import os
import google.generativeai as genai

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
print(f"DEBUG: GOOGLE_API_KEY configurada: {'[set]' if GOOGLE_API_KEY else '[vazia]'}")
genai.configure(api_key=GOOGLE_API_KEY)

def carregar_base():
    caminho = os.path.join("data", "nasa_dataset.json")
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            print("DEBUG: Base de dados carregada com sucesso")
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
        print(f"DEBUG: Contexto gerado: {contexto[:100]}...")

        entrada = f"Base de dados:\n{contexto}\n\nPergunta: {prompt}"

        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(
            entrada,
            generation_config={
                "max_output_tokens": 200,
                "temperature": 0.7
            }
        )
        print(f"DEBUG: Resposta do Gemini: {response.text}")
        return response.text or "[Erro: resposta vazia do modelo]"
    except Exception as e:
        print(f"DEBUG: Erro no gerar_resposta: {e}")
        return f"[Erro ao gerar resposta: {e}]"