import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import speech_recognition as sr
import threading
import time
import os

class VoiceNoteApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Voice Note Taker")
        self.root.geometry("700x900")
        self.root.resizable(False, False)

        # Gradient background using Canvas
        self.canvas = tk.Canvas(root, width=700, height=900)
        self.canvas.pack(fill="both", expand=True)
        self.gradient_background("#1e2f3f", "#5bc0be")

        # Main frame on top of canvas
        self.main_frame = tk.Frame(root, bg="#1e2f3f")
        self.main_frame.place(relwidth=0.9, relheight=0.9, relx=0.05, rely=0.05)

        self.filename = self.get_filename()
        self.is_recording = False
        self.record_thread = None

        self.language_label = tk.Label(
            self.main_frame,
            text="Select language for notes",
            font=("Helvetica", 16, "bold"),
            bg="#1e2f3f",
            fg="#a0c4ff"
        )
        self.language_label.pack(pady=(20,10))

        self.language_var = tk.StringVar(value="en-US")
        self.language_menu = ttk.Combobox(
            self.main_frame,
            textvariable=self.language_var,
            values=["en-US", "hi-IN", "bn-BD"],
            font=("Helvetica", 14),
            state="readonly",
            width=20
        )
        self.language_menu.pack(pady=10)

        # Buttons frame
        self.buttons_frame = tk.Frame(self.main_frame, bg="#1e2f3f")
        self.buttons_frame.pack(pady=15)

        self.record_button = tk.Button(
            self.buttons_frame,
            text="🎤 Start Recording",
            command=self.toggle_recording,
            font=("Helvetica", 14, "bold"),
            bg="#5bc0be",
            fg="#1e2f3f",
            activebackground="#3a5068",
            activeforeground="#ffffff",
            relief="raised",
            bd=3,
            width=20,
            height=2,
            cursor="hand2"
        )
        self.record_button.grid(row=0, column=0, padx=10, pady=5)
        self.add_hover_animation(self.record_button, "#5bc0be", "#3a5068", "#1e2f3f", "#ffffff")

        self.view_button = tk.Button(
            self.buttons_frame,
            text="📄 View File",
            command=self.view_file,
            font=("Helvetica", 14, "bold"),
            bg="#5bc0be",
            fg="#1e2f3f",
            activebackground="#3a5068",
            activeforeground="#ffffff",
            relief="raised",
            bd=3,
            width=20,
            height=2,
            cursor="hand2"
        )
        self.view_button.grid(row=0, column=1, padx=10, pady=5)
        self.add_hover_animation(self.view_button, "#5bc0be", "#3a5068", "#1e2f3f", "#ffffff")

        self.delete_button = tk.Button(
            self.buttons_frame,
            text="🗑️ Delete File",
            command=self.delete_file,
            font=("Helvetica", 14, "bold"),
            bg="#ff6b6b",
            fg="#1e2f3f",
            activebackground="#c94c4c",
            activeforeground="#ffffff",
            relief="raised",
            bd=3,
            width=20,
            height=2,
            cursor="hand2"
        )
        self.delete_button.grid(row=1, column=0, padx=10, pady=5)
        self.add_hover_animation(self.delete_button, "#ff6b6b", "#c94c4c", "#1e2f3f", "#ffffff")

        self.export_button = tk.Button(
            self.buttons_frame,
            text="📤 Export Notes",
            command=self.export_notes,
            font=("Helvetica", 14, "bold"),
            bg="#f6d55c",
            fg="#1e2f3f",
            activebackground="#d4b83d",
            activeforeground="#000000",
            relief="raised",
            bd=3,
            width=20,
            height=2,
            cursor="hand2"
        )
        self.export_button.grid(row=1, column=1, padx=10, pady=5)
        self.add_hover_animation(self.export_button, "#f6d55c", "#d4b83d", "#1e2f3f", "#000000")

        self.exit_button = tk.Button(
            self.buttons_frame,
            text="🚪 Exit",
            command=self.exit_app,
            font=("Helvetica", 14, "bold"),
            bg="#778beb",
            fg="#1e2f3f",
            activebackground="#5d6db3",
            activeforeground="#ffffff",
            relief="raised",
            bd=3,
            width=20,
            height=2,
            cursor="hand2"
        )
        self.exit_button.grid(row=2, column=0, columnspan=2, pady=10)
        self.add_hover_animation(self.exit_button, "#778beb", "#5d6db3", "#1e2f3f", "#ffffff")

        # Notes display with scrollbar
        self.notes_frame = tk.Frame(self.main_frame, bg="#1e2f3f")
        self.notes_frame.pack(pady=20, fill="both", expand=True)

        self.notes_display = tk.Text(
            self.notes_frame,
            font=("Helvetica", 12),
            bg="#2f3e4d",
            fg="#dbe9f4",
            bd=3,
            relief="sunken",
            insertbackground="#dbe9f4",
            wrap="word"
        )
        self.notes_display.pack(side="left", fill="both", expand=True)

        self.scrollbar = ttk.Scrollbar(
            self.notes_frame,
            command=self.notes_display.yview
        )
        self.scrollbar.pack(side="right", fill="y")
        self.notes_display.config(yscrollcommand=self.scrollbar.set)

        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = tk.Label(
            self.root,
            textvariable=self.status_var,
            font=("Helvetica", 10),
            bg="#1e2f3f",
            fg="#a0c4ff",
            anchor="w"
        )
        self.status_bar.pack(side="bottom", fill="x")

    def gradient_background(self, color1, color2):
        width = 700
        height = 900
        limit = height
        (r1, g1, b1) = self.root.winfo_rgb(color1)
        (r2, g2, b2) = self.root.winfo_rgb(color2)
        r_ratio = float(r2 - r1) / limit
        g_ratio = float(g2 - g1) / limit
        b_ratio = float(b2 - b1) / limit

        for i in range(limit):
            nr = int(r1 + (r_ratio * i))
            ng = int(g1 + (g_ratio * i))
            nb = int(b1 + (b_ratio * i))
            color = f'#{nr >> 8:02x}{ng >> 8:02x}{nb >> 8:02x}'
            self.canvas.create_line(0, i, width, i, fill=color)

    def add_hover_animation(self, widget, normal_bg, hover_bg, normal_fg, hover_fg):
        def on_enter(e):
            widget.config(bg=hover_bg, fg=hover_fg)
        def on_leave(e):
            widget.config(bg=normal_bg, fg=normal_fg)
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)

    def get_filename(self):
        date = datetime.now().strftime("%y-%m-%d")
        return f"notes_{date}.txt"

    def toggle_recording(self):
        if self.is_recording:
            self.is_recording = False
            self.record_button.config(text="🎤 Start Recording")
            self.status_var.set("Recording stopped.")
        else:
            self.is_recording = True
            self.record_button.config(text="⏹️ Stop Recording")
            self.status_var.set("Recording started...")
            self.record_thread = threading.Thread(target=self.record_audio)
            self.record_thread.start()

    def record_audio(self):
        recognizer = sr.Recognizer()
        mic = sr.Microphone()
        try:
            with mic as source:
                recognizer.adjust_for_ambient_noise(source)
                while self.is_recording:
                    audio = recognizer.listen(source, phrase_time_limit=5)
                    try:
                        note = recognizer.recognize_google(audio, language=self.language_var.get())
                        timestamp = datetime.now().strftime("%y-%m-%d %H:%M:%S")
                        with open(self.filename, "a", encoding="utf-8") as file:
                            file.write(timestamp + " " + note + "\n")
                        self.notes_display.insert(tk.END, timestamp + " " + note + "\n")
                        self.notes_display.see(tk.END)
                        self.status_var.set("Note recorded.")
                    except Exception as e:
                        self.status_var.set(f"Recognition error: {e}")
        except Exception as e:
            self.status_var.set(f"Microphone error: {e}")
        finally:
            self.is_recording = False
            self.record_button.config(text="🎤 Start Recording")

    def view_file(self):
        try:
            with open(self.filename, "r", encoding="utf-8") as file:
                content = file.read()
            self.notes_display.delete(1.0, tk.END)
            self.notes_display.insert(tk.END, content)
            self.status_var.set("Notes loaded.")
        except FileNotFoundError:
            self.notes_display.delete(1.0, tk.END)
            self.notes_display.insert(tk.END, "No notes file found.\n")
            self.status_var.set("No notes file found.")

    def delete_file(self):
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete the notes?"):
            try:
                if os.path.exists(self.filename):
                    os.remove(self.filename)
                    self.notes_display.delete(1.0, tk.END)
                    self.notes_display.insert(tk.END, "Notes file deleted.\n")
                    self.status_var.set("Notes file deleted.")
                else:
                    self.notes_display.delete(1.0, tk.END)
                    self.notes_display.insert(tk.END, "No notes file to delete.\n")
                    self.status_var.set("No notes file to delete.")
            except Exception as e:
                self.notes_display.delete(1.0, tk.END)
                self.notes_display.insert(tk.END, f"Error deleting file: {e}\n")
                self.status_var.set(f"Error deleting file: {e}")

    def export_notes(self):
        try:
            content = self.notes_display.get(1.0, tk.END)
            if not content.strip():
                self.status_var.set("No notes to export.")
                return
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if file_path:
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(content)
                self.status_var.set(f"Notes exported to {file_path}")
        except Exception as e:
            self.status_var.set(f"Error exporting notes: {e}")

    def exit_app(self):
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = VoiceNoteApp(root)
    root.mainloop()
