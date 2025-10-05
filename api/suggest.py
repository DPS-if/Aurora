from flask import Flask, request, jsonify
import google.generativeai as genai
import os

app = Flask(__name__)
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

model = genai.GenerativeModel("gemini-pro")  # Gemini 1.5 Pro

@app.route("/api/suggest", methods=["POST"])
def sugerir():
    dados = request.get_json()
    prompt = dados.get("problem_text", "")

    try:
        resposta = model.generate_content(prompt)
        texto = resposta.text
        return jsonify({"solution": texto})
    except Exception as e:
        return jsonify({"solution": "Desculpe, ocorreu um erro na análise da IA."}), 500
