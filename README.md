# CHATT — Command Handling and Terminal Tool

**CHATT** is a retro-themed, LLM-powered shell assistant that emulates a Commodore style terminal and executes natural-language commands using your own OpenAI-compatible API (like vLLM).  
It can run both interactive and non-interactive commands intelligently in your terminal — launching a new Konsole window if needed.

![image](https://github.com/user-attachments/assets/014c9fa0-052c-44a3-977b-29efbc2dbd20)

---

## 🧠 Features

- 🕹️ Commodore style text screen
- 💬 LLM-based command understanding
- 🔧 Bash command execution (via MCP-style tool calls)
- 🖥️ Automatically opens `konsole` for interactive commands like `nano`, `top`, `vim`, etc.
- 🔐 Optional confirmation before executing assistant-suggested commands

---

## 🧰 Requirements

- Python 3.8+
- `openai` Python package
- `konsole` terminal emulator (for KDE)
- vLLM or OpenAI-compatible API endpoint

---

## 🚀 Installation
update your LLM connections in main.py

```bash
git clone https://github.com/yourname/chatt.git
cd chatt
python3 main.py
