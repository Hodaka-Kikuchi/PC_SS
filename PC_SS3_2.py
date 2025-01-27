import tkinter as tk
from tkinter import filedialog, messagebox
import time
import os
import threading
import win32gui
import win32api
import win32ui
import win32con

class ScreenshotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Screenshot Tool")
        self.screenshot_interval = tk.StringVar(value="10")
        self.save_folder = tk.StringVar(value=os.getcwd())
        self.selected_window_title_1 = tk.StringVar(value="未選択")
        self.selected_window_title_2 = tk.StringVar(value="未選択")
        self.running = False

        # GUIレイアウト
        tk.Label(root, text="スクリーンショット保存先:").grid(row=0, column=0, sticky="w")
        tk.Entry(root, textvariable=self.save_folder, width=50).grid(row=0, column=1)
        tk.Button(root, text="フォルダ選択", command=self.select_folder).grid(row=0, column=2)

        # アプリケーション1
        tk.Label(root, text="対象アプリケーション1:").grid(row=1, column=0, sticky="w")
        tk.Entry(root, textvariable=self.selected_window_title_1, width=50, state="readonly").grid(row=1, column=1)
        tk.Button(root, text="アプリ1選択", command=self.select_window_1).grid(row=1, column=2)

        # アプリケーション2
        tk.Label(root, text="対象アプリケーション2:").grid(row=2, column=0, sticky="w")
        tk.Entry(root, textvariable=self.selected_window_title_2, width=50, state="readonly").grid(row=2, column=1)
        tk.Button(root, text="アプリ2選択", command=self.select_window_2).grid(row=2, column=2)

        tk.Label(root, text="スクリーンショット間隔 (秒):").grid(row=3, column=0, sticky="w")
        tk.Entry(root, textvariable=self.screenshot_interval, width=10).grid(row=3, column=1, sticky="w")

        self.start_button = tk.Button(root, text="開始", command=self.start_screenshots)
        self.start_button.grid(row=4, column=0, columnspan=2)

        self.stop_button = tk.Button(root, text="終了", command=self.stop_screenshots, state="disabled")
        self.stop_button.grid(row=4, column=2)

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.save_folder.set(folder)

    def select_window_1(self):
        messagebox.showinfo("ウィンドウ選択", "対象のアプリケーション1ウィンドウをクリックしてください。")
        selected_window = self.get_window_title_on_click()
        if selected_window:
            self.selected_window_title_1.set(selected_window)

    def select_window_2(self):
        messagebox.showinfo("ウィンドウ選択", "対象のアプリケーション2ウィンドウをクリックしてください。")
        selected_window = self.get_window_title_on_click()
        if selected_window:
            self.selected_window_title_2.set(selected_window)

    def get_window_title_on_click(self):
        """クリックされたウィンドウのタイトルを取得"""
        previous_title = None
        while True:
            current_title = self.get_window_title_under_cursor()
            if current_title != previous_title:
                previous_title = current_title
            
            if win32api.GetAsyncKeyState(0x01) < 0:  # 左クリック
                return current_title
            time.sleep(0.1)

    def get_window_title_under_cursor(self):
        hwnd = win32gui.WindowFromPoint(win32gui.GetCursorPos())
        return win32gui.GetWindowText(hwnd) if hwnd else None

    def start_screenshots(self):
        if self.running:
            messagebox.showwarning("実行中", "すでにスクリーンショット取得が実行されています。")
            return

        try:
            interval = int(self.screenshot_interval.get())
        except ValueError:
            messagebox.showerror("エラー", "スクリーンショット間隔は整数で指定してください。")
            return

        if not self.selected_window_title_1.get() or self.selected_window_title_1.get() == "未選択":
            messagebox.showerror("エラー", "アプリケーション1ウィンドウを選択してください。")
            return

        if not self.selected_window_title_2.get() or self.selected_window_title_2.get() == "未選択":
            messagebox.showerror("エラー", "アプリケーション2ウィンドウを選択してください。")
            return

        if not os.path.isdir(self.save_folder.get()):
            messagebox.showerror("エラー", "保存先フォルダを正しく指定してください。")
            return

        self.running = True
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        threading.Thread(target=self.screenshot_loop, args=(interval,), daemon=True).start()
        messagebox.showinfo("開始", "スクリーンショットの取得を開始しました。")

    def stop_screenshots(self):
        if not self.running:
            return
        self.running = False
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        messagebox.showinfo("終了", "スクリーンショットの取得を停止しました。")

    def screenshot_loop(self, interval):
        try:
            while self.running:
                #timestamp = time.strftime("%Y%m%d_%H%M%S")
                #output_path_1 = os.path.join(self.save_folder.get(), f"screenshot_1_{timestamp}.bmp")
                #output_path_2 = os.path.join(self.save_folder.get(), f"screenshot_2_{timestamp}.bmp")
                
                output_path_1 = os.path.join(self.save_folder.get(), f"screenshot_1.bmp")
                output_path_2 = os.path.join(self.save_folder.get(), f"screenshot_2.bmp")

                # 2つのアプリケーションのスクリーンショットを同時に取得
                if not self.capture_window(self.selected_window_title_1.get(), output_path_1) or \
                        not self.capture_window(self.selected_window_title_2.get(), output_path_2):
                    messagebox.showerror("エラー", "スクリーンショットの取得に失敗しました。")
                    self.running = False
                    break
                time.sleep(interval)
        except Exception as e:
            messagebox.showerror("エラー", f"予期せぬエラー: {e}")
        finally:
            self.running = False
            self.start_button.config(state="normal")
            self.stop_button.config(state="disabled")

    def capture_window(self, window_title, output_path):
        rect = self.get_window_rect(window_title)
        if not rect:
            return False

        left, top, right, bottom = rect
        width = right - left
        height = bottom - top

        hwnd = win32gui.FindWindow(None, window_title)
        hwindc = win32gui.GetWindowDC(hwnd)
        srcdc = win32ui.CreateDCFromHandle(hwindc)
        memdc = srcdc.CreateCompatibleDC()
        bmp = win32ui.CreateBitmap()
        bmp.CreateCompatibleBitmap(srcdc, width, height)
        memdc.SelectObject(bmp)

        memdc.BitBlt((0, 0), (width, height), srcdc, (0, 0), win32con.SRCCOPY)
        bmp.SaveBitmapFile(memdc, output_path)

        memdc.DeleteDC()
        win32gui.ReleaseDC(hwnd, hwindc)
        win32gui.DeleteObject(bmp.GetHandle())
        return True

    def get_window_rect(self, window_title):
        hwnd = win32gui.FindWindow(None, window_title)
        if hwnd:
            return win32gui.GetWindowRect(hwnd)
        return None


if __name__ == "__main__":
    root = tk.Tk()
    app = ScreenshotApp(root)
    root.mainloop()

