# おおもとの画面のSSのみ取得

import tkinter as tk
from tkinter import filedialog, messagebox
import pyautogui
import os
import time
from threading import Thread

class ScreenshotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Screenshot App")
        self.output_folder = ""
        self.interval = 5
        self.running = False

        # フォルダ選択ボタン
        self.folder_label = tk.Label(root, text="Select output folder:")
        self.folder_label.pack(pady=5)
        self.folder_button = tk.Button(root, text="Choose Folder", command=self.select_folder)
        self.folder_button.pack(pady=5)

        # 秒数入力フィールド
        self.interval_label = tk.Label(root, text="Enter interval (seconds):")
        self.interval_label.pack(pady=5)
        self.interval_entry = tk.Entry(root)
        self.interval_entry.pack(pady=5)
        self.interval_entry.insert(0, "5")

        # 開始・停止ボタン
        self.start_button = tk.Button(root, text="Start", command=self.start_screenshots)
        self.start_button.pack(pady=5)
        self.stop_button = tk.Button(root, text="Stop", command=self.stop_screenshots, state=tk.DISABLED)
        self.stop_button.pack(pady=5)

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_folder = folder
            messagebox.showinfo("Folder Selected", f"Screenshots will be saved in: {folder}")

    def start_screenshots(self):
        try:
            self.interval = int(self.interval_entry.get())
            if self.interval <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid positive integer for the interval.")
            return

        if not self.output_folder:
            messagebox.showerror("No Folder Selected", "Please select a folder to save screenshots.")
            return

        self.running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

        # スクリーンショットスレッドを開始
        Thread(target=self.take_screenshots, daemon=True).start()

    def stop_screenshots(self):
        self.running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def take_screenshots(self):
        while self.running:
            screenshot = pyautogui.screenshot()
            #timestamp = time.strftime("%Y%m%d_%H%M%S")
            #file_path = os.path.join(self.output_folder, f"screenshot_{timestamp}.png")
            file_path = os.path.join(self.output_folder, f"screenshot.png")
            screenshot.save(file_path)
            time.sleep(self.interval)

if __name__ == "__main__":
    root = tk.Tk()
    app = ScreenshotApp(root)
    root.mainloop()
