# HumanIza MVP - Assistente de Integração e Carreira

## 🚀 Setup em 5 Minutos

### 1. Gerar Dataset Sintético

```bash
cd data
pip install faker
python generate_profiles.py
```

Isso criará `profiles.csv` com 200 perfis.

### 2. Configurar Backend

```bash
cd ../backend
pip install -r requirements.txt
```

**Configurar API Gemini (opcional mas recomendado):**
1. Acesse: https://makersuite.google.com/app/apikey
2. Crie uma API key gratuita
3. Copie `.env.example` para `.env`:
   ```bash
   cp .env.example .env
   ```
4. Edite `.env` e cole sua chave:
   ```
   GEMINI_API_KEY=SUA_CHAVE_AQUI
   ```

**Iniciar servidor:**
```bash
python app.py
```

O backend estará rodando em `http://localhost:5000`

### 3. Abrir Frontend

Em outra janela do terminal:

```bash
cd ../frontend
# Abrir com servidor HTTP simples
python -m http.server 8000
```

Ou simplesmente abra `index.html` direto no navegador.

Acesse: `http://localhost:8000`

---

## 📸 Como Demonstrar

### 1. Chat com a Iza
- Pergunte: "quais são os benefícios?"
- Pergunte: "qual o horário de trabalho?"
- Veja respostas inteligentes (se configurou Gemini) ou FAQs

### 2. Encontrar Mentor
- Preencha: "Python, Liderança, Comunicação"
- Interesses: "Inovação, Tecnologia"
- Clique "Buscar Mentores"
- Veja top 3 recomendações com % de match

### 3. Missões Gamificadas
- Marque as 4 missões
- Veja progresso e badges

---

## 🐛 Troubleshooting

**Backend não inicia:**
- Certifique-se de instalar: `pip install -r requirements.txt`
- Verifique se profiles.csv existe em `../data/`

**Chat não responde:**
- Se não configurou Gemini: use as perguntas dos FAQs (benefícios, horário, férias, cultura, treinamento)
- Verifique console do navegador (F12)

**Matching não funciona:**
- Certifique-se de que o backend está rodando
- Abra http://localhost:5000/health para verificar

**CORS error:**
- Certifique-se de que flask-cors está instalado
- Ou abra o HTML direto (sem servidor)

---

## 📊 Estrutura do Projeto

```
cursotiaos-global-solutions-1sem-grupo10/
├── data/
│   ├── generate_profiles.py  ← Gera 200 perfis
│   └── profiles.csv          ← Dataset gerado
├── backend/
│   ├── app.py               ← Flask API
│   ├── requirements.txt     ← Dependências Python
│   ├── .env                 ← API keys (não commitar!)
│   └── .env.example         ← Template para .env
├── frontend/
│   ├── index.html           ← Interface principal
│   ├── style.css            ← Estilos
│   ├── app.js               ← Lógica do frontend
│   └── r_analysis/
│       └── eda.html         ← Dashboard Analytics (gerado do R)
└── r_analysis/
    └── eda.Rmd              ← Análise exploratória em R
```

---

## 🔑 API Endpoints

- `POST /chat` - Chatbot (body: `{question: "..."}`)
- `POST /recommend` - Matching (body: `{skills: "...", interests: "..."}`)
- `GET /profiles` - Ver todos os perfis
- `GET /health` - Status do servidor
