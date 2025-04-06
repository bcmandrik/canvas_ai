import os

from google import genai
from google.genai import types


#THIS IS TERRIBLE HAVING IT BUT ITS TEMPORARY ANYWAYS
GEMINI_API = "AIzaSyAHbphbMZGE0CEzNH-41egmZLk9HLWDzyU"

# Example usage with the Gemini client
tools = types.Tool(function_declarations=[get_courses_data, get_modules])

client = genai.Client(api_key=GEMINI_API)

config = types.GenerateContentConfig(tools=[tools])

response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents="What are the courses I am enrolled in?",
    config=config,
)

if response.candidates[0].content.parts[0].function_call:
    function_call = response.candidates[0].content.parts[0].function_call
    print(f"Function to call: {function_call.name}")
    print(f"Arguments: {function_call.args}")
else:
    print("No function call found in the response.")

    