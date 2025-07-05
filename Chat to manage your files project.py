import tkinter as tk
from tkinter import filedialog
import os
import threading
import shutil
import datetime
import subprocess

class MiniChatApp:
    """
    A simple, modern, frameless Tkinter chat application with a solid light pink background,
    precise widget placement, and carefully chosen text colors for a clean and pleasing aesthetic.
    The window stays always on top and can be dragged.
    """
    def __init__(self, root):
        self.root = root
        self._x = 0
        self._y = 0

        # UI Colors
        self.light_pink_color = "#191919"
        self.darker_pink_color = "#363636"
        self.general_text_color = "#d4d2d2"
        self.user_message_color = "#f0f2f1"
        self.bot_message_color = "#e3e3e3"
        self.system_message_color = "#7cf7a9"

        # Instance variables to hold folder data, replacing globals
        self.path = ""
        self.filesinfo = []

        self.setup_window()
        self.create_widgets()

    def setup_window(self):
        """Sets up the main window properties."""
        self.root.title("Mini Chat")
        self.root.geometry("350x450")
        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", 1)
        self.root.configure(bg=self.light_pink_color)
        self.root.bind("<ButtonPress-1>", self.start_move)
        self.root.bind("<B1-Motion>", self.on_motion)

    def create_widgets(self):
        """Creates and arranges the widgets directly on the root window."""
        close_button = tk.Button(
            self.root, text="X", command=self.root.destroy,
            bg=self.light_pink_color, fg=self.general_text_color,
            font=("Helvetica", 12, "bold"), relief="flat", borderwidth=0, highlightthickness=0,
            activebackground=self.light_pink_color, activeforeground="#FF0000"
        )
        close_button.place(x=340, y=10, anchor="ne", width=25, height=25)

        folder_button = tk.Button(
            self.root, text="...", command=self.open_folder_dialog,
            bg=self.light_pink_color, fg=self.general_text_color,
            font=("Helvetica", 12, "bold"), relief="flat", borderwidth=0, highlightthickness=0,
            activebackground=self.light_pink_color, activeforeground="#0056b3"
        )
        folder_button.place(x=10, y=10, anchor="nw", width=25, height=25)

        chat_frame = tk.Frame(
            self.root, bg=self.light_pink_color, relief="flat",
            borderwidth=0, highlightthickness=0
        )
        chat_frame.place(x=175, y=45, anchor="n", width=330, height=305)

        self.chat_area = tk.Text(
            chat_frame, wrap=tk.WORD, state='disabled', bg=self.light_pink_color,
            fg=self.general_text_color, font=("Helvetica", 10), relief="flat",
            borderwidth=0, highlightthickness=0, padx=10, pady=10
        )
        self.chat_area.pack(fill="both", expand=True)

        input_frame = tk.Frame(
            self.root, bg=self.light_pink_color, borderwidth=0, highlightthickness=0
        )
        input_frame.place(x=175, y=370, anchor="n", width=390, height=100)

        self.entry_box = tk.Text(
            input_frame, height=3, bg=self.darker_pink_color,
            fg=self.general_text_color, font=("Helvetica", 10), relief="flat",
            highlightthickness=0, borderwidth=0, insertbackground=self.general_text_color
        )
        self.entry_box.pack(side="left", fill="both", expand=True, padx=25, pady=25)
        self.entry_box.bind("<Return>", self.send_message_on_enter)
        self.entry_box.focus_set()

        self.send_button = tk.Button(
            input_frame, text="?", command=self.send_message,
            bg=self.darker_pink_color, fg=self.general_text_color,
            font=("Helvetica", 14, "bold"), relief="flat", borderwidth=0,
            highlightthickness=0, activebackground=self.darker_pink_color,
            activeforeground="#0056b3"
        )
        self.send_button.pack(side="right", fill="y", padx=(0, 25), pady=25)
        self.add_message("Chat to manage your files.\n", "system")

    def add_message(self, message, sender="user"):
        """Adds a message to the chat area with specific formatting."""
        self.chat_area.config(state='normal')
        tag_name = f"{sender}_tag"
        if sender == "user":
            self.chat_area.tag_configure(tag_name, justify='right', foreground=self.user_message_color, font=("Helvetica", 10, "bold"))
        elif sender == "bot":
            self.chat_area.tag_configure(tag_name, justify='left', foreground=self.bot_message_color, font=("Helvetica", 10))
        else: # system
            self.chat_area.tag_configure(tag_name, justify='center', foreground=self.system_message_color, font=("Helvetica", 15, "bold italic"))
        self.chat_area.insert(tk.END, message + "\n\n", tag_name)
        self.chat_area.config(state='disabled')
        self.chat_area.yview(tk.END)

    def send_message(self, event=None):
        """Handles getting user input and displaying messages."""
        user_input = self.entry_box.get("1.0", tk.END).strip()
        if user_input:
            self.add_message(user_input, "user")
            self.entry_box.delete("1.0", tk.END)

            #Message Chat handaling Agent
            prompt = "System prompt: you are an AI that manages files, your job is to reply the user that you are moving file to a custom name folder or delete a file or leave the file. The user may be causal too  DONOT USE ' or any symbol, so you have to reply the user that you are working on (that user command to do) PLEASE WAIT, DO NOT ASK FOR CONFIRMATION FOR DELETE, IMPORTANT SYSTEM PROMPT DO NOT IGNORE: DONOT USE SYMBOLYS OR SPECIAL CHARACHERS including ', be a intellegant ai model , User prompt:"
            Final_prompt = prompt + " " + user_input

            process = subprocess.Popen(['ollama', 'run', 'gemma3:4b'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True, creationflags=subprocess.CREATE_NO_WINDOW)
            bot_reply, error = process.communicate(Final_prompt + '\n')

            # Schedule the next step, passing the user_input and bot_reply directly
            self.root.after(500, lambda: self.bot_response(user_input, bot_reply))

        return "break"

    def send_message_on_enter(self, event):
        """Binds the Enter key to send a message."""
        self.send_message()
        return "break"

    def bot_response(self, user_command, bot_message):
        """FIX: Accepts arguments instead of reading globals, then starts the agent thread."""
        self.add_message(bot_message, "bot")
        
        # Start the agent thread, passing the necessary data as arguments
        thread = threading.Thread(target=self.Ai_working_agent, args=(user_command, self.path, self.filesinfo))
        thread.start()

    def Ai_working_agent(self, user_command, folder_path, files_to_process):
        """FIX: Accepts arguments, removing all reliance on globals."""
        if not all([user_command, folder_path, files_to_process]):
            print("Agent stopped: Missing command, folder path, or file list.")
            return

        for filename_with_date in files_to_process:
            actual_file_name = filename_with_date.split(' ')[0].strip()
            full_file_path = os.path.join(folder_path, actual_file_name)

            if not os.path.isfile(full_file_path):
                print(f"Skipping non-existent file: {full_file_path}")
                continue

            # --- Deletion Logic ---
            if 'delete' in user_command.lower():
                prompt1 = "System Prompt: You are a deletion-focused AI agent. Carefully Analyze the user's command. "
                prompt2 = f"User Command: '{user_command}'. File to consider: '{filename_with_date}'. "
                prompt3 = "Does the user's command request deleting this specific file Compare the name, extension, or date compare with the user command . Reply with only 'yes' or 'no'."
                final_prompt = prompt1 + prompt2 + prompt3

                process_del = subprocess.Popen(['ollama', 'run', 'gemma3:4b'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True, creationflags=subprocess.CREATE_NO_WINDOW)
                output_del, _ = process_del.communicate(final_prompt + '\n')
                decision_del = output_del.strip().lower()

                print(f"Deletion agent decision for '{actual_file_name}': {decision_del}")
                if decision_del == 'yes':
                    try:
                        os.remove(full_file_path)
                        print(f"Success: Deleted '{actual_file_name}'.")
                        self.root.after(0, lambda: self.add_message(f"Deleted: {actual_file_name}", "system"))
                    except OSError as e:
                        print(f"Error deleting file '{actual_file_name}': {e}")
                continue # IMPORTANT: After checking for delete, move to the next file

            # --- Folder Creation/Move Logic ---
            prompt1_mov = "System Prompt: You are a file organization AI agent, that carefully analyses this following user command that carefully analyses this following user command "
            prompt2_mov = f"User Command: '{user_command}'. File to consider: '{filename_with_date}'. "
            prompt3_mov = "If the command asks to move this file to a folder, reply with ONLY a suitable folder name. Otherwise, reply with ONLY the word 'none'."
            final_prompt_mov = prompt1_mov + prompt2_mov + prompt3_mov
            
            process_mov = subprocess.Popen(['ollama', 'run', 'gemma3:4b'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True, creationflags=subprocess.CREATE_NO_WINDOW)
            output_mov, _ = process_mov.communicate(final_prompt_mov + '\n')
            decision_mov = output_mov.strip()
            
            print(f"Move agent decision for '{actual_file_name}': {decision_mov}")
            if decision_mov.lower() != 'none' and decision_mov != '':
                target_folder_name = decision_mov
                target_folder_full_path = os.path.join(folder_path, target_folder_name)
                destination_file_full_path = os.path.join(target_folder_full_path, actual_file_name)
                
                try:
                    os.makedirs(target_folder_full_path, exist_ok=True)
                    shutil.move(full_file_path, destination_file_full_path)
                    print(f"SUCCESS: Moved '{actual_file_name}' to '{target_folder_name}'.")
                    self.root.after(0, lambda: self.add_message(f"Moved {actual_file_name} to {target_folder_name}", "system"))
                except (shutil.Error, OSError) as e:
                    print(f"ERROR moving file '{actual_file_name}': {e}")

    def open_folder_dialog(self):
        """Opens a file dialog to select a folder and then processes that folder."""
        folder_path = filedialog.askdirectory()
        os.startfile(folder_path)
        if folder_path:
            # FIX: Use instance variables instead of globals
            self.path = folder_path
            files_info = []
            try:
                for filename in os.listdir(folder_path):
                    file_path = os.path.join(folder_path, filename)
                    if os.path.isfile(file_path):
                        try:
                            timestamp = os.path.getctime(file_path)
                            creation_date = datetime.datetime.fromtimestamp(timestamp)
                            formatted_date = creation_date.strftime("%Y-%m-%d")
                            files_info.append(f"{filename} {formatted_date}")
                        except OSError as e:
                            print(f"Error accessing file '{filename}': {e}")
                
                # FIX: Store in instance variable
                self.filesinfo = files_info
                self.add_message(f"Selected folder: {os.path.basename(folder_path)}\nFound {len(self.filesinfo)} files.", "system")
                print(f"Successfully collected info for {len(self.filesinfo)} files.")
            except Exception as e:
                print(f"An unexpected error occurred during file listing: {e}")

    def start_move(self, event):
        self._x = event.x
        self._y = event.y

    def on_motion(self, event):
        deltax = event.x - self._x
        deltay = event.y - self._y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")

if __name__ == "__main__":
    root = tk.Tk()
    app = MiniChatApp(root)
    root.mainloop()
