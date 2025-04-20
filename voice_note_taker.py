import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime
import speech_recognition as sr

# --- Global Variables ---
filename = ""
language = "en-IN"
duration = 5

# --- Functions ---
def choose_file_location():
    global filename
    filename = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt")],
        title="Choose where to save your voice note"
    )
    if filename:
        status_var.set(f"✅ File path set:\n{filename}")

def set_language():
    global language
    selected = lang_var.get()
    language = selected
    status_var.set(f"🌐 Language set to: {language}")

def set_duration():
    global duration
    try:
        duration = int(duration_entry.get())
        status_var.set(f"⏱️ Duration set to {duration} seconds")
    except ValueError:
        status_var.set("❌ Please enter a valid number")

def take_voice_note():
    global filename, language, duration

    if not filename:
        status_var.set("❌ Please choose a file path first.")
        return

    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    try:
        with mic as source:
            recognizer.adjust_for_ambient_noise(source)
            status_var.set(f"🎙️ Recording for {duration} seconds...")
            root.update()
            audio = recognizer.listen(source, phrase_time_limit=duration)
            status_var.set("🧠 Converting audio to text...")

        note = recognizer.recognize_google(audio, language=language)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(filename, "a", encoding="utf-8") as file:
            file.write(f"{timestamp} - {note}\n")

        status_var.set("✅ Note saved successfully!")

    except sr.UnknownValueError:
        status_var.set("⚠️ Could not understand the audio.")
    except sr.RequestError:
        status_var.set("❌ API unavailable. Check your internet.")
    except Exception as e:
        status_var.set(f"❌ Error: {str(e)}")


# --- GUI Setup ---
root = tk.Tk()
root.title("🎤 Voice Note Taker")
root.geometry("500x400")
root.resizable(False, False)

# File Path
tk.Button(root, text="Choose Save File Path", command=choose_file_location, bg="#d9edf7").pack(pady=10)

# Language
tk.Label(root, text="Select Language:").pack()
lang_var = tk.StringVar(value="en-IN")
lang_menu = tk.OptionMenu(root, lang_var, "en-IN", "hi-IN", "fr-FR", "de-DE")
lang_menu.pack(pady=5)
tk.Button(root, text="Set Language", command=set_language, bg="#f7ecb5").pack(pady=5)

# Duration
tk.Label(root, text="Enter Recording Duration (seconds):").pack()
duration_entry = tk.Entry(root)
duration_entry.pack(pady=5)
tk.Button(root, text="Set Duration", command=set_duration, bg="#f7ecb5").pack(pady=5)

# Record Button
tk.Button(root, text="🎙️ Record Note", command=take_voice_note, bg="blue", fg="white", font=("Arial", 12, "bold")).pack(pady=20)

# Status Label
status_var = tk.StringVar()
status_var.set("Ready to record...")
tk.Label(root, textvariable=status_var, fg="green", font=("Arial", 10)).pack(pady=10)

# Main Loop
root.mainloop()
