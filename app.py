from flask import Flask, render_template, request, jsonify
import os
from groq import Groq
from flask_cors import CORS

# Set up environment variables
api_key = "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"  # Replace with your actual key
os.environ["GROQ_API_KEY"] = api_key



# Initialize Groq client
client = Groq(api_key=api_key)

# Flask app setup
app = Flask(__name__)

CORS(app)

# Route for serving the frontend page
@app.route("/")
def home():
    return render_template("index.html")  # Make sure to create index.html

# Chat endpoint to handle user messages
@app.route("/chat", methods=["POST"])
def chat_with_llama():
    try:
        # Fetch user input from JSON request
        user_input = request.get_json().get("message")
        print(user_input)

        # Define system message (behavior of the chatbot)
        messages = [
            {"role": "system", "content": "You are an educational tutor who patiently answers students' questions, explains concepts clearly, and encourages them to work hard. You are always kind, supportive, and uplifting, ensuring students feel motivated and confident in their learning journey."},
            {"role": "user", "content": user_input}
        ]

        # Make API call to Groq with Llama model
        response = client.chat.completions.create(
            model="llama-3.1-70b-versatile",  # Adjust this as needed
            messages=messages,
            temperature=0.7,
            max_tokens=300,
        )

        # Extract chatbot's reply
        bot_reply = response.choices[0].message.content

        # Return chatbot response as JSON
        return jsonify({"reply": bot_reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
