import tkinter as tk
from tkinter import messagebox
import threading
import pyttsx3
import speech_recognition as sr
import cv2
import os
import webbrowser
import pyautogui
import time
import dlib
import numpy as np
import wikipedia
import urllib.parse

# Initialize text-to-speech
engine = pyttsx3.init()

# Configure voice
def set_funny_accent():
    voices = engine.getProperty('voices')
    for voice in voices:
        if "english" in voice.name.lower() and "male" in voice.name.lower():
            engine.setProperty('voice', voice.id)
            break
    engine.setProperty('rate', 160)
    engine.setProperty('volume', 1.0)
set_funny_accent()

def speak(text):
    engine.say(text)
    engine.runAndWait()

# === Dlib Face Recognition Setup ===
detector = dlib.get_frontal_face_detector()
shape_predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")  # Download required
face_rec_model = dlib.face_recognition_model_v1("dlib_face_recognition_resnet_model_v1.dat")  # Download required

# Load your reference image and get encoding
def get_face_descriptor(image_path):
    img = cv2.imread(image_path)
    if img is None:
        return None
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    dets = detector(img_rgb, 1)
    if len(dets) == 0:
        return None
    shape = shape_predictor(img_rgb, dets[0])
    face_descriptor = face_rec_model.compute_face_descriptor(img_rgb, shape)
    return np.array(face_descriptor)

# Reference encoding of your face
reference_encoding = get_face_descriptor("CV photo.jpg")
if reference_encoding is None:
    print("Error: Could not find or encode the reference image 'test.jpg'. Make sure the image exists and contains a clear face.")
    speak("Reference image missing or invalid. Cannot run face recognition.")
    exit(1)

def face_distance(face_encodings, face_to_compare):
    return np.linalg.norm(face_encodings - face_to_compare)

def recognize_face():
    cap = cv2.VideoCapture(0)
    recognized = False
    start_time = time.time()
    TIMEOUT = 20  # seconds to try recognizing
    
    speak("Starting face recognition. Look at the camera please.")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            speak("Camera error. Please check your camera.")
            break
        
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        faces = detector(img_rgb)
        
        for face in faces:
            shape = shape_predictor(img_rgb, face)
            face_descriptor = face_rec_model.compute_face_descriptor(img_rgb, shape)
            face_encoding = np.array(face_descriptor)
            
            dist = face_distance(reference_encoding, face_encoding)
            threshold = 0.6  # typical threshold for dlib face recognition
            
            if dist < threshold:
                recognized = True
                cv2.putText(frame, "Recognized: Satya Sarthak Manohari", (face.left(), face.top()-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            else:
                cv2.putText(frame, "Unknown Face", (face.left(), face.top()-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            # Draw rectangle
            cv2.rectangle(frame, (face.left(), face.top()), (face.right(), face.bottom()), (255, 0, 0), 2)
        
        cv2.imshow("Face Recognition - Press Q to quit", frame)
        
        if recognized:
            speak("Welcome Satya Sarthak Manohari!")
            time.sleep(1)
            break
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        
        # Timeout
        if time.time() - start_time > TIMEOUT:
            break

    cap.release()
    cv2.destroyAllWindows()
    return recognized

# Password fallback if face recognition fails
def password_fallback():
    speak("Face not recognized. Please say the secret password.")
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        try:
            audio = recognizer.listen(source, timeout=7)
            password = recognizer.recognize_google(audio).lower()
            if "april" in password:
                speak("Password accepted.")
                return True
            else:
                speak("Incorrect password.")
                return False
        except Exception:
            speak("Could not understand the password.")
            return False

# Verify identity using face recognition or password fallback
def verify_identity():
    if recognize_face():
        return True
    else:
        return password_fallback()

# Execute voice commands
def execute_command(command):
    command = command.lower()
    if "youtube" in command:
        speak("Opening YouTube!")
        webbrowser.open("https://www.youtube.com")
    elif "music" in command:
        speak("Playing music!")
        webbrowser.open("https://www.youtube.com/watch?v=k0Ka-deab1s")
    elif "play" in command:
        speak("Playing meditation music!")
        webbrowser.open("https://www.youtube.com/watch?v=lRQ4VTcAljU")
    elif "open linkedin" in command:
        speak("Opening LinkedIn!")
        webbrowser.open("https://www.linkedin.com")
    elif "notepad" in command:
        open_notepad_and_type()
    elif "wikipedia" in command:
        search_query = command.split("wikipedia",1)[-1].strip()
        search_wikipedia(search_query)
    elif "gali" in command:
        speak("You need therapy. Please contact your nearest mental hospital.")
    elif "creator" in command:
        speak("My creator is the ultimate coder, the best hacker, the one and only beast Kabbali aka Satya Sarthak Manohari.")
    elif "dhoni" in command:
        speak("I don't like to talk about credit stealers! Please retire him soon!")
    elif "quit" in command or "exit" in command:
        stop_assistant()
    else:
        search_google(command)

def open_notepad_and_type():
    speak("Opening Notepad!")
    os.system("notepad")
    time.sleep(2)
    pyautogui.typewrite("How can I help you today?")
    pyautogui.press("enter")

def search_wikipedia(query):
    if not query:
        speak("Please specify what to search!")
        return
    try:
        speak(f"Searching Wikipedia for {query}!")
        result = wikipedia.summary(query, sentences=2)
        speak("Here's what I found: " + result)
        messagebox.showinfo("Wikipedia Result", result)
    except Exception as e:
        speak("Wikipedia search failed!")
        print("Error:", e)

def search_google(query):
    if query:
        encoded_query = urllib.parse.quote_plus(query)
        speak(f"Searching Google for {query}!")
        webbrowser.open(f"https://www.google.com/search?q={encoded_query}")
    else:
        speak("What should I search?")

def stop_assistant():
    speak("Goodbye!")
    root.destroy()

def start_assistant():
    # Verify identity first before listening
    if verify_identity():
        threading.Thread(target=listen).start()

def listen():
    speak("Hi I'm April! How can I help you?")
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        while True:
            try:
                audio = recognizer.listen(source, timeout=10)
                command = recognizer.recognize_google(audio)
                execute_command(command)
            except sr.UnknownValueError:
                speak("Could you repeat that?")
            except sr.RequestError:
                speak("Internet connection issue!")
            except Exception as e:
                print("Error:", e)

# === GUI Setup ===
root = tk.Tk()
root.title("AI Assistant - April")
root.geometry("500x400")

try:
    bg_image = tk.PhotoImage(file="AI.png")
    bg_label = tk.Label(root, image=bg_image)
    bg_label.place(relwidth=1, relheight=1)
except Exception as e:
    print("Background image error:", e)

label = tk.Label(root, text="Secure AI Assistant", font=("Helvetica", 18), bg="lightblue")
label.pack(pady=20)

start_btn = tk.Button(root, text="Start", command=start_assistant,
                      font=("Arial", 14), bg="green", fg="white")
start_btn.pack(pady=10)

exit_btn = tk.Button(root, text="Exit", command=stop_assistant,
                     font=("Arial", 14), bg="red", fg="white")
exit_btn.pack(pady=10)

root.mainloop()
