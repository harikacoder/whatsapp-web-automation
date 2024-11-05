
import os
import pyautogui
import pyperclip
from PIL import Image
import cv2
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

class ActionCopyContent(Action):

    def name(self) -> str:
        return "action_copy_content"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict) -> list:
        try:
           
            directories = ["Text", "Images", "Videos"]
            for directory in directories:
                if not os.path.exists(directory):
                    os.makedirs(directory)

            
            options = webdriver.ChromeOptions()
            options.add_argument('--user-data-dir=./User_Data')
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

            
            driver.get("https://web.whatsapp.com")
            dispatcher.utter_message(text="Opening WhatsApp Web...")

            
            while not driver.find_elements_by_css_selector("canvas[aria-label='Scan me!']"):
                pyautogui.sleep(1)

            pyautogui.hotkey('ctrl', 'c')
            content = pyperclip.paste()
            dispatcher.utter_message(text="Content copied: " + content)

            def save_text(content):
                with open("Text/message.txt", "a") as file:
                    file.write(content + "\n")

            def save_image(image_path):
                img = Image.open(image_path)
                img.save(f"Images/{os.path.basename(image_path)}")

            def save_video(video_path):
                cap = cv2.VideoCapture(video_path)
                out = cv2.VideoWriter(f"Videos/{os.path.basename(video_path)}", cv2.VideoWriter_fourcc(*'XVID'), 20.0, (640, 480))
                while cap.isOpened():
                    ret, frame = cap.read()
                    if ret:
                        out.write(frame)
                    else:
                        break
                cap.release()
                out.release()

            def process_content(content):
                if content.endswith(('.png', '.jpg', '.jpeg')):
                    save_image(content)
                elif content.endswith(('.mp4', '.avi', '.mkv')):
                    save_video(content)
                else:
                    save_text(content)

            process_content(content)
        except Exception as e:
            dispatcher.utter_message(text=f"An error occurred: {e}")
        finally:
            driver.quit()

        return []
