from flask import Flask, render_template, request, jsonify
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
api_key = os.getenv("API_KEY")

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

# Route for serving the frontend page
@app.route('/', methods=['GET'])
async def all():
    return jsonify("hi")

# Chat endpoint to handle user messages
@app.route("/chat", methods=["POST"])
def chat_with_llama():
    try:
        # Fetch user input from JSON request
        user_input = request.get_json().get("message")
        
        if not user_input:
            return jsonify({"error": "Message not provided"}), 400

        logger.info(f"Received message: {user_input}")

        # Define the system message (behavior of the chatbot)
        messages = [
            {"role": "system", "content": "You are an educational tutor who patiently answers students' questions, explains concepts clearly, and encourages them to work hard. You are always kind, supportive, and uplifting, ensuring students feel motivated and confident in their learning journey."},
            {"role": "user", "content": user_input}
        ]

        # Make the API call to Groq with the Llama model
        response = client.chat.completions.create(
            model="llama-3.1-70b-versatile",  # Adjust this as needed
            messages=messages,
            temperature=0.7,
            max_tokens=300,
        )

        # Check if response is valid and contains choices
        if not response or not response.choices:
            logger.error("Invalid response from Groq API.")
            return jsonify({"error": "Failed to get a valid response from the Groq API."}), 500

        # Extract chatbot's reply
        bot_reply = response.choices[0].message.content

        # Return chatbot response as JSON
        return jsonify({"reply": bot_reply})

    except Exception as e:
        logger.error(f"Error in /chat endpoint: {e}")
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

