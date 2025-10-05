from flask import Flask, request, jsonify
from rag import gerar_resposta
import os

app = Flask(__name__)

@app.route("/api/generate", methods=["POST"])
def generate():
    try:
        data = request.get_json()
        prompt = data.get("prompt", "")

        if not prompt:
            return jsonify({"error": "Campo 'prompt' é obrigatório"}), 400

        resposta = gerar_resposta(prompt)
        return jsonify({"response": resposta})
    except Exception as e:
        print(f"Erro interno: {e}")
        return jsonify({"error": "Erro interno no servidor", "details": str(e)}), 500


@app.route("/")
def home():
    return jsonify({
        "status": "online",
        "message": "Aurora v7 - API generativa para o NASA Space Apps"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
