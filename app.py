from flask import Flask, request, jsonify, render_template
from canvas_wrapper import *
from google import genai
from google.genai import types

app = Flask(__name__)

# Initialize Gemini client
client = genai.Client(api_key="AIzaSyAHbphbMZGE0CEzNH-41egmZLk9HLWDzyU")

# Conversation context (global for simplicity)
conversation = []

# Configure tools for Gemini
config = types.GenerateContentConfig(
    tools=[
        get_courses_data,
        get_user_profile,
        get_assignments,
        get_modules,
        get_announcements_data,
        get_course_files,
        get_module_items,
        scrape_course_data,
        get_file_download_url,
        download_course_file
    ]
)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    global conversation
    user_input = request.json.get("message", "")

    # Add user input to conversation history
    conversation.append(types.Content(role="user", parts=[types.Part(text=user_input)]))

    try:
        # Generate response from Gemini
        response = client.models.generate_content(
            model="models/gemini-1.5-pro",
            contents=conversation,
            config=config
        )
        reply = response.text

        # Add Gemini's reply to conversation history
        conversation.append(types.Content(role="model", parts=[types.Part(text=reply)]))

        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)