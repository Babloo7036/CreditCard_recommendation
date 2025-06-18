from flask import Flask, request, jsonify
from agent import CreditCardAgent
from recommendation import recommend_cards
import psycopg2
import psycopg2.extras
import json
import os
import logging
import urllib.parse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

agent = CreditCardAgent()

def get_db_connection():
    try:
        db_url = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/credit_cards")
        parsed_url = urllib.parse.urlparse(db_url)
        conn = psycopg2.connect(
            database=parsed_url.path.lstrip('/'),
            user=parsed_url.username,
            password=parsed_url.password,
            host=parsed_url.hostname,
            port=parsed_url.port or 5432
        )
        conn.autocommit = True
        logger.info(f"Connected to PostgreSQL database at {parsed_url.hostname}")
        return conn
    except psycopg2.Error as e:
        logger.error(f"Database connection failed: {str(e)}")
        raise

def init_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS credit_cards (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                issuer TEXT,
                annual_fee INTEGER,
                reward_type TEXT,
                reward_rate TEXT,
                min_income INTEGER,
                min_credit_score INTEGER,
                perks JSONB,
                apply_link TEXT,
                img_url TEXT
            )
        ''')
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "cards.json")
        with open(json_path, 'r') as f:
            cards = json.load(f)
        for card in cards:
            cursor.execute('''
                INSERT INTO credit_cards (name, issuer, annual_fee, reward_type, reward_rate, min_income, min_credit_score, perks, apply_link, img_url)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (name) DO NOTHING
            ''', (
                card['name'],
                card['issuer'],
                card['annual_fee'],
                card['reward_type'],
                card['reward_rate'],
                card['eligibility']['min_income'],
                card['eligibility']['min_credit_score'],
                json.dumps(card['perks']),
                card['apply_link'],
                card['img_url']
            ))
        conn.commit()
        logger.info("Database initialized successfully")
    except (psycopg2.Error, FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise
    finally:
        cursor.close()
        conn.close()

@app.route('/start_session', methods=['POST'])
def start_session():
    try:
        session_id = agent.start_session()
        question = agent.get_next_question(session_id)
        logger.info(f"Started session {session_id}")
        return jsonify({"session_id": session_id, "question": question})
    except Exception as e:
        logger.error(f"Error in start_session: {str(e)}")
        return jsonify({"error": "Failed to start session"}), 500

@app.route('/submit_answer', methods=['POST'])
def submit_answer():
    try:
        data = request.json
        session_id = data['session_id']
        answer = data['answer']
        next_question = agent.process_answer(session_id, answer)
        logger.info(f"Processed answer for session {session_id}")
        return jsonify({"question": next_question})
    except (KeyError, Exception) as e:
        logger.error(f"Error in submit_answer: {str(e)}")
        return jsonify({"error": "Invalid request or server error"}), 400

@app.route('/get_recommendations', methods=['POST'])
def get_recommendations():
    try:
        data = request.json
        session_id = data.get('session_id')
        if not session_id or session_id not in agent.sessions:
            logger.error(f"Invalid or missing session_id: {session_id}")
            return jsonify({"error": "Invalid session ID"}), 400
        
        user_data = agent.get_user_data(session_id)
        if not user_data:
            logger.error(f"No user data found for session {session_id}")
            return jsonify({"error": "Incomplete user data"}), 400

        required_keys = ["income", "spending_fuel", "spending_travel", "spending_groceries", "spending_dining"]
        missing_keys = [k for k in required_keys if k not in user_data]
        if missing_keys:
            logger.error(f"Missing user data keys: {missing_keys}")
            return jsonify({"error": f"Missing data: {', '.join(missing_keys)}"}), 400

        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute('SELECT * FROM credit_cards')
        cards = [dict(row) for row in cursor.fetchall()]
        cursor.close()
        conn.close()

        if not cards:
            logger.error("No cards found in database")
            return jsonify({"error": "No cards available"}), 500

        recommendations = recommend_cards(user_data, cards)
        logger.info(f"Generated recommendations for session {session_id}")
        return jsonify({"recommendations": recommendations})
    except psycopg2.Error as e:
        logger.error(f"Database error in get_recommendations: {str(e)}")
        return jsonify({"error": "Database error"}), 500
    except Exception as e:
        logger.error(f"Error in get_recommendations: {str(e)}")
        return jsonify({"error": "Server error"}), 500

if __name__ == '__main__':
    init_db()
    port = int(os.getenv("PORT", 5000))
    app.run(host='0.0.0.0', port=port)