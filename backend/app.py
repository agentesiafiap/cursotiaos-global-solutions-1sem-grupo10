"""
Backend Flask simples para o HumanIza MVP
Endpoints: /chat, /recommend, /profiles
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import csv
import os
from dotenv import load_dotenv
import google.generativeai as genai
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Configuração
load_dotenv()
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "OPTIONS"], "allow_headers": ["Content-Type"]}})

# Handler CORS adicional
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Configurar Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-pro')
else:
    model = None
    print("⚠️  GEMINI_API_KEY não configurada. Bot usará respostas mock.")

# Carregar perfis
PROFILES = []
import os
PROFILES_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'profiles.csv')

def load_profiles():
    """Carrega perfis do CSV"""
    global PROFILES
    if os.path.exists(PROFILES_PATH):
        with open(PROFILES_PATH, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            PROFILES = list(reader)
        print(f"✅ {len(PROFILES)} perfis carregados")
    else:
        print(f"⚠️  Arquivo {PROFILES_PATH} não encontrado")

load_profiles()

# FAQs básicos
FAQS = {
    "benefícios": "Os benefícios incluem: vale-refeição, plano de saúde, vale-transporte e gympass. Acesse o portal RH para mais detalhes.",
    "horário": "O horário padrão é das 9h às 18h, com 1h de almoço. Temos flexibilidade para home office 2x por semana.",
    "férias": "Você tem direito a 30 dias de férias após 12 meses. Pode dividir em até 3 períodos.",
    "cultura": "Nossa cultura valoriza inovação, colaboração e diversidade. Incentivamos o aprendizado contínuo.",
    "treinamento": "Oferecemos plataformas de e-learning, workshops mensais e budget anual de R$ 1.000 para cursos externos.",
}

@app.route('/chat', methods=['POST', 'OPTIONS'])
def chat():
    """Endpoint do chatbot usando Gemini ou respostas mock"""
    if request.method == 'OPTIONS':
        return '', 204
    
    data = request.json
    question = data.get('question', '').lower()
    
    # Buscar em FAQs primeiro
    for key, answer in FAQS.items():
        if key in question:
            return jsonify({
                'answer': answer,
                'source': 'faq'
            })
    
    # Se não encontrar, usar Gemini
    if model:
        try:
            prompt = f"""Você é a Iza, assistente de RH amigável da empresa HumanIza.
Responda de forma breve e útil (máximo 3 frases):

Pergunta: {question}
"""
            response = model.generate_content(prompt)
            return jsonify({
                'answer': response.text,
                'source': 'gemini'
            })
        except Exception as e:
            print(f"Erro Gemini: {e}")
            return jsonify({
                'answer': 'Desculpe, não consegui processar sua pergunta. Tente perguntar sobre benefícios, horário, férias ou cultura.',
                'source': 'error'
            })
    else:
        return jsonify({
            'answer': 'Configure GEMINI_API_KEY no .env para usar o bot inteligente. Por enquanto, pergunte sobre: benefícios, horário, férias, cultura ou treinamento.',
            'source': 'mock'
        })

@app.route('/recommend', methods=['POST', 'OPTIONS'])
def recommend():
    """Sistema de recomendação usando TF-IDF"""
    if request.method == 'OPTIONS':
        return '', 204
    
    data = request.json
    user_skills = data.get('skills', '')
    user_interests = data.get('interests', '')
    
    if not PROFILES:
        return jsonify({'error': 'Perfis não carregados'}), 500
    
    # Combinar skills e interests do usuário
    user_text = f"{user_skills} {user_interests}".lower()
    
    # Preparar textos dos mentores disponíveis
    mentors = [p for p in PROFILES if p.get('disponivel_mentoria') == 'True']
    
    if not mentors:
        return jsonify({'recommendations': []})
    
    mentor_texts = []
    for m in mentors:
        text = f"{m.get('habilidades', '')} {m.get('interesses', '')}".lower()
        mentor_texts.append(text)
    
    # TF-IDF
    vectorizer = TfidfVectorizer()
    all_texts = [user_text] + mentor_texts
    tfidf_matrix = vectorizer.fit_transform(all_texts)
    
    # Calcular similaridade
    user_vector = tfidf_matrix[0:1]
    mentor_vectors = tfidf_matrix[1:]
    similarities = cosine_similarity(user_vector, mentor_vectors)[0]
    
    # Top 3
    top_indices = np.argsort(similarities)[-3:][::-1]
    
    recommendations = []
    for idx in top_indices:
        mentor = mentors[idx]
        score = float(similarities[idx])
        
        # Explicabilidade simples
        user_skills_list = set(user_skills.lower().split(','))
        mentor_skills_list = set(mentor.get('habilidades', '').lower().split(','))
        common_skills = user_skills_list & mentor_skills_list
        
        recommendations.append({
            'id': mentor['id'],
            'nome': mentor['nome'],
            'departamento': mentor['departamento'],
            'cargo': mentor['cargo'],
            'score': int(score * 100),
            'habilidades': mentor.get('habilidades', ''),
            'interesses': mentor.get('interesses', ''),
            'explicacao': f"Skills em comum: {', '.join(list(common_skills)[:3]) if common_skills else 'Perfil complementar'}"
        })
    
    return jsonify({'recommendations': recommendations})

@app.route('/profiles', methods=['GET'])
def get_profiles():
    """Retorna todos os perfis (para debug)"""
    return jsonify({'profiles': PROFILES, 'total': len(PROFILES)})

@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        'status': 'ok',
        'profiles_loaded': len(PROFILES),
        'gemini_configured': GEMINI_API_KEY is not None
    })

if __name__ == '__main__':
    print("\n🤝 HumanIza Backend iniciado!")
    print("📍 Endpoints disponíveis:")
    print("   - POST /chat - Chatbot")
    print("   - POST /recommend - Recomendação de mentores")
    print("   - GET /profiles - Ver perfis")
    print("   - GET /health - Status\n")
    
    app.run(debug=True, port=5001, host='0.0.0.0')
