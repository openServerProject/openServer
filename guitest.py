import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import threading
import time
import sys

class ConsolePopup(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Console Output")
        self.geometry("500x300")
        self.text_area = ScrolledText(self, wrap=tk.WORD, state='disabled')
        self.text_area.pack(expand=True, fill='both')
        self.protocol("WM_DELETE_WINDOW", self.hide)

    def hide(self):
        self.withdraw()

    def show(self):
        self.deiconify()

    def append_text(self, text):
        self.text_area.configure(state='normal')
        self.text_area.insert(tk.END, text + '\n')
        self.text_area.configure(state='disabled')
        self.text_area.yview(tk.END)

class RedirectedConsole:
    def __init__(self, console_popup):
        self.console_popup = console_popup

    def write(self, message):
        if message.strip():
            self.console_popup.append_text(message)

    def flush(self):
        pass

def background_task(console_popup):
    for i in range(10):
        print(f"Background task running... {i}")
        time.sleep(1)
    console_popup.append_text("Background task completed.")

def main():
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    console_popup = ConsolePopup(root)
    sys.stdout = RedirectedConsole(console_popup)

    console_popup.show()

    threading.Thread(target=background_task, args=(console_popup,), daemon=True).start()

    root.mainloop()

if __name__ == "__main__":
    main()
