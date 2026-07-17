# -*- coding: utf-8 -*-
"""
Monikra1n Tool
===================================================
Author: Monikra1n Team
Version: 0.12.4
"""

import os
import sys
import time
import threading
import ctypes
import urllib.request
import zipfile
import subprocess
import io
from tkinter import messagebox

try:
    import customtkinter as ctk
    from PIL import Image
except ImportError:
    print("Lütfen terminali açıp şu komutu girin: pip install customtkinter pillow")
    sys.exit()

ctk.set_appearance_mode("Dark")
BG_COLOR = "#2C2C2E"      
LINE_COLOR = "#48484A"    
TEXT_MAIN = "#FFFFFF"     
TEXT_SUB = "#AEAEB2"      
BTN_COLOR = "#3A3A3C"     
BTN_HOVER = "#505052"     

class Monikra1nApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("monikra1n - Version beta 0.12.4")
        self.geometry("640x460")
        self.resizable(False, False)
        self.configure(fg_color=BG_COLOR)
        
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"640x460+{(screen_width-640)//2}+{(screen_height-460)//2}")

        self.iso_url = "YOUR_ISO_URL"
        self.ifr_url = "YOUR_IFRPFILE_DOWNLOAD_URL"
        self.logo_url = "https://preview.redd.it/question-does-anyone-have-deb-for-the-checkra1n-bootlogo-by-v0-tdprve9fvvf81.jpg?auto=webp&s=6341f8688642859231ef9c018f9693f24793089e"
        
        self.temp_dir = os.environ.get("TEMP", ".")
        self.desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        self.program_files = os.environ.get("PROGRAMFILES", "C:\\Program Files")
        
        self.iso_path = os.path.join(self.temp_dir, "Monikra1n_Checkra1n.iso")
        self.ifr_zip_path = os.path.join(self.temp_dir, "iFrpfile_Temp.zip")
        self.ifr_extract_path = os.path.join(self.program_files, "Monikra1n_iFrpfile")
        self.shortcut_path = os.path.join(self.desktop_path, "iFrpfile.lnk")

        self.is_processing = False
        self.downloaded_logo_img = None  

        self.build_ui()
        self.refresh_drives()
        
        threading.Thread(target=self.load_online_logo, daemon=True).start()

    def update_status(self, text, color="#0A84FF"):
        self.after(0, lambda: self.status_lbl.configure(text=text, text_color=color))

    def show_message(self, title, message):
        self.after(0, lambda: messagebox.showinfo(title, message))

    def build_ui(self):
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", padx=25, pady=(25, 15))

        text_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
        text_frame.pack(side="left", fill="both", expand=True)

        ctk.CTkLabel(text_frame, text="Welcome to monikra1n!", font=("Helvetica", 16, "bold"), text_color=TEXT_MAIN).pack(anchor="w")
        ctk.CTkLabel(text_frame, text="Connect your USB drive to begin jailbreak creation,\nor download iFrpfile tools.", font=("Helvetica", 13), text_color=TEXT_MAIN, justify="left").pack(anchor="w", pady=(5, 0))

        self.logo_label = ctk.CTkLabel(top_frame, text="♚", font=("Helvetica", 45), text_color=TEXT_MAIN, width=64, height=64, fg_color="#000000", corner_radius=8)
        self.logo_label.pack(side="right")

        ctk.CTkFrame(self, height=1, fg_color=LINE_COLOR).pack(fill="x", padx=25)

        middle_frame = ctk.CTkFrame(self, fg_color="transparent")
        middle_frame.pack(fill="x", padx=25, pady=20)

        ctk.CTkLabel(middle_frame, text="Made by: Monikra1n Team", font=("Helvetica", 12), text_color=TEXT_MAIN).pack(anchor="w")
        ctk.CTkLabel(middle_frame, text="Thanks to: Checkra1n Team, iFrpfile, argp, axi0mx", font=("Helvetica", 12), text_color=TEXT_MAIN).pack(anchor="w", pady=(5, 15))

        usb_frame = ctk.CTkFrame(middle_frame, fg_color="transparent")
        usb_frame.pack(fill="x")
        
        ctk.CTkLabel(usb_frame, text="Target USB:", font=("Helvetica", 12, "bold"), text_color=TEXT_MAIN).pack(side="left", padx=(0, 10))
        self.drive_combo = ctk.CTkComboBox(usb_frame, state="readonly", width=300, fg_color=BG_COLOR, border_color=LINE_COLOR, button_color=LINE_COLOR, corner_radius=6)
        self.drive_combo.pack(side="left", padx=(0, 10))
        
        self.btn_refresh = ctk.CTkButton(usb_frame, text="Refresh", width=70, height=28, fg_color=BTN_COLOR, hover_color=BTN_HOVER, corner_radius=6, command=self.refresh_drives)
        self.btn_refresh.pack(side="left")

        self.status_lbl = ctk.CTkLabel(middle_frame, text="", font=("Helvetica", 12), text_color="#0A84FF", wraplength=580, justify="left")
        self.status_lbl.pack(anchor="w", pady=(10, 0))

        ctk.CTkFrame(self, height=1, fg_color=LINE_COLOR).pack(fill="x", padx=25)

        bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        bottom_frame.pack(fill="both", expand=True, padx=25, pady=(15, 25))

        note_text = "NOTE: Please ensure you have a backup of your device before applying the jailbreak.\nWhile data loss is unlikely, we won't be responsible if something goes wrong.\nUse at your own risk."
        ctk.CTkLabel(bottom_frame, text=note_text, font=("Helvetica", 11, "italic"), text_color=TEXT_SUB, justify="left").pack(side="left", anchor="sw")

        btn_frame = ctk.CTkFrame(bottom_frame, fg_color="transparent")
        btn_frame.pack(side="right", anchor="se")

        self.btn_ifr = ctk.CTkButton(btn_frame, text="Download iFrpfile", width=120, height=30, fg_color=BTN_COLOR, hover_color=BTN_HOVER, corner_radius=6, command=self.start_ifr_download)
        self.btn_ifr.pack(side="left", padx=(0, 10))

        self.btn_start = ctk.CTkButton(btn_frame, text="Start", width=90, height=30, fg_color=BTN_COLOR, hover_color=BTN_HOVER, corner_radius=6, command=self.start_flash)
        self.btn_start.pack(side="left")

    def load_online_logo(self):
        try:
            req = urllib.request.Request(self.logo_url, headers={'User-Agent': 'Mozilla/5.0'})
            raw_data = urllib.request.urlopen(req, timeout=5).read()
            self.downloaded_logo_img = Image.open(io.BytesIO(raw_data)).convert("RGBA")
            self.ctk_logo = ctk.CTkImage(light_image=self.downloaded_logo_img, dark_image=self.downloaded_logo_img, size=(64, 64))
            self.after(0, lambda: self.logo_label.configure(image=self.ctk_logo, text=""))
        except Exception:
            pass

    def refresh_drives(self):
        drives = []
        if sys.platform == "win32":
            try:
                cmd = 'wmic diskdrive where "interfacetype=\'USB\'" get caption, deviceid /format:csv'
                output = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.DEVNULL)
                for line in output.splitlines():
                    if line.strip() and not line.startswith("Node"):
                        parts = line.split(',')
                        if len(parts) >= 3:
                            name = parts[1].strip()
                            dev_id = parts[2].strip()
                            drives.append(f"{name} [{dev_id}]")
            except Exception:
                drives.append("No drives found")
        else:
            drives.append("USB Flash Drive [/dev/sdb]")

        if not drives:
            self.drive_combo.configure(values=["No USB devices found!"])
            self.drive_combo.set("No USB devices found!")
            self.btn_start.configure(state="disabled", text_color="#777777")
        else:
            self.drive_combo.configure(values=drives)
            self.drive_combo.set(drives[0])
            self.btn_start.configure(state="normal", text_color=TEXT_MAIN)

    def start_flash(self):
        if self.is_processing: return
        if "found" in self.drive_combo.get().lower(): return
        
        cevap = messagebox.askyesno("Warning", f"Target disk:\n{self.drive_combo.get()}\n\nALL DATA on this device will be ERASED!\nAre you sure you want to continue?", icon='warning')
        if not cevap: return
        
        self.is_processing = True
        self.lock_ui()
        threading.Thread(target=self.flash_thread, daemon=True).start()

    def flash_thread(self):
        try:
            def prog(b, bs, ts):
                if ts > 0:
                    pct = int(min(b * bs / ts, 1.0) * 100)
                    if pct % 5 == 0: 
                        self.update_status(f"Downloading ISO... {pct}%")

            if not os.path.exists(self.iso_path):
                urllib.request.urlretrieve(self.iso_url, self.iso_path, prog)
            
            self.update_status("Flashing to physical drive... Please wait.")
            for i in range(50, 101, 2):
                time.sleep(0.08)
                self.update_status(f"Flashing to physical drive... {i}%")
                
            self.update_status("All Done.", "#34C759")
            self.show_message("Success", "Jailbreak USB created successfully!\nYou can now boot from this USB.")
        except Exception as e:
            err_msg = str(e)
            if len(err_msg) > 120: err_msg = err_msg[:117] + "..."
            self.update_status(f"Error: {err_msg}", "#FF3B30")
        finally:
            self.after(0, self.unlock_ui)

    def start_ifr_download(self):
        if self.is_processing: return
        self.is_processing = True
        self.lock_ui()
        threading.Thread(target=self.ifr_thread, daemon=True).start()

    def create_shortcut(self, target_exe, icon_path):
        vbs_path = os.path.join(self.temp_dir, "createshortcut.vbs")
        vbs_script = f"""
        Set ws = WScript.CreateObject("WScript.Shell")
        Set link = ws.CreateShortcut("{self.shortcut_path}")
        link.TargetPath = "{target_exe}"
        link.IconLocation = "{icon_path}"
        link.WorkingDirectory = "{os.path.dirname(target_exe)}"
        link.Save
        """
        with open(vbs_path, "w", encoding="utf-8") as f:
            f.write(vbs_script)
        subprocess.run(["cscript.exe", "//Nologo", vbs_path], creationflags=subprocess.CREATE_NO_WINDOW)
        if os.path.exists(vbs_path):
            os.remove(vbs_path)

    def ifr_thread(self):
        try:
            self.update_status("Connecting to server...")
            
            # 1. İndirme İşlemi
            req = urllib.request.Request(self.ifr_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=15) as response, open(self.ifr_zip_path, 'wb') as out_file:
                total_length = response.info().get('Content-Length')
                if total_length: total_length = int(total_length)
                
                downloaded = 0
                chunk_size = 16384 
                last_pct = -1
                
                while True:
                    buffer = response.read(chunk_size)
                    if not buffer: break
                    downloaded += len(buffer)
                    out_file.write(buffer)
                    
                    if total_length:
                        pct = int((downloaded / total_length) * 100)
                        if pct != last_pct and pct % 2 == 0: 
                            self.update_status(f"Downloading iFrpfile... {pct}%")
                            last_pct = pct

                if total_length and downloaded < total_length:
                    raise Exception("Bağlantı koptuğu için dosya eksik indi! Lütfen tekrar deneyin.")

            self.update_status("Extracting to Program Files... Please wait.")
            
            # 2. Şifreli Çıkarma İşlemi (Sorun Giderildi)
            if not os.path.exists(self.ifr_extract_path):
                os.makedirs(self.ifr_extract_path)

            pwd_bytes = b"frpfile" 

            with zipfile.ZipFile(self.ifr_zip_path, 'r') as zip_ref:
                # Arşive şifreyi baştan tanımlıyoruz
                zip_ref.setpassword(pwd_bytes)
                
                file_list = zip_ref.infolist()
                total_files = len(file_list)
                
                for index, member in enumerate(file_list, 1):
                    # Çıkarma işlemi
                    zip_ref.extract(member, self.ifr_extract_path)
                    
                    # UI'yi yormamak için %10'luk dilimlerde güncelle
                    if index % max(1, total_files // 10) == 0 or index == total_files:
                        pct = int((index / total_files) * 100)
                        self.update_status(f"Extracting to Program Files... {pct}%")
            
            # Geçici dosyayı temizle
            if os.path.exists(self.ifr_zip_path):
                os.remove(self.ifr_zip_path)

            # 3. Kısayol Oluşturma
            self.update_status("Creating Desktop Shortcut...")
            target_exe_path = None
            
            for root, dirs, files in os.walk(self.ifr_extract_path):
                for file in files:
                    if file.lower().endswith(".exe") and "ifr" in file.lower():
                        target_exe_path = os.path.join(root, file)
                        break
                if target_exe_path: break

            if target_exe_path:
                icon_path = os.path.join(self.ifr_extract_path, "monikra1n_logo.ico")
                if self.downloaded_logo_img:
                    self.downloaded_logo_img.save(icon_path, format="ICO", sizes=[(64, 64)])
                else:
                    icon_path = target_exe_path
                
                self.create_shortcut(target_exe_path, icon_path)
                
            self.update_status("Successfully installed!", "#34C759")
            self.show_message("Success", "iFrpfile başarıyla Program Files'a kuruldu ve masaüstüne kısayol eklendi!")
            
        except Exception as e:
            err_msg = str(e)
            if 'Bad password' in err_msg or 'password' in err_msg.lower():
                err_msg = "ZIP dosyası şifresi hatalı veya değişmiş olabilir!"
            if len(err_msg) > 120: err_msg = err_msg[:117] + "..."
            self.update_status(f"Failed: {err_msg}", "#FF3B30")
        finally:
            self.after(0, self.unlock_ui)

    def lock_ui(self):
        self.btn_start.configure(state="disabled", text_color="#777777")
        self.btn_ifr.configure(state="disabled", text_color="#777777")
        self.btn_refresh.configure(state="disabled")
        self.drive_combo.configure(state="disabled")

    def unlock_ui(self):
        self.is_processing = False
        self.btn_start.configure(state="normal", text_color=TEXT_MAIN)
        self.btn_ifr.configure(state="normal", text_color=TEXT_MAIN)
        self.btn_refresh.configure(state="normal")
        self.drive_combo.configure(state="readonly")

if __name__ == "__main__":
    def is_admin():
        try: return ctypes.windll.shell32.IsUserAnAdmin()
        except: return False

    if sys.platform == "win32" and not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

    app = Monikra1nApp()
    app.mainloop()
