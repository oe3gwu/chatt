# 💾 CHATT — Command Handling and Terminal Tool

**CHATT** is a nerdy, retro-themed AI terminal assistant designed to run natural-language shell commands securely, safely, and intelligently — all through a ChatGPT-style interface. It supports interactive tools, intelligent command suggestions, safety confirmations, and a Commodore-style startup experience.

![CHATT Banner](https://github.com/user-attachments/assets/88c83970-ce19-4518-8142-2f607121e95a)

## 🧠 Features

- 🧵 **Command Handling via LLM** — Uses your own OpenAI-compatible LLM (like vLLM) to interpret natural language.
- 🎮 **Retro Boot Screen** — Commodore-style boot output when starting up.
- 🖥️ **Interactive Command Support** — Launches commands like `nano`, `top`, `htop`, etc. in a real terminal window (Konsole, GNOME Terminal, etc.).
- 🔒 **Safety Prompts** — Dangerous commands like `rm -rf`, `mkfs`, `fdisk`, `zfs`, `lvm` require confirmation.
- 📜 **Command History** — Full up/down history support using arrow keys.
- 🧾 **Tool Call Suggestions** — Assistant can propose structured command JSONs and ask if you'd like to run them.
- ⚙️ **Terminal Auto-Detection** — Works with many terminal emulators: `konsole`, `xterm`, `lxterminal`, etc.
- 📁 **Config File Driven** — Easy-to-change LLM connection settings via `config.txt`.

## 🧰 Requirements

- Python 3.8+
- Linux terminal with a GUI terminal emulator
- A vLLM or OpenAI-compatible API endpoint
- Python packages: `openai`

## 🚀 Installation

```bash
pip install openai
git clone https://github.com/yourname/chatt.git
```

## ⚙️ Configuration
Create a file named config.txt in the same folder as main.py:

```
api_key=YOUR_API_KEY
base_url=YOUR_OPENAI_URL
model=YOUR_MODEL
```

## 🖥️ Running
```bash
cd chatt
python3 main.py
```
## ⚠️ Disclaimer

CHATT is a **prototype** developed for experimental and educational use.  
It is not intended for production environments without thorough review and sandboxing.

- Commands are interpreted and executed via a language model.
- While safety checks (like confirmation for dangerous commands) are included, they are not foolproof.
- Use caution and always review suggested commands before confirming execution.

By using CHATT, you accept all responsibility for any system-level changes it performs.
