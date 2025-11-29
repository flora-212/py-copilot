# 🤖 Py-Copilot
## Introduction
**Py-Copilot** is a VSCode extension that enables Python programs to interact directly with GitHub Copilot.  
It supports sending messages programmatically, attaching file context, and running structured prompts.  

With these features, Py-Copilot lays the foundation for **automated evaluation of Copilot’s performance across different models** —  
this project provides an example where models are adapting other code completion methods to ne

---

## ✨ Features
- 📩 Send messages to Copilot directly from Python programs  
- 📎 Attach file context to enrich prompts  
- 🔄 Run structured prompts to simulate dataset-specific testing scenarios  
- 📊 Evaluate how Copilot models perform when adapting other code completion methods to new datasets and contexts *(partially implemented, designed for further extension)*    
- 🧪 **Planned**: Automate evaluation of Copilot across multiple models *(not yet implemented, but the framework supports it)*

---

## 🚀 Installation

### Prerequisites
Before installing this project, make sure you have:

**Required:**
- **Visual Studio Code** 1.103.0 or higher
- **Python** 3.6 or higher 
- **Node.js** 16.0 or higher and **npm**
- **GitHub Copilot Chat** extension (installed in VS Code)

**Python Libraries:**
- `tkinter` (usually comes with Python, for GUI interface)
- All other required libraries are part of Python standard library (`urllib`, `json`, `os`, etc.)

**Optional for development:**
- `requests` library (only needed for `test_client.py`)

### Installation Steps

1. **Clone the repository:**
```bash
git clone https://github.com/flora-212/py-copilot.git
cd py-copilot
```

2. **Install Node.js dependencies:**
```bash
npm install
```

3. **Build the extension:**
```bash
npm run compile
# Or use watch mode for development:
# npm run watch
```

4. **Install in VS Code:**
   - Press `F5` to run the extension in a new Extension Development Host window
   - Or package and install: `npm run package` then install the generated `.vsix` file

5. **Verify Python setup:**
```bash
python --version  # Should be 3.6+
python -c "import tkinter"  # Should not raise an error
```

### Optional: Install Python test dependencies
If you want to run the test client with requests library:
```bash
pip install requests
```

---

## 📖 Usage

### Prerequisites for Usage
Before using any Python clients, make sure:
1. **Open a separate VS Code window** (not the one running this project) 
2. **Install and activate the py-copilot extension** in that VS Code window by pressing `F5` in this project
3. **Open GitHub Copilot Chat** in the separate VS Code window (`Ctrl+Shift+P` → "GitHub Copilot: Open Chat")
4. **Keep the separate VS Code window with Copilot Chat open** while running Python clients from your terminal

**Important:** The Python clients communicate with the py-copilot extension running in a separate VS Code window, not the development window where you're editing this project.

### 1. Project Configuration Dialog
For structured adaptation tasks:
```bash
python client/project_client.py
```
This opens a GUI where you can:
- Specify technology and benchmark names
- Set paths to technology and benchmark folders  
- Add context from papers or documentation
- Preview the generated message before sending

### 2. Test Client (with requests library)
If you have `requests` installed:
```bash
python client/test_client.py
```

### 3. Simple Command-Line Client
For quick queries:
```bash
python client/simple_client.py "your message" [optional_path_for_additional_file]
```


**Note:** The VS Code extension must be running for Python clients to communicate with Copilot.
