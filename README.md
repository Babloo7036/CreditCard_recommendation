# Credit Card Recommendation System: Project Report

## 1. Project Overview
The Credit Card Recommendation System is a web-based application designed to assist users in selecting the most suitable credit cards from a dataset of 20 Indian credit cards. The system leverages a conversational agent powered by Groq's Llama3-70b-8192 model to collect user preferences (e.g., income, spending habits, preferred benefits) through a question-and-answer interface. It uses a recommendation engine to match user inputs with credit card attributes, displays results with card images via a Streamlit frontend, and stores card data in a SQLite database managed by a Flask backend. The project was developed within a 3-day timeline, focusing on functionality, user experience, and deployability on Render.

## 2. Objectives
- **Primary Goal**: Develop a system to recommend Indian credit cards based on user inputs (income, spending on fuel/travel/groceries/dining, preferred benefits, existing cards, credit score).
- **Secondary Goals**:
  - Implement a conversational agent using Groq's API for dynamic, context-aware Q&A.
  - Store and query credit card data in a SQLite database.
  - Provide a user-friendly Streamlit interface with card images, recommendation summaries, and comparison tables.
  - Deploy the application on Render with persistent storage for the database.
  - Ensure robust input validation and error handling.
  - Integrate a dataset of 20 Indian credit cards with attributes like name, issuer, annual fee, reward type, reward rate, eligibility, perks, apply link, and image URL.

## 3. Technologies Used
- **Backend**:
  - **Flask (2.3.2)**: Lightweight Python web framework for API endpoints.
  - **SQLite**: Embedded database for storing credit card data.
  - **Groq (0.11.0)**: API client for Llama3-70b-8192 model, used for conversational agent.
  - **Gunicorn (22.0.0)**: WSGI server for production deployment.
- **Frontend**:
  - **Streamlit (1.38.0)**: Python framework for interactive web UI.
  - **Requests (2.31.0)**: HTTP client for API communication.
- **Other**:
  - **Python (3.10)**: Programming language for all components.
  - **JSON**: Format for the credit card dataset.
  - **Render**: Cloud platform for deployment with persistent disk support.
  - **GitHub**: Version control and repository hosting.

## 4. System Architecture
The system is divided into three main components:

1. **Backend (Flask)**:
   - **API Endpoints**:
     - `/start_session`: Initiates a new user session, returning a session ID and the first question.
     - `/submit_answer`: Processes user answers, validates inputs, and returns the next question.
     - `/get_recommendations`: Generates top 5 card recommendations based on user data.
   - **Database**: SQLite stores card data in a `credit_cards` table with fields for name, issuer, annual fee, reward type, reward rate, minimum income, minimum credit score, perks, apply link, and image URL.
   - **Agent**: Groq-powered conversational agent manages Q&A flow, validates inputs, and stores session data in-memory.
   - **Recommendation Engine**: Matches user preferences with card attributes, calculates reward simulations, and ranks cards.

2. **Frontend (Streamlit)**:
   - **UI Components**:
     - Chat interface for Q&A interaction.
     - Recommendation display with expandable cards, including images, details, and apply links.
     - Comparison table for recommended cards.
     - Restart button to clear session state.
   - Communicates with the backend via HTTP requests to the Flask API.

3. **Dataset**:
   - A JSON file (`data/cards.json`) containing 20 Indian credit cards, loaded into the SQLite database on startup.

**Architecture Diagram** (Conceptual):
```
[User] <--> [Streamlit Frontend]
                    |
                    v
[Flask Backend] <--> [SQLite Database]
    |                |
    v                v
[Groq Agent]    [Cards JSON]
```

## 5. Implementation Details

### 5.1 Project Structure
```
credit-card-advisor/
├── backend/
│   ├── app.py              # Flask API
│   ├── agent.py            # Groq-based agent
│   ├── recommendation.py   # Recommendation engine
│   ├── requirements.txt    # Backend dependencies
│   └── data/
│       └── cards.json      # Dataset of 20 cards
├── frontend/
│   ├── app.py             # Streamlit UI
│   ├── requirements.txt   # Frontend dependencies
└── README.md              # Documentation
```

### 5.2 Backend Implementation
- **Flask API (`app.py`)**:
  - Initializes the SQLite database with the `cards.json` dataset.
  - Defines API endpoints for session management and recommendations.
  - Uses platform-independent paths for local and Render environments.
- **Groq Agent (`agent.py`)**:
  - Manages conversational flow with 8 questions: income, spending (fuel, travel, groceries, dining), benefits, existing cards, credit score.
  - Validates inputs (e.g., numeric for income, "none" for existing cards) and uses Groq to generate context-aware questions and error messages.
  - Stores user data in-memory per session.
- **Recommendation Engine (`recommendation.py`)**:
  - Parses complex reward rates (e.g., "5% on online, 1% others") using regex.
  - Calculates scores based on eligibility, spending patterns, benefits, and fee affordability.
  - Simulates annual rewards for cashback (INR) and other types (points, miles, etc.).
  - Returns top 5 recommendations with details and reasons.
- **Database**:
  - SQLite table `credit_cards` stores card data, including the new `img_url` field.
  - Initialized with 20 cards from `cards.json` on startup.

### 5.3 Frontend Implementation
- **Streamlit UI (`app.py`)**:
  - Displays a chat interface for user interaction with the Groq agent.
  - Shows recommendations in expandable sections with card images (via `img_url`), annual fee, reward type, perks, reward simulation, reasons, and apply links.
  - Includes a comparison table and restart functionality.
  - Communicates with the Flask backend using environment-configurable URLs.

### 5.4 Dataset Integration
- **Dataset**: A JSON file with 20 Indian credit cards, including:
  - Fields: `name`, `issuer`, `annual_fee`, `reward_type`, `reward_rate`, `eligibility` (min_income, min_credit_score), `perks`, `apply_link`, `img_url`.
  - Examples: "Cashback SBI Credit Card" (5% online cashback), "HDFC Bank INFINIA Metal Credit Card" (premium points-based card).
- **Integration**:
  - Loaded into SQLite via `app.py`.
  - `img_url` field used to display card images in Streamlit.
  - Diverse reward types (cashback, points, miles, neucoins, discount, custom, fuel points) handled by the recommendation engine.

### 5.5 Deployment
- **Platform**: Render, chosen for its support for Python apps and persistent storage.
- **Backend**:
  - Deployed as a Web Service with Gunicorn.
  - Persistent disk at `/app/data` for SQLite (`credit_cards.db`).
  - Environment variables: `GROQ_API_KEY`, `DB_PATH=/app/data/credit_cards.db`, `PYTHON_VERSION=3.10`.
- **Frontend**:
  - Deployed as a separate Web Service running Streamlit.
  - Environment variables: `BACKEND_URL` (backend URL), `PYTHON_VERSION=3.10`.
- **Process**:
  - Pushed to GitHub, connected to Render.
  - Configured build and start commands for each service.
  - Tested live URLs for functionality.

## 6. Challenges and Solutions
1. **SQLite Path Issues**:
   - **Challenge**: Local runs failed with `sqlite3.OperationalError: unable to open database file` due to a Render-specific path (`/app/data/credit_cards.db`).
   - **Solution**: Updated `app.py` to use `os.path` for platform-independent paths, defaulting to `data/credit_cards.db` locally and supporting `DB_PATH` for Render.
2. **Validation Bug for Existing Cards**:
   - **Challenge**: The agent repeatedly asked the "existing cards" question when answered with "none" due to a faulty validation function.
   - **Solution**: Fixed `agent.py` by implementing `validate_existing_cards` to accept "none" or non-empty strings, returning `None` for valid inputs.
3. **Diverse Reward Types**:
   - **Challenge**: The initial recommendation engine only handled cashback and points, but the final dataset included miles, neucoins, discount, custom, and fuel points.
   - **Solution**: Enhanced `recommendation.py` with a `parse_reward_rate` function using regex to extract rates for specific categories and updated reward simulation logic.
4. **Image Integration**:
   - **Challenge**: The final dataset included `img_url`, requiring database and UI updates.
   - **Solution**: Added `img_url` to the SQLite schema and displayed images in Streamlit using `st.image`.
5. **Deployment Configuration**:
   - **Challenge**: Ensuring SQLite persistence and cross-service communication on Render.
   - **Solution**: Used a persistent disk for SQLite and configured `BACKEND_URL` in the frontend to point to the backend’s Render URL.

## 7. Testing
- **Unit Testing**:
  - **Agent**: Tested Q&A flow for context retention (e.g., referencing income in spending questions) and validation (e.g., rejecting negative income, accepting "none" for existing cards).
  - **Recommendation Engine**: Verified card rankings for various inputs (e.g., high dining spend → Swiggy HDFC card prioritized).
  - **Database**: Confirmed all 20 cards loaded correctly with `img_url`.
- **Integration Testing**:
  - Tested API endpoints (`/start_session`, `/submit_answer`, `/get_recommendations`) using `curl` and Postman.
  - Verified frontend-backend communication via Streamlit UI.
- **UI Testing**:
  - Checked chat interface, recommendation display (including images), and comparison table in Streamlit.
  - Ensured restart functionality cleared session state.
- **Edge Cases**:
  - Handled "unknown" credit score, zero spending, and invalid inputs (e.g., "abc" for income).
  - Tested multiple concurrent sessions for isolation.
- **Deployment Testing**:
  - Verified Render deployment for both services, checking database persistence and image loading.

## 8. Results
- **Functionality**: The system successfully collects user preferences, validates inputs, and recommends the top 5 credit cards with detailed reasons and reward simulations.
- **User Experience**: The Streamlit UI is intuitive, with a clean chat interface, expandable recommendation cards with images, and a comparison table.
- **Performance**: Local runs are fast (sub-second API responses), and Render deployment is responsive despite free-tier spindown delays.
- **Dataset**: All 20 cards are integrated, with accurate reward calculations for diverse types.
- **Deployment**: Live on Render with persistent SQLite storage and secure Groq API key management.

## 9. Future Enhancements
- **WhatsApp Integration**: Add a WhatsApp bot using Twilio for conversational access, constrained by the 3-day timeline in this iteration.
- **Advanced Recommendation**:
  - Incorporate machine learning (e.g., collaborative filtering) for personalized rankings.
  - Add filters for user-specified criteria (e.g., no annual fee).
- **User Profiles**: Store user data in a database for returning users.
- **Analytics**: Track user interactions (e.g., popular cards, common inputs) for insights.
- **UI Improvements**:
  - Add card image carousels or tooltips for perks.
  - Support dark mode and responsive design for mobile.
- **Dataset Expansion**: Include more cards (50+) and update dynamically via web scraping or APIs.

## 10. Conclusion
The Credit Card Recommendation System meets all project requirements, delivering a functional, user-friendly, and deployable solution within the 3-day timeline. The integration of Groq’s conversational agent, a robust recommendation engine, and a visually appealing Streamlit UI with card images provides a seamless experience for users seeking Indian credit cards. Despite challenges like SQLite path issues and validation bugs, all were resolved efficiently, ensuring a polished product. The system is live on Render, ready for demonstration, and extensible for future enhancements.

## 11. Appendices

### 11.1 Key Artifacts
- **Backend (`app.py`)**: Flask API with SQLite integration.
- **Agent (`agent.py`)**: Groq-powered conversational logic.
- **Recommendation (`recommendation.py`)**: Scoring and reward simulation.
- **Frontend (`app.py`)**: Streamlit UI with image display.
- **Dataset (`cards.json`)**: 20 Indian credit cards.
- **README**: Setup and deployment instructions.

### 11.2 Deployment Details
- **Backend URL**: [e.g., https://credit-card-backend.onrender.com]
- **Frontend URL**: [e.g., https://credit-card-frontend.onrender.com]
- **GitHub Repository**: [Link to repo]
- **Demo Video**: [Link to demo video/GIF]

### 11.3 Acknowledgments
- **Groq**: For providing the Llama3-70b-8192 model API.
- **Render**: For hosting the application.
- **Streamlit**: For enabling rapid UI development.

---

**Prepared by**: [Your Name]  
**Date**: June 18, 2025  
**Contact**: [Your Contact Info]
