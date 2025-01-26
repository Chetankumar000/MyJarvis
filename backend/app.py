from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
from groq import Groq
from flask_cors import CORS
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

# Set up logging for debugging purposes
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Retrieve the API key from environment variables
api_key =os.getenv("API_KEY")# Fallback to default for testing

# Ensure the API key is available, exit if not
if not api_key:
    logger.error("API_KEY is missing from environment variables.")
    exit(1)

# Set the API key in the environment for Groq client
os.environ["GROQ_API_KEY"] = api_key

# Initialize the Groq client
client = Groq(api_key=api_key)

# Initialize Flask app
app = Flask(__name__)

# Enable CORS
CORS(app)

app.secret_key = "your_secret_key"  # Replace with a secure key for session management

# Configure SQLAlchemy Database URI (use SQLite for simplicity)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'  # Change to another DB if needed
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database model for storing chat history
class ChatHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_query = db.Column(db.Text, nullable=False)
    bot_response = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

# Create database tables
with app.app_context():
    db.create_all()

# Route for serving the frontend page
@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Hi"})  # Adjusted for proper response

@app.route("/chat", methods=["POST"])
def chat_with_llama():
    try:
        # Fetch user input from JSON request
        user_input = request.get_json().get("message")

        # Fetch the entire chat history from the database
        history_records = ChatHistory.query.order_by(ChatHistory.timestamp).all()
        chat_history = [
            {"role": "user", "content": record.user_query} if i % 2 == 0 else {"role": "assistant", "content": record.bot_response}
            for i, record in enumerate(history_records)
        ]

        # Include system role at the beginning
        if not chat_history:
            chat_history = [
                {
                    "role": "system",
                    "content": "You are an educational tutor who patiently answers students' questions, explains concepts clearly, and encourages them to work hard. You are always kind, supportive, and uplifting, ensuring students feel motivated and confident in their learning journey."
                }
            ]

        # Add the latest user query to the chat history
        chat_history.append({"role": "user", "content": user_input})

        # Make API call to Groq with Llama model
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # Adjust this as needed
            messages=chat_history,  # Full conversation context sent here
            temperature=0.7,
            max_tokens=1000,
        )

        # Extract chatbot's reply
        bot_reply = response.choices[0].message.content

        try:
            new_entry = ChatHistory(user_query=user_input, bot_response=bot_reply)
            db.session.add(new_entry)
            db.session.commit()
          
        except Exception as e:
            logger.error(f"Database error: {str(e)}")
            return jsonify({"error": "Failed to save chat history"}), 500

        # Return chatbot response as JSON
        return jsonify({"reply": bot_reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Get the PORT from the environment or use 5000 as a fallback
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
