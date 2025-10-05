from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys

# Adiciona diretório pai para importar rag.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print("DEBUG: Inicializando Flask, sys.path:", sys.path)

try:
    from rag import gerar_resposta
except ImportError as e:
    print(f"DEBUG: Erro ao importar rag: {e}")

app = Flask(__name__, static_folder="../", static_url_path="/")
CORS(app, resources={r"/api/*": {"origins": "*"}})

@app.errorhandler(Exception)
def handle_error(e):
    print(f"DEBUG: Erro global: {e}")
    return jsonify({"error": "Erro inesperado", "details": str(e)}), 500

@app.route("/api/generate", methods=["POST", "OPTIONS"])
def generate():
    print(f"DEBUG: Recebido {request.method} em {request.path}")
    if request.method == "OPTIONS":
        return "", 204
    try:
        data = request.get_json(force=True)
        print(f"DEBUG: JSON recebido: {data}")
        prompt = data.get("prompt", "")
        if not prompt:
            return jsonify({"error": "Campo 'prompt' é obrigatório"}), 400
        resposta = gerar_resposta(prompt)
        print(f"DEBUG: Resposta gerada: {resposta}")
        return jsonify({"response": resposta})
    except Exception as e:
        print(f"DEBUG: Erro interno: {e}")
        return jsonify({"error": "Erro interno", "details": str(e)}), 500

@app.route("/", methods=["GET"])
def root():
    print("DEBUG: Servindo index.html")
    return app.send_static_file("index.html")

@app.route("/<path:path>", methods=["GET"])
def catch_all(path):
    print(f"DEBUG: Rota não tratada: {request.method} em /{path}")
    if path == "favicon.ico":
        return app.send_static_file("favicon.ico")
    return jsonify({"error": "Rota não encontrada"}), 404