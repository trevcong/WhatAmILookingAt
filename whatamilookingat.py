import pyautogui
import pynput
from openai import OpenAI
import time
from pynput import keyboard
from PIL import ImageGrab
import base64

# OpenAI API Key (replace with your actual key)!! 
OPENAI_API_KEY = ""

start_pos = None
end_pos = None
screenshot_path = "screenshot.png"  # Always override the last screenshot

def on_press(key):
    global start_pos, end_pos
    try:
        if key == keyboard.Key.ctrl_l:
            if start_pos is None:
                start_pos = pyautogui.position()
                print(f"Start position set at: {start_pos}")
            else:
                end_pos = pyautogui.position()
                print(f"End position set at: {end_pos}")
                take_screenshot()
        elif isinstance(key, keyboard.KeyCode) and key.vk == 103:  # NumPad 7
            print("Exit key (NumPad 7) pressed. Exiting...")
            return False  # This stops the keyboard listener
    except Exception as e:
        print(f"Error: {e}")

def take_screenshot():
    global start_pos, end_pos, screenshot_path
    if start_pos and end_pos:
        x1, y1 = start_pos
        x2, y2 = end_pos
        
        left = min(x1, x2)
        top = min(y1, y2)
        right = max(x1, x2)
        bottom = max(y1, y2)
        
        screenshot = ImageGrab.grab(bbox=(left, top, right, bottom))
        screenshot.save(screenshot_path)  # Override previous screenshot
        print(f"Screenshot saved as {screenshot_path}")
        analyze_image(screenshot_path)
        
        start_pos = None
        end_pos = None

def analyze_image(image_path):
    try:
        # Initialize OpenAI client
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        # Read and encode the image to base64
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            data_uri = f"data:image/png;base64,{base64_image}"
        
        # Make the API request using gpt-4o
        response = client.chat.completions.create(
            model="gpt-4o",  # Best model for image analysis as of now
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Describe this image in detail."},
                        {
                            "type": "image_url",
                            "image_url": {"url": data_uri}  # Correct format: object with "url" key
                        }
                    ]
                }
            ],
            max_tokens=300  # Adjust as needed
        )
        print("OpenAI Response:", response.choices[0].message.content)
    except Exception as e:
        print(f"Error analyzing image: {e}")

def main():
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()  # The program exits when '7' on numpad is pressed

if __name__ == "__main__":
    main()
