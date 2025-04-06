import requests
import json
from datetime import datetime
import os
import logging

from google import genai
from google.genai import types
from typing import List, Dict, Any, Optional


# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Replace with your Canvas instance URL and access token
BASE_URL = "https://vcccd.instructure.com/api/v1"
ACCESS_TOKEN = "5499~ka4kBzAAPBUWWE6QFcaUVQkJnDfuMnGQCX8KTW2fuxhTkmvNxx99vhUQ8Weu3V4E"

matthew_api = "5499~VxDt62xrv2F8zGT7wG9c6zzmJuYNZTDG2FTJaGRhED7nm6CHCDtAh4W7tkxm7NDw"



def make_request(endpoint: str, params: Optional[Dict[str, Any]] = None) -> Optional[requests.Response]:
    """Helper function to make API requests with better error handling
    
    Args:
        endpoint (str): The API endpoint to call.
        params (Optional[Dict[str, Any]]): Query parameters for the API request.

    Returns:
        Optional[requests.Response]: The response object if the request is successful, otherwise None.
    """
    try:
        headers: Dict[str, str] = {
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Accept": "application/json"
        }
        url: str = f"{BASE_URL}/{endpoint}"
        logger.debug(f"Making request to: {url}")
        
        response: requests.Response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        return response
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {str(e)}")
        return None

def get_user_profile() -> Optional[Dict[str, Any]]:
    """Get authenticated user's profile with validation
    
    Returns:
        Optional[Dict[str, Any]]: The user's profile as a dictionary if successful, otherwise None.
    """
    response: Optional[requests.Response] = make_request("users/self")
    if response and response.status_code == 200:
        try:
            profile: Dict[str, Any] = response.json()
            # Validate required fields
            if not isinstance(profile, dict):
                logger.error("Invalid profile data structure")
                return None
            return profile
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse user profile: {str(e)}")
            return None
    return None

def get_courses_data() -> Optional[List[Dict[str, Any]]]:
    """Get courses data without printing"""
    params: Dict[str, Any] = {
        'enrollment_state': 'active',
        'include[]': ['term', 'total_students'],
        'per_page': 100
    }
    
    response: Optional[requests.Response] = make_request("courses", params=params)
    if response and response.status_code == 200:
        return response.json()  # Can be a list of course dicts
    return None

def get_assignments(course_id: int, page: int) -> Dict[str, Any]:
    """Get assignments data with pagination
    
    Args:
        course_id (int): The ID of the course to fetch assignments from.
        page (int): The page number for pagination (default is 1).
    
    Returns:
        Dict[str, Any]: A dictionary containing assignments, current page, and total pages.
    """
    page = page or 1
    params: Dict[str, Any] = {
        'page': page,
        'per_page': 10,
        'include[]': ['submission']
    }
    
    response: Optional[requests.Response] = make_request(f"courses/{course_id}/assignments", params=params)
    if response and response.status_code == 200:
        total_pages: int = int(response.headers.get('Link', '').count('rel="next"')) + page
        return {
            'assignments': response.json(),
            'current_page': page,
            'total_pages': total_pages
        }
    return {'assignments': [], 'current_page': 1, 'total_pages': 1}

def get_modules(course_id: int) -> Optional[List[Dict[str, Any]]]:
    """Get modules data"""
    response = make_request(f"courses/{course_id}/modules")
    if response and response.status_code == 200:
        return response.json()
    return []

def get_announcements_data(course_id: int) -> Optional[List[Dict[str, Any]]]:
    """Get announcements data
    
    Args:
        course_id (int): The ID of the course to fetch announcements from.
    
    Returns:
        Optional[List[Dict[str, Any]]]: A list of announcements as dictionaries if successful, otherwise None.
    """
    params: Dict[str, Any] = {
        "only_announcements": True,
        "order_by": "posted_at",
        "per_page": 10
    }
    response: Optional[requests.Response] = make_request(f"courses/{course_id}/discussion_topics", params=params)
    if response and response.status_code == 200:
        return response.json()
    return None

def create_calendar_event(title, description, start_date, end_date, location):
    """Create a new calendar event"""
    # Get current user to set the correct context
    user = get_user_profile()
    if not user:
        logger.error("Failed to get user profile for calendar event")
        return None

    # Format the payload according to Canvas API specs
    payload = {
        'calendar_event[context_code]': f"user_{user['id']}",  # Specific user context
        'calendar_event[title]': title,
        'calendar_event[description]': description,
        'calendar_event[start_at]': start_date.strftime('%Y-%m-%dT%H:%M:%SZ'),
        'calendar_event[end_at]': end_date.strftime('%Y-%m-%dT%H:%M:%SZ'),
        'calendar_event[location_name]': location or ''
    }
    
    logger.debug(f"Creating calendar event with payload: {payload}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/calendar_events",
            headers={
                "Authorization": f"Bearer {ACCESS_TOKEN}",
                "Accept": "application/json"
            },
            data=payload  # Use data instead of json for form-encoded data
        )
        
        logger.debug(f"Response status: {response.status_code}")
        logger.debug(f"Response content: {response.text}")
        
        if response.status_code in (200, 201):
            logger.info("Calendar event created successfully")
            return response.json()
        else:
            logger.error(f"Failed to create calendar event. Status: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {str(e)}")
        return None

def get_course_files(course_id: int) -> Optional[List[Dict[str, Any]]]:
    """Get all files from a course
    
    Args:
        course_id (int): The ID of the course to fetch files from.
    
    Returns:
        Optional[List[Dict[str, Any]]]: A list of file dictionaries if successful, otherwise None.
    """
    params: Dict[str, Any] = {
        'per_page': 100,  # Maximum files per request
        'sort': 'created_at',
        'order': 'desc'
    }
    
    response: Optional[requests.Response] = make_request(f"courses/{course_id}/files", params=params)
    if response and response.status_code == 200:
        return response.json()
    return None

def get_module_items(course_id: int, module_id: int) -> Optional[List[Dict[str, Any]]]:
    """Get all items within a module
    
    Args:
        course_id (int): The ID of the course.
        module_id (int): The ID of the module.
    
    Returns:
        Optional[List[Dict[str, Any]]]: A list of module items as dictionaries if successful, otherwise None.
    """
    response: Optional[requests.Response] = make_request(f"courses/{course_id}/modules/{module_id}/items")
    if response and response.status_code == 200:
        return response.json()
    return None

def scrape_course_data(course_id: int) -> Dict[str, List[Dict[str, Any]]]:
    """Scrape all relevant data from a course
    
    Args:
        course_id (int): The ID of the course to scrape data from.
    
    Returns:
        Dict[str, List[Dict[str, Any]]]: A dictionary containing modules, files, and assignments data.
    """
    course_data: Dict[str, List[Dict[str, Any]]] = {
        'modules': [],
        'files': [],
        'assignments': []
    }
    
    # Get all modules and their items
    modules: Optional[List[Dict[str, Any]]] = get_modules(course_id)
    if modules:
        for module in modules:
            module_data: Dict[str, Any] = {
                'id': module['id'],
                'name': module['name'],
                'items': get_module_items(course_id, module['id']) or []
            }
            course_data['modules'].append(module_data)
    
    # Get all files
    course_data['files'] = get_course_files(course_id) or []
    
    # Get all assignments (not just the first page)
    page: int = 1
    while True:
        assignments_data: Dict[str, Any] = get_assignments(course_id, page)
        course_data['assignments'].extend(assignments_data['assignments'])
        
        if page >= assignments_data['total_pages']:
            break
        page += 1
    
    return course_data

def get_file_download_url(course_id: int, file_id: int) -> Optional[str]:
    """Get the download URL for a specific file
    
    Args:
        course_id (int): The ID of the course.
        file_id (int): The ID of the file.
    
    Returns:
        Optional[str]: The download URL as a string if successful, otherwise None.
    """
    response: Optional[requests.Response] = make_request(f"courses/{course_id}/files/{file_id}")
    if response and response.status_code == 200:
        file_data: Dict[str, Any] = response.json()
        return file_data.get('url')
    return None

def download_course_file(course_id: int, file_id: int, filename: str) -> bool:
    """Download a specific file from the course
    
    Args:
        course_id (int): The ID of the course.
        file_id (int): The ID of the file to download.
        filename (str): The name to save the downloaded file as.
    
    Returns:
        bool: True if the file was successfully downloaded, False otherwise.
    """
    download_url: Optional[str] = get_file_download_url(course_id, file_id)
    if not download_url:
        logger.error(f"Could not get download URL for file {file_id}")
        return False
        
    try:
        response: requests.Response = requests.get(
            download_url,
            headers={"Authorization": f"Bearer {ACCESS_TOKEN}"}
        )
        response.raise_for_status()
        
        # Create downloads directory if it doesn't exist
        downloads_dir: str = os.path.join(os.path.dirname(__file__), 'downloads')
        os.makedirs(downloads_dir, exist_ok=True)
        
        # Save the file
        file_path: str = os.path.join(downloads_dir, filename)
        with open(file_path, 'wb') as f:
            f.write(response.content)
            
        logger.info(f"Successfully downloaded {filename}")
        return True
        
    except Exception as e:
        logger.error(f"Error downloading file {filename}: {str(e)}")
        return False


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


response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents="Can you get me any assignments at all from any course at all, if you need a course id try and get one, it's okay just give me anything I'm testing your functionality",
    config=config,
)

print(response.text)


