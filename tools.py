import subprocess
import shlex

# Commands that should run in Konsole
INTERACTIVE_COMMANDS = {"nano", "vim", "htop", "top", "less", "man", "apt"}

# Substrings that indicate danger (must be lowercase)
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

def execute_command(command: str) -> str:
    try:
        if is_dangerous_command(command):
            if not confirm_dangerous(command):
                return "🛑 Command skipped for safety."

        if is_interactive_command(command):
            terminal_cmd = f"konsole --noclose -e bash -c {shlex.quote(command)}"
            subprocess.Popen(terminal_cmd, shell=True)
            return f"🚀 Launched in Konsole: {command}"

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
