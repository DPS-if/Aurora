# app.py
from flask import Flask, request, jsonify
from rag import gerar_resposta
import os

app = Flask(__name__)

@app.route("/api/generate", methods=["POST"])
def generate():
    try:
        data = request.get_json(force=True)
        prompt = data.get("prompt", "")
        if not prompt:
            return jsonify({"error": "Campo 'prompt' é obrigatório"}), 400

        resposta = gerar_resposta(prompt)
        return jsonify({"response": resposta})

    except Exception as e:
        print("Erro interno:", e)
        return jsonify({"error": "Erro interno no servidor", "details": str(e)}), 500

# Removida a rota GET para /api/generate, pois Flask retorna 405 automaticamente com texto simples.
# Se precisar de uma mensagem customizada, pode adicionar de volta, mas para simplicidade, removemos.

@app.route("/")
def home():
    return jsonify({"status": "online", "message": "Aurora v7 - API generativa"})

if __name__ == "__main__":
    app.run(debug=True)  # Adicionado para rodar localmente com python app.py