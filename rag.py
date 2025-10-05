import json
import os
import numpy as np
import onnxruntime as ort

# Carrega o modelo ONNX uma vez
MODEL_PATH = os.path.join("models", "mini-gpt.onnx")
print("DEBUG: Carregando modelo ONNX...")
session = ort.InferenceSession(MODEL_PATH)
print("DEBUG: Modelo ONNX carregado com sucesso!")

def carregar_base():
    caminho = os.path.join("data", "nasa_dataset.json")
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            print("DEBUG: Base de dados carregada")
            return json.load(f)
    except Exception as e:
        print(f"DEBUG: Erro ao carregar base: {e}")
        return []

def tokenize_input(text):
    # Função simplificada de tokenização (substitua por uma real se necessário)
    tokens = text.split()
    token_ids = [hash(word) % 1000 for word in tokens]  # Exemplo fictício
    return np.array([token_ids], dtype=np.int64)

def detokenize_output(token_ids):
    # Função simplificada de detokenização (substitua por uma real)
    return " ".join([str(id) for id in token_ids])

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

        entrada = f"Contexto: {contexto}\nPergunta: {prompt}\nResposta:"
        
        # Tokenização simplificada (substitua por tokenização real do modelo)
        input_ids = tokenize_input(entrada)
        
        # Executa inferência com ONNX Runtime
        outputs = session.run(None, {"input_ids": input_ids})[0]
        texto = detokenize_output(outputs[0])
        print(f"DEBUG: Resposta gerada: {texto}")
        return texto or "[Erro: resposta vazia do modelo]"
    except Exception as e:
        print(f"DEBUG: Erro em gerar_resposta: {e}")
        return f"[Erro ao gerar resposta: {e}]"