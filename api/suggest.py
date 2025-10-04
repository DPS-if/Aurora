import os
import json
import pandas as pd
import google.generativeai as genai
from http.server import BaseHTTPRequestHandler
from transformers import pipeline

# PLANO B: Nosso "Motor de Emergência" feito do zero
def run_fallback_system(problem_text, solutions_df):
    print("WARNING: External APIs failed. Activating Fallback System.")
    problem_text_lower = problem_text.lower()
    best_match = None
    highest_score = 0
    
    for index, solution in solutions_df.iterrows():
        score = 0
        for keyword in solution.get('Keywords', []):
            if keyword in problem_text_lower:
                score += 1
        
        if score > highest_score:
            highest_score = score
            best_match = solution
            
    if best_match is not None:
        title = best_match['Solution_Title']
        details = best_match['Solution_Details_EN']
        ai_answer = f"Based on your report, a potential solution is **{title}**. \n\n**Details:** {details} \n\n*(This is a preliminary analysis based on keywords. For a more detailed suggestion, please try again later.)*"
    else:
        ai_answer = "We received your report, but couldn't determine a specific solution at this moment. Our team will analyze it manually. Thank you for your contribution."
        
    return ai_answer

# Classe principal que a Vercel vai usar
class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        user_problem_text = ""
        ai_answer = ""
        try:
            # PLANO A: Tentar usar as IAs externas de alta qualidade
            print("INFO: Initiating Plan A with external APIs.")
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            user_input = json.loads(post_data.decode('utf-8'))
            user_problem_text = user_input.get('problem_text', '')

            GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
            HF_TOKEN = os.environ.get('HUGGING_FACE_TOKEN')
            
            # Validação crucial das chaves
            if not GEMINI_API_KEY or not HF_TOKEN:
                raise ValueError("API keys are not configured in Vercel Environment Variables.")
                
            genai.configure(api_key=GEMINI_API_KEY)
            
            script_dir = os.path.dirname(__file__)
            json_path = os.path.join(script_dir, '..', 'solutions.json')
            with open(json_path, 'r') as f:
                solutions_data = json.load(f)
            solutions_df = pd.DataFrame(solutions_data)
            
            problem_labels = solutions_df['Problem_Tags'].tolist()
            classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli", token=HF_TOKEN)
            classification_result = classifier(user_problem_text, candidate_labels=problem_labels)
            detected_problem = classification_result['labels'][0]
            
            best_solution = solutions_df[solutions_df['Problem_Tags'] == detected_problem].iloc[0]
            
            final_prompt = f"""Act as an expert urban planner. A citizen reported: "{user_problem_text}". The primary issue is '{best_solution['Solution_Title']}'. Your task: Write a constructive response in English. Explain the solution '{best_solution['Solution_Title']}' using these details: "{best_solution['Solution_Details_EN']}". Suggest a simple next step. Keep it concise."""
            generation_model = genai.GenerativeModel('gemini-pro')
            final_response = generation_model.generate_content(final_prompt)
            ai_answer = final_response.text

        except Exception as e:
            # SE QUALQUER COISA NO PLANO A FALHAR, EXECUTE O PLANO B
            print(f"ERROR in Plan A: {e}")
            script_dir = os.path.dirname(__file__)
            json_path = os.path.join(script_dir, '..', 'solutions.json')
            with open(json_path, 'r') as f:
                solutions_data = json.load(f)
            solutions_df = pd.DataFrame(solutions_data)
            ai_answer = run_fallback_system(user_problem_text, solutions_df)

        # Envia a resposta final
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        response = json.dumps({'solution': ai_answer})
        self.wfile.write(response.encode('utf-8'))
        return