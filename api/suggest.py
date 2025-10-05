import os
import json
import google.generativeai as genai
from http.server import BaseHTTPRequestHandler

# Versão Final Simplificada - Foco em Robustez e Personalidade

class handler(BaseHTTPRequestHandler):

    def do_OPTIONS(self):
        # Lida com a permissão de CORS
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "X-Requested-With, Content-Type")
        self.end_headers()

    def do_POST(self):
        ai_answer = ""
        try:
            # --- 1. CONFIGURAÇÃO ---
            print("[AURORA FINAL] Nova requisição recebida.")

            # Valida a chave de API do Gemini
            GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
            if not GEMINI_API_KEY:
                raise ValueError("ERRO CRÍTICO: Chave GEMINI_API_KEY não foi encontrada nas Environment Variables da Vercel.")
            
            genai.configure(api_key=GEMINI_API_KEY)
            print("[AURORA FINAL] Gemini configurado.")

            # Carrega a base de conhecimento (solutions.json)
            script_dir = os.path.dirname(__file__)
            json_path = os.path.join(script_dir, '..', 'solutions.json')
            with open(json_path, 'r', encoding='utf-8') as f:
                solutions_data = json.load(f)
            
            # Converte toda a base de conhecimento num texto que a IA possa ler
            knowledge_base_text = json.dumps(solutions_data, indent=2, ensure_ascii=False)
            
            print("[AURORA FINAL] Base de conhecimento carregada.")

            # --- 2. EXTRAÇÃO DOS DADOS DO UTILIZADOR ---
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            user_input = json.loads(post_data.decode('utf-8'))
            user_problem = user_input.get('problem_text', '')

            # --- 3. UMA ÚNICA CHAMADA PODEROSA AO GEMINI ---
            
            # A personalidade da Aurora, definida como uma instrução de sistema
            system_instruction = "Você é a Aurora, uma IA pesquisadora especialista em mudanças climáticas e desenvolvimento urbano sustentável. Seja sempre simpática, direta e apresente os dados com a confiança de uma académica. Use uma linguagem clara, mas não simplifique excessivamente os conceitos."
            
            # O prompt final e direto
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
            
            print("[AURORA FINAL] A enviar o prompt único e completo para o modelo Gemini...")
            model = genai.GenerativeModel('gemini-pro', system_instruction=system_instruction)
            response = model.generate_content(final_prompt)
            ai_answer = response.text
            print("[AURORA FINAL] Resposta gerada com sucesso.")

        except Exception as e:
            # Se qualquer passo acima falhar, o erro exato será registado
            print(f"!!!!!!!!!!!!!! ERRO CRÍTICO NO SERVIDOR !!!!!!!!!!!!!!")
            print(f"TIPO DE ERRO: {type(e).__name__}")
            print(f"MENSAGEM DE ERRO DETALHADA: {e}")
            print(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            ai_answer = "Peço desculpa, mas encontrei um problema interno ao processar a sua análise. A nossa equipa técnica já foi notificada do erro exato. Por favor, tente novamente mais tarde."

        # --- 4. ENVIO DA RESPOSTA FINAL ---
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        response_data = json.dumps({'solution': ai_answer})
        self.wfile.write(response_data.encode('utf-8'))
        print("[AURORA FINAL] Resposta enviada ao utilizador. Processo concluído.")