import os
import requests
from dotenv import load_dotenv
import ipywidgets as widgets
from IPython.display import display
import csv
import json

# Load the API key from the .env file
load_dotenv()
google_api_key = os.getenv('GOOGLE_API_KEY')
UPLOAD_DIRECTORY = "uploads"

def query_google_gemini(prompt, api_key):
    """Queries the Google Gemini 1.5 Flash model."""
    url = f"https://generativelanguage.googleapis.com/v1beta3/models/gemini-1.5-flash:generateText?key={api_key}"

    payload = {
        "prompt": {
            "text": prompt
        }
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        # Make the POST request to Google Gemini API
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

        # Parse the JSON response
        data = response.json()
        # Get the model response from the "candidates"
        return data.get("candidates", [{}])[0].get("output", "No output generated.")
    
    except requests.exceptions.RequestException as e:
        if '400' in str(e) and 'API key not valid' in str(e):
            return "Error: Invalid API key. Please check your .env file."
        else:
            return f"An error occurred during the API request: {str(e)}"
    except json.JSONDecodeError as e:
         return f"Error decoding JSON response: {str(e)}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"


def print_llm_response(prompt):
    """Prints the response from the Google Gemini 1.5 Flash model."""
    # Get the response from the Google Gemini model
    response = query_google_gemini(prompt, google_api_key)
    print(response)


def get_llm_response(prompt):
    """Returns the response from the Google Gemini 1.5 Flash model."""
    if not isinstance(prompt, str):
        return "Error: Input must be a string enclosed in quotes."
    response = query_google_gemini(prompt, google_api_key)
    return response


def read_csv_dict(csv_file_path):
    """This function takes a CSV file and loads it as a dict."""
    data_list = []

    with open(csv_file_path, mode='r') as file:
        csv_reader = csv.DictReader(file)
    
        for row in csv_reader:
            data_list.append(row)

    data_dict = {i: data_list[i] for i in range(len(data_list))}
    return data_dict


def upload_txt_file():
    """Uploads a text file and saves it to the specified directory."""
    upload_widget = widgets.FileUpload(
        accept='.txt',
        multiple=False
    )
    
    output = widgets.Output()
    
    def handle_upload(change):
        with output:
            output.clear_output()
            if not upload_widget.value:
                print("No file uploaded.")
                return
            
            uploaded_file = list(upload_widget.value.values())[0]
            content = uploaded_file['content']
            name = uploaded_file['name']
            size_in_kb = len(content) / 1024

            if size_in_kb > 50:
                print("Your file is too large, please upload a file that doesn't exceed 50KB.")
                return
            
            if not name.lower().endswith(".txt"):
                print("Invalid file format, please upload a '.txt' file.")
                return

            os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)
            file_path = os.path.join(UPLOAD_DIRECTORY, name)

            try:
                with open(file_path, 'wb') as f:
                    f.write(content)
                print(f"The {name} file has been uploaded to the '{UPLOAD_DIRECTORY}' directory.")
            except Exception as e:
                print(f"An error occurred while saving the file: {e}")


    upload_widget.observe(handle_upload, names='value')
    display(upload_widget, output)


def list_files_in_directory(directory='.'):
    """Lists all non-hidden files in the specified directory."""
    try:
        files = [f for f in os.listdir(directory) if (not f.startswith('.') and not f.startswith('_'))]
        for file in files:
            print(file)
    except FileNotFoundError:
            print(f"Error: Directory '{directory}' not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")