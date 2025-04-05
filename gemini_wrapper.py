import os

from google import genai
from google.genai import types


#THIS IS TERRIBLE HAVING IT BUT ITS TEMPORARY ANYWAYS
GEMINI_API = "AIzaSyAHbphbMZGE0CEzNH-41egmZLk9HLWDzyU"

#tool declarations


# Define function declarations for the Gemini model
# get_user_profile = {
#     "name": "get_user_profile",
#     "description": "Retrieves the authenticated user's profile.",
#     "parameters": {
#         "type": "object",
#         "properties": {},
#         "required": []
#     }
# }

# get_courses_data = {
#     "name": "get_courses_data",
#     "description": "Fetches a list of active courses for the authenticated user.",
#     "parameters": {
#         "type": "object",
#         "properties": {},
#         "required": []
#     }
# }

# get_assignments = {
#     "name": "get_assignments",
#     "description": "Retrieves assignments for a specific course with pagination.",
#     "parameters": {
#         "type": "object",
#         "properties": {
#             "course_id": {
#                 "type": "integer",
#                 "description": "The ID of the course."
#             },
#             "page": {
#                 "type": "integer",
#                 "description": "The page number for pagination.",
#                 "default": 1
#             }
#         },
#         "required": ["course_id"]
#     }
# }

# get_modules = {
#     "name": "get_modules",
#     "description": "Fetches all modules for a specific course.",
#     "parameters": {
#         "type": "object",
#         "properties": {
#             "course_id": {
#                 "type": "integer",
#                 "description": "The ID of the course."
#             }
#         },
#         "required": ["course_id"]
#     }
# }

# create_calendar_event = {
#     "name": "create_calendar_event",
#     "description": "Creates a new calendar event for the authenticated user.",
#     "parameters": {
#         "type": "object",
#         "properties": {
#             "title": {
#                 "type": "string",
#                 "description": "The title of the calendar event."
#             },
#             "description": {
#                 "type": "string",
#                 "description": "The description of the calendar event."
#             },
#             "start_date": {
#                 "type": "string",
#                 "description": "The start date and time of the event (ISO 8601 format)."
#             },
#             "end_date": {
#                 "type": "string",
#                 "description": "The end date and time of the event (ISO 8601 format)."
#             },
#             "location": {
#                 "type": "string",
#                 "description": "The location of the event.",
#                 "default": ""
#             }
#         },
#         "required": ["title", "description", "start_date", "end_date"]
#     }
# }

# download_course_file = {
#     "name": "download_course_file",
#     "description": "Downloads a specific file from a course.",
#     "parameters": {
#         "type": "object",
#         "properties": {
#             "course_id": {
#                 "type": "integer",
#                 "description": "The ID of the course."
#             },
#             "file_id": {
#                 "type": "integer",
#                 "description": "The ID of the file to download."
#             },
#             "filename": {
#                 "type": "string",
#                 "description": "The name to save the downloaded file as."
#             }
#         },
#         "required": ["course_id", "file_id", "filename"]
#     }
# }



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

    