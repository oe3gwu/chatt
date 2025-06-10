import subprocess
import shlex
import shutil
import os

# Commands that require an interactive terminal
INTERACTIVE_COMMANDS = {
    "nano", "vim", "htop", "top", "less", "man", "apt", "fdisk", "cfdisk", "nmtui"
}

DANGEROUS_KEYWORDS = [
    "rm -rf", "mkfs", ":(){", "shutdown", "reboot", "poweroff", "dd if=",
    "mv /", "chmod -r", "chown -r", "wipefs",
    "fdisk", "cfdisk", "parted", "sfdisk",
    "pvcreate", "vgcreate", "vgremove", "lvcreate", "lvremove", "lvextend", "lvreduce",
    "zpool", "zfs", "zpool destroy", "zfs destroy"
]

def is_interactive_command(command: str) -> bool:
    return any(command.strip().startswith(cmd) for cmd in INTERACTIVE_COMMANDS)

def is_dangerous_command(command: str) -> bool:
    lowered = command.lower()
    return any(keyword in lowered for keyword in DANGEROUS_KEYWORDS)

def confirm_dangerous(command: str) -> bool:
    confirm = input(f"⚠️ REALLY run this? It may be potentially disastrous:\n    {command}\n[Y/n]: ").strip().lower()
    return confirm in {"y", "yes", ""}

def detect_terminal() -> str:
    for term in [
        "konsole",         # KDE
        "gnome-terminal",  # GNOME
        "xfce4-terminal",  # XFCE
        "lxterminal",      # LXDE
        "qterminal",       # LXQt
        "tilix",           # GNOME alt
        "xterm",           # fallback
        "mate-terminal",   # MATE
        "alacritty",       # Modern GPU term
        "terminator"       # Advanced
    ]:
        if shutil.which(term):
            return term
    return None

def launch_in_terminal(command: str) -> str:
    terminal = detect_terminal()
    if terminal:
        quoted_cmd = shlex.quote(command)
        if "konsole" in terminal:
            cmd = f"{terminal} -e bash -c {quoted_cmd}"
        elif "gnome-terminal" in terminal or "xfce4-terminal" in terminal or "mate-terminal" in terminal:
            cmd = f"{terminal} -- bash -c {quoted_cmd}"
        elif "lxterminal" in terminal:
            cmd = f"{terminal} -e bash -c {quoted_cmd}"
        elif "qterminal" in terminal or "tilix" in terminal or "xterm" in terminal or "terminator" in terminal:
            cmd = f"{terminal} -e bash -c {quoted_cmd}"
        elif "alacritty" in terminal:
            cmd = f"{terminal} -e bash -c {quoted_cmd}"
        else:
            return f"⚠️ Terminal '{terminal}' is not supported."

        subprocess.Popen(cmd, shell=True)
        return f"🚀 Launched in {terminal}: {command}"
    else:
        return f"⚠️ No supported terminal emulator found."

def execute_command(command: str) -> str:
    try:
        if is_dangerous_command(command):
            if not confirm_dangerous(command):
                return "🛑 Command skipped for safety."

        if is_interactive_command(command):
            return launch_in_terminal(command)

        # Run non-interactive commands inline
        result = subprocess.run(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10
        )
        output = result.stdout.strip()
        error = result.stderr.strip()

        if result.returncode == 0:
            return f"✅ Success:\n{output}"
        else:
            return f"⚠️ Error (code {result.returncode}):\n{error or output}"

    except subprocess.TimeoutExpired:
        return f"❌ Timeout: Command took too long"
    except Exception as e:
        return f"❌ Exception: {str(e)}"
