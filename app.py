from flask import Flask, request, jsonify, render_template
from canvas_wrapper import *
from google import genai
from google.genai import types
from time import strftime, localtime

app = Flask(__name__)

# Initialize Gemini client
client = genai.Client(api_key="AIzaSyAHbphbMZGE0CEzNH-41egmZLk9HLWDzyU")

# Get the current date for the system prompt
today = strftime("%Y-%m-%d", localtime())

# Conversation context (global for simplicity) with system prompt
conversation = [
    types.Content(
        role="model",
        parts=[types.Part(text=(
            "You are a helpful academic assistant who helps students interact with their Canvas dashboard. "
            "You answer questions about assignments, classes, due dates, modules, and announcements. "
            "Be friendly and informative. Ask follow-up questions if needed and always prioritize relevance."
            f"today is {today}"
        ))]
    )
]

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
            model="models/gemini-2.0-flash-lite",  # Use a valid model name
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

