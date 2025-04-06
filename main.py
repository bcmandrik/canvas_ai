from canvas_wrapper import *


GEMINI_API = "AIzaSyAHbphbMZGE0CEzNH-41egmZLk9HLWDzyU"

# Example usage with the Gemini client
client = genai.Client(api_key=GEMINI_API)

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
)  # Pass the functions themselves


# response = client.models.generate_content(
#     model="gemini-2.0-flash",
#     contents="Can you get any assignments from my phil m02 class ethics? at all from any course at all, if you need a course id try and get one, it's okay just give me anything I'm testing your functionality",
#     config=config,
# )

# print(response.text)



conversation = []  # Initialize conversation

while True:
    # Get user input
    user_input = input("You: ")

    # Exit loop if the user wants to stop
    if user_input.lower() == 'exit':
        print("Ending conversation.")
        break

    # Add user input to conversation history
    conversation.append(types.Content(role="user", parts=[types.Part(text=user_input)]))

    # Make the request to Gemini for the model response
    try:
        response = client.models.generate_content(
            model="models/gemini-1.5-pro",  # Use a valid model name
            contents=conversation,
            config=config
        )
        
        # Get the model's reply
        reply = response.text
        print("Gemini:", reply)

        # Add Gemini's reply to the conversation history
        conversation.append(types.Content(role="model", parts=[types.Part(text=reply)]))

    except Exception as e:
        print(f"Error: {e}")


