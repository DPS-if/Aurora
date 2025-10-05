from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

HF_TOKEN = os.environ["HF_API_KEY"]
MODEL_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"

@app.route("/api/suggest", methods=["POST"])
def sugerir():
    dados = request.get_json()
    prompt = dados.get("problem_text", "")

    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {"inputs": prompt}

    try:
        resposta = requests.post(MODEL_URL, headers=headers, json=payload)
        resultado = resposta.json()
        texto = resultado[0]["generated_text"] if isinstance(resultado, list) else "Erro na geração"
        return jsonify({"solution": texto})
    except Exception as e:
        print("Erro Hugging Face:", e)
        return jsonify({"solution": "Desculpe, ocorreu um erro na análise da IA."}), 500
