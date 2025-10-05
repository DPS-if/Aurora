import os
import json
import pandas as pd
import google.generativeai as genai
from http.server import BaseHTTPRequestHandler

# Versão Final e Robusta da Aurora - Criada para Diagnóstico e Performance

class handler(BaseHTTPRequestHandler):

    def do_OPTIONS(self):
        # Lida com a permissão de CORS, essencial para a comunicação
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "X-Requested-With, Content-Type")
        self.end_headers()

    def do_POST(self):
        # Onde a magia acontece
        
        # Bloco de segurança principal. Se qualquer coisa aqui dentro falhar,
        # o erro será capturado e uma mensagem de erro será enviada.
        try:
            # --- 1. CONFIGURAÇÃO E VALIDAÇÃO ---
            print("[AURORA] Nova requisição recebida. Iniciando processo...")

            # Valida a chave de API do Gemini imediatamente
            GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
            if not GEMINI_API_KEY:
                raise ValueError("ERRO CRÍTICO: Chave GEMINI_API_KEY não foi encontrada nas Environment Variables da Vercel.")
            
            genai.configure(api_key=GEMINI_API_KEY)
            print("[AURORA] Chave API e Gemini configurados com sucesso.")

            # Carrega a base de conhecimento (solutions.json)
            script_dir = os.path.dirname(__file__)
            json_path = os.path.join(script_dir, '..', 'solutions.json')
            with open(json_path, 'r', encoding='utf-8') as f:
                solutions_data = json.load(f)
            
            # Valida se o JSON não está vazio
            if not solutions_data:
                raise ValueError("ERRO CRÍTICO: O ficheiro solutions.json está vazio ou mal formatado.")
            
            print(f"[AURORA] Base de conhecimento carregada com {len(solutions_data)} itens.")

            # --- 2. EXTRAÇÃO DOS DADOS DO UTILIZADOR ---
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            user_input = json.loads(post_data.decode('utf-8'))
            
            user_problem = user_input.get('problem_text', '')
            # Extrai cidade e país do problema, caso existam no prompt do index.html
            context_parts = user_problem.split("relata o seguinte problema:")
            context = context_parts[0].strip() if len(context_parts) > 1 else "Local não especificado"

            # --- 3. CLASSIFICAÇÃO INTERNA (USANDO PALAVRAS-CHAVE) ---
            # Abordagem mais simples e robusta que usar um modelo externo para classificar
            best_match = None
            highest_score = 0
            for solution in solutions_data:
                score = 0
                for keyword in solution.get('Keywords', '').split(','):
                    if keyword.strip() in user_problem.lower():
                        score += 1
                if score > highest_score:
                    highest_score = score
                    best_match = solution
            
            if not best_match:
                raise ValueError("Não foi encontrada nenhuma solução correspondente na base de conhecimento para o problema descrito.")
            
            print(f"[AURORA] Problema classificado na categoria: {best_match['Categoria']}")

            # --- 4. GERAÇÃO DA RESPOSTA COM O GEMINI ---
            
            # A personalidade da Aurora, definida como uma instrução de sistema
            system_instruction = "Você é a Aurora, uma IA pesquisadora especialista em mudanças climáticas e desenvolvimento urbano sustentável. Seja sempre simpática, direta e apresente os dados com a confiança de uma académica. Use uma linguagem clara, mas não simplifique excessivamente os conceitos."
            
            # O prompt final, refinado para uma resposta de alta qualidade
            final_prompt = f"""
            **Contexto da Análise:**
            - **Local:** {context}
            - **Problema Apresentado:** {user_problem}

            **Sua Missão como Pesquisadora:**
            Com base **exclusivamente** no texto académico da sua fonte de conhecimento abaixo, elabore uma resposta aprofundada para o problema apresentado.

            **Fonte de Conhecimento (Texto-Base):**
            - **Título do Conceito:** {best_match['Categoria']}
            - **Texto:** "{best_match['Texto_Base']}"

            **Estrutura Obrigatória da Resposta:**
            1.  **Diagnóstico:** Comece por enquadrar o problema do cidadão dentro do conceito técnico do seu Texto-Base.
            2.  **Análise Detalhada:** Elabore sobre a definição e a importância do conceito, sintetizando as informações do Texto-Base numa explicação original e coesa.
            3.  **Conclusão e Fonte:** Apresente uma breve conclusão e, numa nova linha no final, cite a sua fonte da seguinte forma: "Fonte da Análise: {best_match['Fonte']}".
            """
            
            print("[AURORA] A enviar o prompt final para o modelo Gemini...")
            model = genai.GenerativeModel('gemini-pro', system_instruction=system_instruction)
            response = model.generate_content(final_prompt)
            ai_answer = response.text
            print("[AURORA] Resposta gerada com sucesso pelo Gemini.")

        except Exception as e:
            # Se qualquer passo acima falhar, este bloco será executado
            print(f"!!!!!!!!!!!!!! ERRO CRÍTICO NO SERVIDOR !!!!!!!!!!!!!!")
            print(f"TIPO DE ERRO: {type(e).__name__}")
            print(f"MENSAGEM DE ERRO DETALHADA: {e}")
            print(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            ai_answer = "Peço desculpa, mas encontrei um problema interno ao processar a sua análise. A nossa equipa técnica já foi notificada do erro exato. Por favor, tente novamente mais tarde."

        # --- 5. ENVIO DA RESPOSTA FINAL ---
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        response_data = json.dumps({'solution': ai_answer})
        self.wfile.write(response_data.encode('utf-8'))
        print("[AURORA] Resposta enviada ao utilizador. Processo concluído.")