import os
import json
import pandas as pd
import google.generativeai as genai
from http.server import BaseHTTPRequestHandler

# Esta classe de handler já inclui a correção de CORS (do_OPTIONS)
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
            # --- ETAPA 1: RECEBER E CONFIGURAR ---
            print("INFO: Iniciando nova arquitetura da Aurora.")
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            user_input = json.loads(post_data.decode('utf-8'))
            
            # Extrai os dados do problema do utilizador
            user_problem = user_input.get('problem_text', '')
            user_city = user_input.get('city', 'Não especificada')
            user_country = user_input.get('country', 'Não especificado')

            # Configura as APIs
            GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
            if not GEMINI_API_KEY:
                raise ValueError("Chave GEMINI_API_KEY não configurada na Vercel.")
            genai.configure(api_key=GEMINI_API_KEY)

            # Carrega a base de conhecimento
            script_dir = os.path.dirname(__file__)
            json_path = os.path.join(script_dir, '..', 'solutions.json')
            with open(json_path, 'r', encoding='utf-8') as f:
                solutions_data = json.load(f)
            solutions_df = pd.DataFrame(solutions_data)
            
            # --- MODELO 1: GEMINI COMO CLASSIFICADOR ---
            print("INFO: Modelo 1 (Gemini-Classificador) em execução...")
            
            # Cria uma lista de categorias para o Gemini escolher
            category_list = solutions_df['Categoria'].tolist()
            
            classification_prompt = f"""
            Analise o seguinte problema relatado por um cidadão: "{user_problem}".
            Com base neste problema, qual das seguintes categorias é a mais relevante?
            Responda APENAS com o nome exato da categoria da lista.

            Lista de Categorias:
            {', '.join(category_list)}
            """
            
            classifier_model = genai.GenerativeModel('gemini-pro')
            classification_response = classifier_model.generate_content(classification_prompt)
            detected_category = classification_response.text.strip()
            print(f"✅ Modelo 1: Categoria detectada -> {detected_category}")

            # Encontra a solução correspondente na nossa base de dados
            matching_solutions = solutions_df[solutions_df['Categoria'] == detected_category]
            if matching_solutions.empty:
                raise ValueError(f"A categoria '{detected_category}' não foi encontrada no ficheiro solutions.json")
            
            best_solution = matching_solutions.iloc[0].to_dict()

            # --- MODELO 2: GEMINI COMO PESQUISADORA ESPECIALISTA ---
            print("INFO: Modelo 2 (Gemini-Pesquisadora) em execução...")

            # Define a personalidade da Aurora (System Instruction)
            system_instruction = "Você é a Aurora, uma IA pesquisadora especialista em mudanças climáticas e desenvolvimento urbano sustentável. Seja sempre simpática, direta e apresente os dados com a confiança de uma académica. Use uma linguagem clara, mas não simplifique excessivamente os conceitos."
            
            # Refina o prompt do utilizador para uma resposta de alta qualidade
            final_prompt = f"""
            **Problema Reportado:**
            Na cidade de **{user_city}, {user_country}**, foi identificado o seguinte desafio: "{user_problem}".

            **Sua Tarefa:**
            Com base no texto-base da sua fonte de conhecimento, elabore uma resposta que seja breve, mas aprofundada.

            **Fonte de Conhecimento (use esta fonte como base principal da sua resposta):**
            - **Título:** {best_solution['Categoria']}
            - **Texto-Base:** {best_solution['Texto_Base']}

            **Estrutura da Resposta:**
            1.  **Saudação e Contextualização:** Comece por se dirigir ao cidadão e enquadrar o problema dele dentro do conceito técnico do seu Texto-Base.
            2.  **Análise Aprofundada:** Explique o conceito do Texto-Base em detalhe. Descreva o porquê de ser relevante para o problema apresentado.
            3.  **Conclusão e Citação:** Termine com uma breve conclusão e cite a sua fonte de forma clara.
            """
            
            researcher_model = genai.GenerativeModel('gemini-pro', system_instruction=system_instruction)
            final_response = researcher_model.generate_content(final_prompt)
            ai_answer = final_response.text

        except Exception as e:
            # Se qualquer etapa falhar, gera uma resposta de erro
            print(f"!!! ERRO CRÍTICO NA EXECUÇÃO: {e} !!!")
            ai_answer = "Peço desculpa, mas encontrei um problema ao processar a sua análise. A nossa equipa técnica já foi notificada. Por favor, tente novamente mais tarde."

        # Envia a resposta final
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        response = json.dumps({'solution': ai_answer})
        self.wfile.write(response.encode('utf-8'))
        return