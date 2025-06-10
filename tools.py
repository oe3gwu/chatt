# tools.py

import os
import shlex
import subprocess
import shutil
import tempfile

INTERACTIVE_COMMANDS = {
    "nano", "vim", "top", "htop", "bash", "zsh",
    "cfdisk", "fdisk", "apt", "apt-get",
    "lvm", "lvcreate", "vgcreate", "pvcreate", "zfs"
}

DANGEROUS_COMMANDS = [
    "rm -rf", "mkfs", "dd", "shutdown", "reboot",
    "fdisk", "cfdisk", "lvm", "zfs"
]

TERMINALS = ["konsole", "gnome-terminal", "xterm", "lxterminal", "tilix", "mate-terminal"]

def is_interactive_command(command):
    return any(command.startswith(cmd) for cmd in INTERACTIVE_COMMANDS)

def is_dangerous_command(command):
    return any(danger in command for danger in DANGEROUS_COMMANDS)

def get_terminal():
    for term in TERMINALS:
        if shutil.which(term):
            return term
    return None

def execute_command(command):
    # Confirm truly dangerous commands
    if is_dangerous_command(command):
        confirm = input(f"⚠️ This command may be dangerous: '{command}'. REALLY run it? [Y/n]: ").strip().lower()
        if confirm not in {"", "y", "yes"}:
            return "❎ Cancelled."

    # Launch interactive commands in a new terminal
    if is_interactive_command(command):
        term = get_terminal()
        if not term:
            return "❌ No supported terminal emulator found."

        with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.sh') as f:
            f.write(f"#!/bin/bash\n{command}\necho; echo '[Press any key to close]'; read -n 1\n")
            f.flush()
            os.chmod(f.name, 0o755)
            subprocess.Popen([term, "--hold", "-e", f.name])
        return f"🖥️ Launched interactive terminal for: {command}"

    # Non-interactive commands — now with shell=True for redirection support
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return f"✅ Success:\n{result.stdout.strip()}"
        else:
            return f"❌ Error:\n{result.stderr.strip()}"
    except subprocess.TimeoutExpired:
        return "❌ Command timed out."
    except Exception as e:
        return f"❌ Exception: {e}"
