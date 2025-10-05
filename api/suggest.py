import os
import json
import google.generativeai as genai
from http.server import BaseHTTPRequestHandler

# Versão Definitiva com o Nome do Modelo Mais Recente e Estável

class handler(BaseHTTPRequestHandler):

    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "X-Requested-With, Content-Type")
        self.end_headers()

    def do_POST(self):
        ai_answer = ""
        try:
            # --- 1. CONFIGURAÇÃO ---
            GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
            if not GEMINI_API_KEY:
                raise ValueError("Chave GEMINI_API_KEY não encontrada nas Environment Variables da Vercel.")
            
            genai.configure(api_key=GEMINI_API_KEY)

            # Carrega a base de conhecimento (solutions.json)
            script_dir = os.path.dirname(__file__)
            json_path = os.path.join(script_dir, '..', 'solutions.json')
            with open(json_path, 'r', encoding='utf-8') as f:
                solutions_data = json.load(f)
            
            knowledge_base_text = json.dumps(solutions_data, indent=2, ensure_ascii=False)

            # --- 2. EXTRAÇÃO DOS DADOS DO UTILIZADOR ---
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            user_input = json.loads(post_data.decode('utf-8'))
            user_problem = user_input.get('problem_text', '')

            # --- 3. UMA ÚNICA CHAMADA PODEROSA AO GEMINI ---
            
            system_instruction = "Você é a Aurora, uma IA pesquisadora especialista em mudanças climáticas e desenvolvimento urbano sustentável. Seja sempre simpática, direta e apresente os dados com a confiança de uma académica. Use uma linguagem clara, mas não simplifique excessivamente os conceitos."
            
            final_prompt = f"""
            **Sua Missão como Pesquisadora:**
            Você recebeu um problema de um cidadão e uma base de conhecimento em formato JSON. Siga estas três etapas:

            **Etapa 1: Identificar o Documento Relevante.**
            Leia o "Problema do Cidadão" e analise a "Base de Conhecimento" inteira. Identifique qual dos objetos JSON na base de conhecimento é o mais relevante para responder à questão.

            **Etapa 2: Formular a Resposta.**
            Use o campo "Texto_Base" do documento que você identificou como a sua única fonte de verdade. Elabore uma resposta aprofundada, original e bem explicada para o cidadão. Não copie o texto, sintetize-o com a sua personalidade de especialista.

            **Etapa 3: Citar a Fonte.**
            No final da sua resposta, numa nova linha, cite a fonte usando o campo "Fonte" do documento que você utilizou.

            ---
            **Problema do Cidadão:**
            "{user_problem}"
            ---
            **Base de Conhecimento (Ficheiro JSON):**
            {knowledge_base_text}
            ---
            """
            
            # <<< A CORREÇÃO FINAL E DEFINITIVA ESTÁ AQUI >>>
            # Usando o nome do modelo mais recente, rápido e estável
            model = genai.GenerativeModel('gemini-1.5-flash-latest', system_instruction=system_instruction)
            
            response = model.generate_content(final_prompt)
            ai_answer = response.text

        except Exception as e:
            # Se qualquer passo acima falhar, a mensagem de erro exata será a resposta.
            error_message = f"ERRO DE DIAGNÓSTICO DO SERVIDOR:\n\nTIPO DE ERRO: {type(e).__name__}\n\nMENSAGEM: {str(e)}"
            ai_answer = error_message

        # --- 4. ENVIO DA RESPOSTA FINAL (OU DO ERRO) ---
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset-utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        response_data = json.dumps({'solution': ai_answer})
        self.wfile.write(response_data.encode('utf-8'))