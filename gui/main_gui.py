import threading
import time
import pyautogui  # type: ignore
import customtkinter as ctk  # type: ignore
import pygetwindow as gw  # type: ignore
from input.voice_command import get_command
from input.voice_input import listen_for_wake_word
from output.speak import respond
from ai.nlp import ask_gpt
from system.commands import execute_command
from system.read_file import read_file, read_and_summarize_file
from system.folder_map import get_known_folder_path
from system.search_fallback import google_search_fallback  # type: ignore
from system.app_control import launch_app, current_app  # type: ignore
import re
import os
import glob
import traceback


class JARVISApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.chat_history = []  # Reset on app start
        self.listening_thread_started = False  # 🔐 Ensures wake word starts only once

        self.title("JARVIS Assistant")
        self.geometry("600x700")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.animation_running = False
        self.is_destroyed = False

        self.title_label = ctk.CTkLabel(self, text="JARVIS Voice Assistant", font=("Consolas", 22, "bold"))
        self.title_label.pack(pady=10)

        self.canvas = ctk.CTkCanvas(self, width=120, height=120, bg="black", highlightthickness=0)
        self.canvas.pack(pady=20)
        self.bubble = self.canvas.create_oval(10, 10, 110, 110, fill="#00AEEF", outline="#0077AA", width=3)

        self.chat_frame = ctk.CTkFrame(self, height=400, width=560)
        self.chat_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.result_box = ctk.CTkTextbox(self.chat_frame, height=400, wrap="word")
        self.result_box.pack(fill="both", expand=True)
        self.result_box.configure(state="disabled")

        self.entry_frame = ctk.CTkFrame(self)
        self.entry_frame.pack(side="bottom", fill="x", padx=10, pady=10)

        self.user_entry = ctk.CTkEntry(self.entry_frame, placeholder_text="Type your request...", height=40)
        self.user_entry.pack(side="left", fill="x", expand=True, padx=5)
        self.user_entry.bind("<Return>", lambda event: self.process_command(self.user_entry.get()))

        self.listen_button = ctk.CTkButton(self.entry_frame, text="🎙️", width=40, command=self.start_listening)
        self.listen_button.pack(side="right", padx=5)

        threading.Thread(target=self.animate_bubble, daemon=True).start()
        self.after(1000, self.start_listening)  # ✅ Only starts once


    def animate_bubble(self):
        self.animation_running = True
        while self.animation_running and not self.is_destroyed:
            try:
                dx = 5 * abs(time.time() % 1 - 0.5)
                self.canvas.move(self.bubble, dx, 0)
                self.canvas.update_idletasks()
                time.sleep(0.05)
                self.canvas.move(self.bubble, -dx, 0)
                self.canvas.update_idletasks()
            except Exception:
                break

    def start_listening(self):
        if self.listening_thread_started:
            return
        self.listening_thread_started = True
        threading.Thread(target=self.listen_loop_once_then_forever, daemon=True).start()

    def listen_loop_once_then_forever(self):
        while not self.is_destroyed:
            try:
                print("[DEBUG] Waiting for wake word...")
                self.append_message("🔊 Listening for wake word...", "jarvis")
                while not listen_for_wake_word():
                    if self.is_destroyed: 
                        return
                    time.sleep(0.5)

                print("[DEBUG] Wake word detected")
                respond("Yes, how can I help you?")

                while not self.is_destroyed:
                    command = get_command().lower().strip()
                    if not command:
                        respond("Sorry, I didn't catch that. Can you please repeat?")
                        continue

                    print(f"[You said]: {command}")
                    self.process_command(command)

                    if command in ["exit", "quit", "bye"]:
                        return
            except Exception as e:
                print(f"[Voice Loop Error]: {e}")
                traceback.print_exc()
                respond("Something went wrong while listening.")
                time.sleep(1)

    def save_chat_history(self):
        try:
            with open("chat_history.txt", "w", encoding="utf-8") as f:
                f.write("\n".join(self.chat_history))
        except Exception as e:
            print(f"[Save Error]: {e}")

    def process_command(self, command):
        if not command.strip():
            return
        self.user_entry.delete(0, "end")
        self.append_message(f"You: {command}", "user")

        if command in ["exit", "quit", "bye"]:
            respond("Goodbye!")
            self.save_chat_history()
            self.is_destroyed = True
            self.animation_running = False
            self.destroy()
            return

        SECURE_COMMANDS = ["uninstall", "delete", "install"]
        if any(cmd in command.lower() for cmd in SECURE_COMMANDS):
            respond("This action requires confirmation. Please enter your security PIN.")
            self.append_message("JARVIS: Action blocked for security. PIN confirmation required.", "jarvis")
            return

        elif command.startswith("run "):
            shell_cmd = re.sub(r"\s+", "", command.split("run ", 1)[1].strip())
            output = execute_command(shell_cmd)
            respond(output)
            self.append_message(f"JARVIS: {output}", "jarvis")
            return

        elif "system info" in command or "pc info" in command:
            from system.system_info import get_system_info
            reply = get_system_info()
            respond(reply)
            self.append_message(f"JARVIS: {reply}", "jarvis")
            return

        elif "list apps" in command or "installed applications" in command:
            from system.applications import list_installed_apps
            apps = list_installed_apps()
            reply = "Installed applications:\n" + "\n".join(apps[:30])
            respond("Listing installed applications.")
            self.append_message(f"JARVIS:\n{reply}", "jarvis")
            return

        elif command.startswith("open "):
            app_name = command.replace("open ", "").strip()
            launch_app(app_name)
            current_app["name"] = app_name
            respond(f"{app_name} opened.")
            return

        elif any(word in command for word in ["read", "open", "show", "display"]):
            file_path = self.find_matching_file_from_command(command)
            if file_path:
                try:
                    summary = read_and_summarize_file(file_path)
                except Exception:
                    content = read_file(file_path)
                    summary = ask_gpt(f"Summarize:\n{content[:5000]}")
                respond(summary)
                self.append_message(f"JARVIS: {summary}", "jarvis")
            else:
                respond("Couldn't find any file.")
                self.append_message("JARVIS: No file found.", "jarvis")
            return

        if current_app["name"] and current_app["name"].lower() not in gw.getActiveWindowTitle().lower():
            respond("The application doesn't seem to be focused. Please click on it.")
            return

        if "write" in command and current_app["window"]:
            respond("Okay, I will start writing. Say 'save' or 'discard' to finish.")
            self.dictate_mode()
            return

        self.chat_history.append(f"User: {command}")
        context = "\n".join(self.chat_history[-10:])
        reply = ask_gpt(context)

        fail_phrases = [
            "i do not have access", "i cannot provide", "i'm sorry",
            "i recommend checking", "i suggest looking", "unfortunately", "as an ai"
        ]
        if any(phrase in reply.lower() for phrase in fail_phrases):
            reply = google_search_fallback(command)
            reply = reply.replace("*", "")
        else:
            self.chat_history.append(f"JARVIS: {reply}")

        respond(reply)
        self.append_message(f"JARVIS: {reply}", "jarvis")

    def append_message(self, text, sender):
        if self.is_destroyed:
            return
        try:
            self.result_box.configure(state="normal")
            self.result_box.insert("end", f"{text}\n")
            self.result_box.see("end")
            self.result_box.configure(state="disabled")
        except Exception:
            pass

    def find_matching_file_from_command(self, command):
        folder = get_known_folder_path(command)
        if not folder: 
            return None

        extensions = []
        if "pdf" in command:
            extensions = ["*.pdf"]
        elif "text" in command or "txt" in command:
            extensions = ["*.txt"]
        elif "image" in command or "jpg" in command or "png" in command:
            extensions = ["*.jpg", "*.png"]

        files = []
        for ext in extensions:
            files += glob.glob(os.path.join(folder, ext))

        if not files: 
            return None
        files.sort(key=os.path.getmtime)
        return files[0] if "first" in command or "oldest" in command else files[-1]

    def dictate_mode(self):
        full_text = ""
        app_name = current_app.get("name", "")
        target_window = None

        if app_name:
            try:
                windows = gw.getWindowsWithTitle(app_name)
                if windows:
                    target_window = windows[0]
                    target_window.activate()
                    time.sleep(1.5)
            except Exception as e:
                print(f"[Window Activation Error]: {e}")

        if not target_window:
            try:
                active = gw.getActiveWindow()
                if active:
                    target_window = active
            except Exception as e:
                print(f"[Fallback Active Window Error]: {e}")

        if target_window:
            try:
                rect = target_window._rect
                center_x = rect.left + rect.width // 2
                center_y = rect.top + rect.height // 2
                pyautogui.click(center_x, center_y)
                time.sleep(0.5)
            except Exception as e:
                print(f"[Click Error]: {e}")
        else:
            print("[Dictate Mode] No window available to click")

        while True:
            respond("I'm listening...")
            cmd = get_command().lower().strip()

            if "save" in cmd:
                try:
                    pyautogui.typewrite(full_text)
                    pyautogui.hotkey("ctrl", "s")
                    respond("Saved the text.")
                except Exception as e:
                    print(f"[Typing Error]: {e}")
                break
            elif "discard" in cmd:
                respond("Okay, discarding the note.")
                break
            else:
                full_text += cmd + " "


def run_gui():
    app = JARVISApp()
    app.mainloop()
