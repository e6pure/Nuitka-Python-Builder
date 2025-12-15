import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext, simpledialog
import subprocess
import os
import threading
import shlex
import queue
import sys
import shutil
import json

# --- Configuration ---
APP_NAME = "Nuitka Python Builder"
VERSION = "2.1 for Nuitka 2.8.9"
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
OPTIONS_FILE = os.path.join(ASSETS_DIR, "nuitka_options.json")
DEFAULT_ICON_NAME = "windowsicon.ico"

# --- Colors ---
COLOR_BG_MAIN = "#f5f6fa"
COLOR_BG_SIDE = "#2f3640"
COLOR_ACCENT = "#44bd32"
COLOR_ACCENT_HOVER = "#4cd137"
COLOR_TEXT_WHITE = "#ffffff"
COLOR_TEXT_DARK = "#2f3640"
COLOR_LOG_BG = "#1e1e1e"
COLOR_LOG_FG = "#00ff00"

class NuitkaBuilderApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_NAME} v{VERSION}")
        self.geometry("1150x850")
        self.minsize(1000, 750)
        self.configure(bg=COLOR_BG_MAIN)
        
        self.dynamic_options = {} 
        
        self.init_core_variables()
        self.load_app_icon()
        self.setup_styles()
        self.create_layout()
        
        self.log_queue = queue.Queue()
        self.check_log_queue()
        self.detect_system_python()

    def init_core_variables(self):
        self.python_exe_var = tk.StringVar()
        self.source_folder_var = tk.StringVar()
        self.main_file_var = tk.StringVar()
        self.icon_file_var = tk.StringVar()
        self.output_dir_var = tk.StringVar()
        self.output_name_var = tk.StringVar()

    def load_json_config(self):
        if not os.path.exists(OPTIONS_FILE):
            self.log(f"Config Warning: {OPTIONS_FILE} not found.")
            return None
        try:
            with open(OPTIONS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            messagebox.showerror("Config Error", f"Invalid JSON:\n{e}")
            return None

    def load_app_icon(self):
        icon_path = os.path.join(ASSETS_DIR, DEFAULT_ICON_NAME)
        if os.path.exists(icon_path):
            try: self.iconbitmap(icon_path)
            except: pass

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Main.TFrame", background=COLOR_BG_MAIN)
        style.configure("Header.TFrame", background=COLOR_BG_SIDE)
        style.configure("Header.TLabel", background=COLOR_BG_SIDE, foreground=COLOR_TEXT_WHITE, font=("Segoe UI", 18, "bold"))
        style.configure("Section.TLabel", background=COLOR_BG_MAIN, foreground=COLOR_TEXT_DARK, font=("Segoe UI", 10, "bold"))
        style.configure("Normal.TLabel", background=COLOR_BG_MAIN, foreground=COLOR_TEXT_DARK, font=("Segoe UI", 9))
        style.configure("Group.TLabelframe", background=COLOR_BG_MAIN, bordercolor="#dcdde1")
        style.configure("Group.TLabelframe.Label", background=COLOR_BG_MAIN, foreground=COLOR_BG_SIDE, font=("Segoe UI", 9, "bold"))
        style.configure("Tab.TFrame", background=COLOR_BG_MAIN)

    def detect_system_python(self):
        path = shutil.which("python")
        if path: self.python_exe_var.set(path)

    def create_layout(self):
        # Header
        header = ttk.Frame(self, style="Header.TFrame", padding=(25, 15))
        header.pack(fill="x")
        ttk.Label(header, text=APP_NAME.upper(), style="Header.TLabel").pack(side="left")
        
        # Content
        content = ttk.Frame(self, style="Main.TFrame", padding=20)
        content.pack(fill="both", expand=True)
        
        # Left Panel
        left_panel = ttk.Frame(content, style="Main.TFrame")
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 15))
        
        self.create_env_section(left_panel)
        self.create_files_section(left_panel)
        self.create_dynamic_tabs(left_panel)
        
        # Right Panel
        right_panel = ttk.Frame(content, style="Main.TFrame", width=420)
        right_panel.pack(side="right", fill="y")
        
        self.create_actions_section(right_panel)
        self.create_log_section(right_panel)
        
        # Footer
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(self, textvariable=self.status_var, relief="sunken", anchor="w", padding=6).pack(side="bottom", fill="x")

    def create_env_section(self, parent):
        group = ttk.LabelFrame(parent, text=" 0. Build Environment ", style="Group.TLabelframe", padding=15)
        group.pack(fill="x", pady=(0, 15))
        row = ttk.Frame(group, style="Main.TFrame")
        row.pack(fill="x")
        ttk.Entry(row, textvariable=self.python_exe_var).pack(side="left", fill="x", expand=True, padx=(0, 5))
        ttk.Button(row, text="Browse", width=8, command=self.browse_python).pack(side="right")

    def create_files_section(self, parent):
        group = ttk.LabelFrame(parent, text=" 1. Project Config ", style="Group.TLabelframe", padding=15)
        group.pack(fill="x", pady=(0, 15))
        
        def add_row(label, var, cmd, idx):
            ttk.Label(group, text=label, style="Normal.TLabel").grid(row=idx, column=0, sticky="w", pady=5)
            ttk.Entry(group, textvariable=var).grid(row=idx, column=1, sticky="ew", padx=10)
            if cmd: ttk.Button(group, text="...", width=4, command=cmd).grid(row=idx, column=2)
            else: ttk.Frame(group, width=30).grid(row=idx, column=2)

        group.columnconfigure(1, weight=1)
        add_row("Main Script:", self.main_file_var, self.browse_main_file, 0)
        add_row("Source Folder:", self.source_folder_var, self.browse_source_folder, 1)
        add_row("Icon (ico/png):", self.icon_file_var, self.browse_icon, 2)
        add_row("Output Dir:", self.output_dir_var, self.browse_output_dir, 3)
        add_row("Output Name:", self.output_name_var, None, 4)

    def create_dynamic_tabs(self, parent):
        config = self.load_json_config()
        if not config: return

        nb = ttk.Notebook(parent)
        nb.pack(fill="both", expand=True)

        for tab_data in config.get("tabs", []):
            tab_frame = ttk.Frame(nb, style="Tab.TFrame", padding=10)
            nb.add(tab_frame, text=tab_data["name"])
            
            for group_data in tab_data.get("groups", []):
                g_frame = ttk.LabelFrame(tab_frame, text=group_data["name"], style="Group.TLabelframe", padding=15)
                g_frame.pack(fill="x", pady=5)
                for i in range(3): g_frame.columnconfigure(i, weight=1)

                for idx, opt in enumerate(group_data.get("options", [])):
                    flag = opt.get("flag", "")
                    var = tk.BooleanVar(value=opt.get("default", False))
                    self.dynamic_options[flag] = var
                    r, c = divmod(idx, 3)
                    ttk.Checkbutton(g_frame, text=opt.get("label"), variable=var).grid(row=r, column=c, sticky="w", padx=5, pady=5)

        self.create_assets_tab(nb)
        self.create_custom_args_tab(nb)

    def create_assets_tab(self, nb):
        """Redesigned Assets Tab with Listbox (No more manual syntax)"""
        tab = ttk.Frame(nb, style="Tab.TFrame", padding=15)
        nb.add(tab, text="Assets & Data")
        
        # --- Asset List (Treeview) ---
        # Columns: Type, Source, Destination
        columns = ("type", "source", "dest")
        self.asset_tree = ttk.Treeview(tab, columns=columns, show="headings", height=8)
        self.asset_tree.heading("type", text="Type")
        self.asset_tree.heading("source", text="Source Path / Name")
        self.asset_tree.heading("dest", text="Destination in EXE")
        
        self.asset_tree.column("type", width=80, anchor="center")
        self.asset_tree.column("source", width=250)
        self.asset_tree.column("dest", width=150)
        
        self.asset_tree.pack(fill="both", expand=True, pady=(0, 10))
        
        # --- Buttons ---
        btn_frame = ttk.Frame(tab, style="Tab.TFrame")
        btn_frame.pack(fill="x")
        
        ttk.Button(btn_frame, text="+ Add Folder", command=self.add_asset_folder).pack(side="left", padx=(0, 5))
        ttk.Button(btn_frame, text="+ Add File", command=self.add_asset_file).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="+ Add Package", command=self.add_asset_package).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="- Remove Selected", command=self.remove_asset).pack(side="right")

    def add_asset_folder(self):
        """Pick a folder and ask for destination name."""
        path = filedialog.askdirectory()
        if path:
            default_name = os.path.basename(path)
            dest = simpledialog.askstring("Destination", "Folder name inside EXE:", initialvalue=default_name)
            if dest:
                self.asset_tree.insert("", "end", values=("Dir", path, dest))

    def add_asset_file(self):
        """Pick a file and ask for destination folder."""
        path = filedialog.askopenfilename()
        if path:
            dest = simpledialog.askstring("Destination", "Relative path/name inside EXE ('.' for root):", initialvalue=".")
            if dest:
                if dest == ".": dest = os.path.basename(path) # If root, keep filename
                self.asset_tree.insert("", "end", values=("File", path, dest))

    def add_asset_package(self):
        """Ask for package name."""
        name = simpledialog.askstring("Package", "Package Name (e.g. pandas):")
        if name:
             self.asset_tree.insert("", "end", values=("Package", name, "N/A"))

    def remove_asset(self):
        selected = self.asset_tree.selection()
        for item in selected:
            self.asset_tree.delete(item)

    def create_custom_args_tab(self, nb):
        tab = ttk.Frame(nb, style="Tab.TFrame", padding=15)
        nb.add(tab, text="Extra Args")
        ttk.Label(tab, text="Additional Arguments (One per line):", style="Section.TLabel").pack(anchor="w")
        self.txt_custom_args = tk.Text(tab, height=12, font=("Consolas", 9), bd=1, relief="solid")
        self.txt_custom_args.pack(fill="both", expand=True, pady=5)

    def create_actions_section(self, parent):
        frame = ttk.LabelFrame(parent, text=" Actions ", style="Group.TLabelframe", padding=15)
        frame.pack(fill="x", pady=(0, 15))
        btn_grid = ttk.Frame(frame, style="Main.TFrame")
        btn_grid.pack(fill="x", pady=(0, 10))
        ttk.Button(btn_grid, text="Check Version", command=self.check_version).pack(side="left", fill="x", expand=True, padx=(0, 5))
        ttk.Button(btn_grid, text="Install/Update Nuitka", command=self.update_nuitka).pack(side="right", fill="x", expand=True, padx=(5, 0))
        self.btn_build = tk.Button(frame, text="BUILD EXE NOW", font=("Segoe UI", 14, "bold"),
                                   bg=COLOR_ACCENT, fg="white", activebackground=COLOR_ACCENT_HOVER,
                                   relief="flat", cursor="hand2", height=2, command=self.start_build_process)
        self.btn_build.pack(fill="x")

    def create_log_section(self, parent):
        lbl = ttk.Label(parent, text="Terminal Output:", style="Section.TLabel")
        lbl.pack(anchor="w", pady=(0, 5))
        self.log_widget = scrolledtext.ScrolledText(parent, state='disabled', bg=COLOR_LOG_BG, fg=COLOR_LOG_FG, font=("Consolas", 9), borderwidth=0)
        self.log_widget.pack(fill="both", expand=True)

    # --- Actions ---
    def browse_python(self):
        f = filedialog.askopenfilename(filetypes=[("Executable", "python.exe")])
        if f: self.python_exe_var.set(f)
    
    def browse_main_file(self):
        f = filedialog.askopenfilename(filetypes=[("Python Files", "*.py")])
        if f:
            self.main_file_var.set(f)
            self.source_folder_var.set(os.path.dirname(f))
            self.output_name_var.set(os.path.splitext(os.path.basename(f))[0])
            self.detect_virtual_env(os.path.dirname(f))

    def detect_virtual_env(self, folder):
        for name in ["venv", ".venv", "env"]:
            path = os.path.join(folder, name, "Scripts", "python.exe")
            if os.path.exists(path):
                self.python_exe_var.set(path)
                self.log(f"Auto-detected venv: {path}")
                return

    def browse_source_folder(self):
        d = filedialog.askdirectory()
        if d: self.source_folder_var.set(d)

    def browse_icon(self):
        f = filedialog.askopenfilename(filetypes=[("Images", "*.ico;*.png")])
        if f: self.icon_file_var.set(f)
        
    def browse_output_dir(self):
        d = filedialog.askdirectory()
        if d: self.output_dir_var.set(d)

    def log(self, msg): self.log_queue.put(msg)
    
    def check_log_queue(self):
        while not self.log_queue.empty():
            msg = self.log_queue.get()
            self.log_widget.config(state='normal')
            self.log_widget.insert(tk.END, str(msg) + "\n")
            self.log_widget.see(tk.END)
            self.log_widget.config(state='disabled')
        self.after(100, self.check_log_queue)

    def get_safe_python_cmd(self):
        path = self.python_exe_var.get().strip()
        if not path or not os.path.exists(path):
            messagebox.showerror("Error", "Invalid Python Interpreter Path.")
            return None
        return path

    def check_version(self):
        py = self.get_safe_python_cmd()
        if py: threading.Thread(target=self._run_subprocess, args=([py, "-m", "nuitka", "--version"],), daemon=True).start()

    def update_nuitka(self):
        py = self.get_safe_python_cmd()
        if py and messagebox.askyesno("Confirm", f"Update Nuitka via:\n{py}?"):
            threading.Thread(target=self._run_subprocess, args=([py, "-m", "pip", "install", "-U", "nuitka"],), daemon=True).start()

    def _run_subprocess(self, cmd):
        self.log(f"> Executing: {' '.join(cmd)}")
        try:
            flags = 0x08000000 if os.name == 'nt' else 0
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, creationflags=flags)
            for line in proc.stdout: self.log(line.strip())
            proc.wait()
            self.log(">>> Finished.")
        except Exception as e: self.log(f"Error: {e}")

    def start_build_process(self):
        py = self.get_safe_python_cmd()
        if not py or not self.main_file_var.get():
            messagebox.showwarning("Missing Info", "Python Path and Main Script are required.")
            return
        threading.Thread(target=self.run_nuitka_build, args=(py,), daemon=True).start()

    def run_nuitka_build(self, python_path):
        self.btn_build.config(state="disabled", text="BUILDING...", bg="#95a5a6")
        try:
            cmd = [python_path, "-m", "nuitka"]
            cmd.append("--assume-yes-for-downloads")
            
            # JSON Options
            for flag, var in self.dynamic_options.items():
                if var.get(): cmd.append(flag)

            # Files
            ico = self.icon_file_var.get()
            if ico: cmd.append(f'--windows-icon-from-ico={ico}')
            out_dir = self.output_dir_var.get()
            if out_dir: cmd.append(f'--output-dir={out_dir}')
            out_name = self.output_name_var.get()
            if out_name:
                if not out_name.lower().endswith(".exe"): out_name += ".exe"
                cmd.append(f'--output-filename={out_name}')
            
            # --- ASSETS (From Treeview) ---
            # Iterate through the treeview items to build commands
            for item in self.asset_tree.get_children():
                vals = self.asset_tree.item(item)['values']
                type_, src, dest = vals[0], vals[1], vals[2]
                
                if type_ == "Dir":
                    cmd.append(f'--include-data-dir={src}={dest}')
                elif type_ == "File":
                    cmd.append(f'--include-data-files={src}={dest}')
                elif type_ == "Package":
                    cmd.append(f'--include-package-data={src}')

            # Custom Args
            custom = self.txt_custom_args.get("1.0", tk.END).strip()
            if custom: cmd.extend(shlex.split(custom))
            
            cmd.append(self.main_file_var.get())
            
            self._run_subprocess(cmd)
            self.generate_batch_script(self.source_folder_var.get(), cmd)
            
        except Exception as e: self.log(f"CRITICAL ERROR: {e}")
        finally: self.btn_build.config(state="normal", text="BUILD EXE NOW", bg=COLOR_ACCENT)

    def generate_batch_script(self, folder, cmd):
        try:
            if not folder: return
            path = os.path.join(folder, "build_reproduce.bat")
            cmd_str = " ".join(shlex.quote(c) for c in cmd)
            with open(path, "w", encoding="utf-8") as f:
                f.write(f"@echo off\necho Reproducing Build...\n{cmd_str}\npause")
            self.log(f"Batch script saved: {path}")
        except: pass

if __name__ == "__main__":
    app = NuitkaBuilderApp()
    app.mainloop()