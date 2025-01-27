# 全ての画面のSSを取得

import mss
import os
import time
import threading
from tkinter import Tk, Label, Entry, Button, filedialog
from screeninfo import get_monitors

class MultiScreenCapture:
    def __init__(self, root):
        self.root = root
        self.root.title("Multi-Screen Screenshot Tool")

        self.folder_path = ""
        self.interval = 1
        self.is_running = False

        # フォルダ選択
        Label(root, text="Select Save Folder:").grid(row=0, column=0, padx=10, pady=10)
        self.folder_label = Label(root, text="No folder selected", width=40, anchor='w')
        self.folder_label.grid(row=0, column=1, padx=10, pady=10)
        Button(root, text="Choose Folder", command=self.choose_folder).grid(row=0, column=2, padx=10, pady=10)

        # 秒数入力
        Label(root, text="Enter interval (seconds):").grid(row=1, column=0, padx=10, pady=10)
        self.interval_entry = Entry(root)
        self.interval_entry.grid(row=1, column=1, padx=10, pady=10)
        self.interval_entry.insert(0, "60")

        # 開始・停止ボタン
        self.start_button = Button(root, text="Start", command=self.start_capture, state="normal")
        self.start_button.grid(row=2, column=0, padx=10, pady=10)

        self.stop_button = Button(root, text="Stop", command=self.stop_capture, state="disabled")
        self.stop_button.grid(row=2, column=1, padx=10, pady=10)

    def choose_folder(self):
        self.folder_path = filedialog.askdirectory()
        if self.folder_path:
            self.folder_label.config(text=self.folder_path)

    def start_capture(self):
        try:
            self.interval = float(self.interval_entry.get())
            if self.interval <= 0:
                raise ValueError
        except ValueError:
            self.folder_label.config(text="Invalid interval. Enter a positive number.")
            return

        if not self.folder_path:
            self.folder_label.config(text="Please select a folder.")
            return

        self.is_running = True
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        threading.Thread(target=self.capture_screenshots).start()

    def stop_capture(self):
        self.is_running = False
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")

    def capture_screenshots(self):
        #counter = 1
        with mss.mss() as sct:
            while self.is_running:
                for monitor in get_monitors():
                    monitor_name_safe = "".join(c if c.isalnum() else "_" for c in monitor.name)
                    bbox = (monitor.x, monitor.y, monitor.x + monitor.width, monitor.y + monitor.height)
                    
                    screenshot = sct.grab(bbox)
                    #filename = os.path.join(self.folder_path, f"screenshot_monitor_{monitor_name_safe}_{counter}.png")
                    filename = os.path.join(self.folder_path, f"screenshot_monitor_{monitor_name_safe}.png")

                    # Save the screenshot
                    mss.tools.to_png(screenshot.rgb, screenshot.size, output=filename)

                #counter += 1
                time.sleep(self.interval)

if __name__ == "__main__":
    root = Tk()
    app = MultiScreenCapture(root)
    root.mainloop()
    
# cd C:\DATA_HK\python\PC_SS
# pyinstaller -F --noconsole PC_SS2.py