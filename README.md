# Credit Card Advisor
A web-based, Groq-powered credit card recommendation system built with Flask, SQLite, and Streamlit.
Features

Conversational agent powered by Groq's Llama3-70b-8192 model.
SQLite database with 25 Indian credit cards, including images.
Recommendation engine that matches cards to user preferences (income, spending, benefits).
Streamlit UI with chat interface, recommendation summary with card images, and comparison table.

Setup

Clone the repository:git clone <repo-url>
cd credit-card-advisor


Backend:cd backend
pip install -r requirements.txt
export GROQ_API_KEY=<your-key>
python app.py


Frontend:cd frontend
pip install -r requirements.txt
streamlit run app.py


Database:
Data is loaded from data/cards.json (20 cards) into data/credit_cards.db on first run.



Agent Flow

The agent asks questions in sequence: income, spending (fuel, travel, groceries, dining), preferred benefits, existing cards, and credit score.
Responses are validated (e.g., numeric for income, "none" for existing cards).
User data is stored in-memory and used for recommendations.

Prompt Design

Uses Groq's API for context-aware Q&A.
Example prompt: "You are a friendly credit card recommendation assistant. Based on the conversation history: {history}, ask this question: {question}."

Deployment on Render

Backend:
Push to GitHub (backend/ directory).
Create a Web Service on Render:
Root Directory: backend
Runtime: Python 3
Build Command: pip install -r requirements.txt
Start Command: gunicorn --bind 0.0.0.0:$PORT app:app
Add Persistent Disk: Mount Path /app/data, Size 1 GB
Environment Variables: GROQ_API_KEY, DB_PATH=/app/data/credit_cards.db, PYTHON_VERSION=3.10




Frontend:
Push to GitHub (frontend/ directory).
Create a Web Service on Render:
Root Directory: frontend
Runtime: Python 3
Build Command: pip install -r requirements.txt
Start Command: streamlit run app.py --server.port $PORT --server.address 0.0.0.0
Environment Variables: BACKEND_URL=<backend-url>, PYTHON_VERSION=3.10





Demo
[Link to demo video/GIF]
Deployed Link
[Link to Render frontend deployment]
