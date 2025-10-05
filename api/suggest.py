import os
import json
import pandas as pd
import google.generativeai as genai
from http.server import BaseHTTPRequestHandler

# Versão Final com Classificação Inteligente via Gemini

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
            # --- 1. CONFIGURAÇÃO E VALIDAÇÃO ---
            print("[AURORA V3] Nova requisição recebida. Iniciando processo...")

            GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
            if not GEMINI_API_KEY:
                raise ValueError("ERRO CRÍTICO: Chave GEMINI_API_KEY não foi encontrada nas Environment Variables da Vercel.")
            
            genai.configure(api_key=GEMINI_API_KEY)
            print("[AURORA V3] Gemini configurado.")

            # Carrega a base de conhecimento
            script_dir = os.path.dirname(__file__)
            json_path = os.path.join(script_dir, '..', 'solutions.json')
            with open(json_path, 'r', encoding='utf-8') as f:
                solutions_data = json.load(f)
            
            if not solutions_data:
                raise ValueError("ERRO CRÍTICO: O ficheiro solutions.json está vazio ou mal formatado.")
            
            solutions_df = pd.DataFrame(solutions_data)
            print(f"[AURORA V3] Base de conhecimento carregada com {len(solutions_data)} itens.")

            # --- 2. EXTRAÇÃO DOS DADOS DO UTILIZADOR ---
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            user_input = json.loads(post_data.decode('utf-8'))
            user_problem = user_input.get('problem_text', '')

            # --- 3. MODELO 1: GEMINI COMO CLASSIFICADOR INTELIGENTE ---
            print("[AURORA V3] Modelo 1 (Classificador) em execução...")
            
            # Cria uma lista de categorias para o Gemini escolher
            category_list = solutions_df['Categoria'].tolist()
            
            classification_prompt = f"""
            Analise o seguinte problema relatado por um cidadão: "{user_problem}".
            Com base neste problema, qual das seguintes categorias é a mais relevante?
            Responda APENAS com o nome exato da categoria da lista abaixo. Não adicione nenhuma outra palavra ou pontuação.

            Lista de Categorias Válidas:
            - {', '.join(category_list)}
            """
            
            classifier_model = genai.GenerativeModel('gemini-pro')
            classification_response = classifier_model.generate_content(classification_prompt)
            # Limpa a resposta para garantir que temos apenas a categoria
            detected_category = classification_response.text.strip().replace("'", "").replace('"', '')
            
            print(f"[AURORA V3] Categoria detectada pelo Gemini: '{detected_category}'")

            # Encontra a solução correspondente na nossa base de dados
            matching_solutions = solutions_df[solutions_df['Categoria'] == detected_category]
            
            if matching_solutions.empty:
                print(f"!!! AVISO: A categoria '{detected_category}' retornada pelo Gemini não corresponde a nenhuma categoria no JSON. A tentar o fallback.")
                # Se o Gemini devolver algo inesperado, ativamos o fallback
                raise ValueError("O classificador de IA retornou uma categoria inválida.")

            best_solution = matching_solutions.iloc[0].to_dict()
            print(f"[AURORA V3] Categoria encontrada na base de conhecimento: {best_solution['Categoria']}")

            # --- 4. MODELO 2: GEMINI COMO PESQUISADORA ESPECIALISTA ---
            print("[AURORA V3] Modelo 2 (Pesquisadora) em execução...")
            
            system_instruction = "Você é a Aurora, uma IA pesquisadora especialista em mudanças climáticas e desenvolvimento urbano sustentável. Seja sempre simpática, direta e apresente os dados com a confiança de uma académica. Use uma linguagem clara, mas não simplifique excessivamente os conceitos."
            
            final_prompt = f"""
            **Contexto da Análise:**
            - **Problema Apresentado:** {user_problem}

            **Sua Missão como Pesquisadora:**
            Com base **exclusivamente** no texto académico da sua fonte de conhecimento abaixo, elabore uma resposta aprofundada para o problema apresentado.

            **Fonte de Conhecimento (Texto-Base):**
            - **Título do Conceito:** {best_solution['Categoria']}
            - **Texto:** "{best_solution['Texto_Base']}"

            **Estrutura Obrigatória da Resposta:**
            1.  **Diagnóstico:** Comece por enquadrar o problema do cidadão dentro do conceito técnico do seu Texto-Base.
            2.  **Análise Detalhada:** Elabore sobre a definição e a importância do conceito, sintetizando as informações do Texto-Base numa explicação original e coesa.
            3.  **Conclusão e Fonte:** Apresente uma breve conclusão e, numa nova linha no final, cite a sua fonte da seguinte forma: "Fonte da Análise: {best_solution['Fonte']}".
            """
            
            researcher_model = genai.GenerativeModel('gemini-pro', system_instruction=system_instruction)
            response = researcher_model.generate_content(final_prompt)
            ai_answer = response.text
            print("[AURORA V3] Resposta final gerada com sucesso.")

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
        print("[AURORA V3] Resposta enviada ao utilizador. Processo concluído.")