import subprocess
import shlex

# Commands that should open in a new Konsole window
INTERACTIVE_COMMANDS = {"nano", "vim", "htop", "top", "less", "man"}

def is_interactive_command(command: str) -> bool:
    return any(command.strip().startswith(cmd) for cmd in INTERACTIVE_COMMANDS)

def execute_command(command: str) -> str:
    try:
        if is_interactive_command(command):
            # Use KDE's Konsole
            terminal_cmd = f"konsole --noclose -e bash -c {shlex.quote(command)}"
            subprocess.Popen(terminal_cmd, shell=True)
            return f"🚀 Launched in Konsole: {command}"

        # Run regular command
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
