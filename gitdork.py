import os
import re
import shutil
import requests
from zipfile import ZipFile
from colorama import Fore, Style

def get_github_repo_link():
    while True:
        github_repo_link = input("Enter the GitHub repository link (type 'exit' to quit): ").strip()
        if github_repo_link.lower() == 'exit':
            return None
        if github_repo_link:
            return github_repo_link
        print("Invalid input. Please provide a valid GitHub repository link.")

while True:
    # Get the GitHub repository link from the user.
    github_repo_link = get_github_repo_link()
    if not github_repo_link:
        break

    local_repo_path = os.path.join(os.getcwd(), "github_repo")  # Create a subdirectory for the local repository.

    # Clone the GitHub repository to the local path.
    repo_name = github_repo_link.split('/')[-1]
    zip_url = f"{github_repo_link}/archive/master.zip"

    response = requests.get(zip_url, stream=True)
    if response.status_code == 200:
        os.makedirs(local_repo_path, exist_ok=True)
        zip_file_path = os.path.join(local_repo_path, f"{repo_name}.zip")
        with open(zip_file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

    # Unzip the repository contents.
    with ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(local_repo_path)

    # Remove the downloaded zip file.
    os.remove(zip_file_path)

    # Get the filename of the script.
    script_file_name = os.path.basename(__file__)

    # Define the sensitive information patterns to search for.
    sensitive_patterns = [
        r'\bpassword\b',
        r'\bapikey\b',
        r'\bsecret\b',
        r'\baccess[_]?token\b',
        r'\btoken[_]?secret\b',
        r'\bprivate[_]?key\b',
        r'\bsecret[_]?key\b',
        r'\bencryption[_]?key\b',
        r'\busername\b',
        r'\buser[_]?id\b',
        r'\bemail\b',
        r'\bphone[_]?number\b',
        r'\bssn\b',  # Social Security Number
        r'\bcredit[_]?card\b',
        r'\bpin\b',
        r'\bpassport[_]?number\b',
        r'\bdate[_]?of[_]?birth\b',
        # Add other patterns as needed (e.g., database credentials, AWS keys, etc.).
    ]

    # Function to check if a file is a binary file based on its extension.
    def is_binary_file(file_path):
        binary_extensions = {'.svg', '.png', '.jpg', '.jpeg', '.gif', '.pdf', '.docx', '.xlsx', '.zip'}
        _, ext = os.path.splitext(file_path)
        return ext.lower() in binary_extensions

    # Function to search for sensitive information in a file.
    def search_for_sensitive_info(file_path):
        if is_binary_file(file_path):
            print(f"Skipping binary file: {file_path}")
            return

        # Check if the file is the script file itself, and skip it.
        if os.path.basename(file_path) == script_file_name:
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                file_content = file.readlines()
                for line_number, line in enumerate(file_content, start=1):
                    for pattern in sensitive_patterns:
                        matches = re.finditer(pattern, line, re.IGNORECASE)
                        for match in matches:
                            print(f"Sensitive Information Found in: {file_path}")
                            print(f"Type: {match.group(0)}")

                            # Get the start and end position of the sensitive keyword.
                            start_pos = max(0, match.start() - 20)
                            end_pos = min(len(line), match.end() + 20)

                            # Extract the specific portion of the line with the sensitive keyword.
                            specific_line = line[start_pos:end_pos]

                            # Highlight the sensitive keyword in red.
                            line_with_highlight = line.replace(
                                match.group(0),
                                f"{Fore.RED}{match.group(0)}{Style.RESET_ALL}"
                            )

                            print(f"Line {line_number}: {line_with_highlight.strip()}")
                            print("--------------------------------------------------------")
        except Exception as e:
            print(f"Error occurred while searching in {file_path}: {str(e)}")

    # Recursively search for sensitive information in all files within the local repository.
    for root, _, files in os.walk(local_repo_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            search_for_sensitive_info(file_path)

    # Remove the local repository clone after the search is completed.
    shutil.rmtree(local_repo_path)

print("Script finished execution. The repo has been deleted.")
