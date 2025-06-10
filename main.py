import os
import json
import re
import readline
import atexit
from openai import OpenAI
from tools import execute_command

# ─────────────────────────────────────────────
# Load config.txt
# ─────────────────────────────────────────────
def load_config(file_path="config.txt"):
    config = {}
    try:
        with open(file_path) as f:
            for line in f:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    try:
                        key, value = line.split("=", 1)
                        config[key.strip()] = value.strip()
                    except ValueError:
                        continue  # skip malformed lines
    except FileNotFoundError:
        print(f"⚠ Warning: {file_path} not found.")
    return config

# ─────────────────────────────────────────────
# Persistent command history
# ─────────────────────────────────────────────
HISTORY_FILE = os.path.expanduser("~/.chatt_history")
try:
    readline.read_history_file(HISTORY_FILE)
except FileNotFoundError:
    pass
atexit.register(readline.write_history_file, HISTORY_FILE)
readline.set_history_length(500)

# ─────────────────────────────────────────────
# Startup screen
# ─────────────────────────────────────────────
def show_boot_screen():
    os.system("clear")
    print("\033[1;34m")
    print("    ██████╗██╗  ██╗ █████╗ ████████╗████████╗")
    print("   ██╔════╝██║  ██║██╔══██╗╚══██╔══╝╚══██╔══╝")
    print("   ██║     ███████║███████║   ██║      ██║   ")
    print("   ██║     ██╔══██║██╔══██║   ██║      ██║   ")
    print("   ╚██████╗██║  ██║██║  ██║   ██║      ██║   ")
    print("    ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝      ╚═╝   ")
    print("  Command Handling and Terminal Tool (CHATT)")
    print("  ------------------------------------------")
    print(" ")
    print("READY.\n")
    print("\033[0m")

# ─────────────────────────────────────────────
# Assistant suggestion parser
# ─────────────────────────────────────────────
def handle_suggested_command(message_content: str):
    try:
        match = re.search(r'{\s*"name"\s*:\s*"execute_command"\s*,\s*"parameters"\s*:\s*{[^}]+}}', message_content, re.DOTALL)
        if match:
            cmd_json = match.group(0)
            cmd_json_clean = cmd_json.replace("\n", " ").replace("\r", " ").strip()
            cmd_json_clean = re.sub(r',\s*}', '}', cmd_json_clean)
            cmd_json_clean = re.sub(r',\s*]', ']', cmd_json_clean)
            cmd_obj = json.loads(cmd_json_clean)

            if cmd_obj.get("name") == "execute_command":
                suggested_command = cmd_obj["parameters"]["command"]
                confirm = input(f"🧠 The assistant suggests: '{suggested_command}'. Run it? [Y/n]: ").strip().lower()
                if confirm in {"", "y", "yes"}:
                    result = execute_command(suggested_command)
                    print(result)
                else:
                    print("❎ Skipped.")
        else:
            print("🟡 No runnable suggestion detected.")
    except Exception as e:
        print(f"⚠️ Failed to parse command suggestion: {e}")

# ─────────────────────────────────────────────
# Main loop
# ─────────────────────────────────────────────
def main():
    config = load_config()

    required_keys = {"api_key", "base_url", "model"}
    if not required_keys.issubset(config):
        print("❌ ERROR: config.txt must include api_key, base_url, and model.")
        return

    client = OpenAI(
        api_key=config["api_key"],
        base_url=config["base_url"]
    )
    model_name = config["model"]

    show_boot_screen()
    print("Type your command. Type 'exit' to quit.\n")

    tools = [
        {
            "type": "function",
            "function": {
                "name": "execute_command",
                "description": "Executes a bash command. Interactive ones run in terminal, dangerous ones are confirmed.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "The shell command to run"
                        }
                    },
                    "required": ["command"]
                }
            }
        }
    ]

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Goodbye.")
            break

        if user_input.lower() in {"exit", "quit"}:
            print("👋 Goodbye.")
            break

        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": user_input}],
                tools=tools,
                tool_choice="auto"
            )

            message = response.choices[0].message
            tool_calls = message.tool_calls

            if not tool_calls:
                print("🤷 No tool call detected. Assistant says:")
                print(message.content)
                handle_suggested_command(message.content)
                continue

            for call in tool_calls:
                if call.function.name == "execute_command":
                    args = json.loads(call.function.arguments)
                    command = args.get("command")
                    print("🔧 Running:", command)
                    result = execute_command(command)
                    print(result)
                else:
                    print("❌ Unknown tool call:", call.function.name)

        except Exception as e:
            print(f"❌ Runtime error: {e}")

# ─────────────────────────────────────────────
if __name__ == "__main__":
    main()
