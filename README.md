# Nuitka Python Builder (NPB)

**NPB** is a friendly, configuration-driven GUI wrapper for [Nuitka](https://nuitka.net/) that makes compiling Python scripts into standalone Windows executables easier and more intuitive. It eliminates the need to memorize complex CLI arguments while managing build environments, plugins, and asset embedding automatically.

![Python](https://img.shields.io/badge/Python-3.x-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Stable-brightgreen.svg)

## ⚠️ Python Version & Compiler Requirements

- **Python ≥3.12**  
  - **Required compiler:** **MSVC (`--msvc=latest`)**  
  - MinGW64 is **no longer supported** on Python ≥3.12 and will cause build errors.  
  - Clang is possible but requires a full LLVM toolchain and manual configuration.  

- **Python ≤3.11**  
  - You can safely use either **MSVC** or **MinGW64 (`--mingw64`)**.  

- **Visual Studio Build Tools** (required for MSVC builds)  
  1. Download from [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)  
  2. Install the **“Desktop development with C++”** workload.  
  3. Ensure `cl.exe` is available in your PATH or via the Developer Command Prompt.  
  4. Nuitka will automatically detect MSVC if installed properly.  

- **Plugins & Compatibility**  
  - Some plugins may not fully support Python ≥3.12 yet.  
  - If a build fails, ensure you are using MSVC and the recommended Nuitka version (2.8.9).  

> **Tip:** NPB automatically detects your Python version and will warn if the selected compiler is incompatible.

## Inspiration

I often use Python to develop scripts and small tools, but Nuitka's command-line interface can be daunting with countless flags and options. I kept forgetting which arguments to use, especially when switching between virtual environments or including assets.  

This tool was created to simplify the process. With NPB, I can configure builds visually, select interpreters, manage plugins, embed data folders, and produce reproducible executables without worrying about remembering CLI syntax. It’s a small convenience, but it solves a real headache when building Python EXEs regularly.

## Real-World Problems NPB Solves

- Remembering Nuitka CLI arguments is tedious and error-prone.
- Switching between virtual environments can break builds if dependencies are missed.
- Including assets (images, configs) or hidden imports manually is cumbersome.
- Producing reproducible builds consistently requires running long CLI commands.

## Key Features

- **Environment Agnostic:** Works with your System Python or virtual environments (`venv`, `conda`), using the interpreter you select.  
- **JSON-Driven Configuration:** All compiler flags are dynamically loaded from `assets/nuitka_options.json`. Add or modify flags without touching the Python source code.  
- **Smart Asset Management:** Easily include data directories, hidden imports, or resource files.  
- **Reproducible Builds:** Generates a `build_reproduce.bat` after every build for later CLI re-execution.  
- **Windows Optimized:** Handles icons, UAC Admin requests, and compiler selection (MSVC/MinGW).  

## Prerequisites

- **OS:** Windows 10 or 11  
- **Python:** 3.6+  
- **Nuitka:** Installed in the Python environment you intend to use  

## Installation (Source Code)

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/e6pure/Nuitka-Python-Builder.git
    cd Nuitka-Python-Builder
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    Note: The GUI itself runs on tkinter (standard library) and requires no extra dependencies.
    ```

3.  **Run the script:**
    ```bash
    python nuitka_python_builder_v2.0.py
    ```

## Download Executable (.exe)

You can download the standalone executable (`.exe`) directly from the **Releases** page. It runs instantly on Windows without requiring any installation.

**[Download Nuitka Python Builder v2.1](https://github.com/e6pure/Nuitka-Python-Builder/releases)**


## Usage Guide
1. **Select Build Environment** 
   * **Default:** System Python. 
   * **For virtual environments (venv):** Browse to the Scripts folder and select python.exe. 
   * NPB will use only the libraries in that environment for the build.

2. **Configure Project Files** 
   * **Main Script:** Your entry point .py
   * **file Icon:** Optional .ico for the EXE
   * **Output Dir:** Folder for the final .exe or dist directory

3. **Build Options**
   * **General/Basics:** Toggle Standalone, One-File mode, or Console visibility
   * **Plugins:** Enable Tkinter, PyQt6, PySide6, NumPy, etc.
   * **Assets & Imports:** Include directories or hidden imports

4. **Build**

   * Click BUILD EXE NOW. Terminal output shows real-time compilation.

## Tip: JSON Options

Open `assets/nuitka_options.json` to add or modify compiler flags.  
New entries automatically appear in the GUI on next launch.

> **Note:**  
> - You can customize this JSON for **any supported Nuitka version**, adding new flags or plugins as needed.  
> - The current NPB release is tested with **Nuitka 2.8.9**. Some newer options from Nuitka may require updating NPB or adjusting the JSON manually.  
> - Always check [Nuitka's official documentation](https://nuitka.net/doc/user-manual.html#command-line-options) if you want to use flags from future versions.

## Project Structure

Nuitka-Python-Builder/
│
├── assets/
│   ├── windowsicon.ico              # Default application icon
│   └── nuitka_options.json          # Configuration database
│
├── nuitka_python_builder_v2.0.py    # Main Application
├── requirements.txt                 # Dependencies (nuitka, zstandard, ordered-set)
└── README.md                        # Documentation

## Disclaimer

**Warning:** NPB does not maintain a history of builds or undo for configuration changes. Always double-check your selections before building: mistakes in paths, icons, or hidden imports cannot be automatically reverted. The tool is a convenience wrapper, not a safety net.

## Contributing

Contributions welcome! Submit issues or pull requests for bug fixes, improvements, or new features.

## Troubleshooting

Q: The build fails with "Access Denied".
A: If your Python is installed in C:\Program Files, you may need permission to install Nuitka. Right-click nuitka_python_builder_v2.0.py (or your terminal) and select Run as Administrator.
Q: My EXE closes immediately after opening.
A: This usually means there is a runtime error in your script (missing file or library). Re-build with "Disable Console" UNCHECKED. Run the EXE again, and the console window will stay open, allowing you to read the Python error traceback.
Q: Nuitka complains about missing C Compiler.
A: Nuitka requires a C compiler. When you run the build for the first time, allow Nuitka to automatically download and install MinGW64 (The tool passes --assume-yes-for-downloads to handle this automatically).

## Contact / Support

GitHub: https://github.com/e6pure

## License

This project is open-source and available under the **MIT License**.

---
*Developed with Python & Tkinter.*
