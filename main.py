# main.py

import os
import json
import re
import readline
import atexit
from openai import OpenAI
from tools import execute_command

def load_config():
    config = {}
    base_path = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(base_path, "config.txt")
    try:
        with open(file_path) as f:
            for line in f:
                line = line.strip()
                if line and "=" in line and not line.startswith("#"):
                    key, value = line.split("=", 1)
                    config[key.strip()] = value.strip()
    except FileNotFoundError:
        print(f"⚠ Warning: {file_path} not found.")
    return config

HISTORY_FILE = os.path.expanduser("~/.chatt_history")
try:
    readline.read_history_file(HISTORY_FILE)
except FileNotFoundError:
    pass
atexit.register(readline.write_history_file, HISTORY_FILE)
readline.set_history_length(500)

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

def handle_suggested_command(message_content: str):
    try:
        # Show assistant message for transparency
        print("🧠 Raw suggestion from assistant:")
        print(message_content)

        # Look for something that starts like a JSON dict and contains "command":
        if "command" not in message_content:
            print("🟡 No command detected.")
            return

        # Fix common JSON issues
        fixed = message_content.strip()

        # Try to repair missing quote after 'execute_command'
        fixed = re.sub(r'"name":\s*"execute_command([^"]*)"', r'"name": "execute_command"', fixed)

        # Fix unquoted keys or missing braces (best-effort)
        fixed = re.sub(r"([,{])\s*'([^']+)'\s*:", r'\1 "\2":', fixed)
        fixed = re.sub(r":\s*'([^']+)'", r': "\1"', fixed)

        # Attempt to parse the fixed JSON
        cmd_obj = json.loads(fixed)

        if cmd_obj.get("name") == "execute_command":
            suggested_command = cmd_obj["parameters"]["command"]
            confirm = input(f"🧠 The assistant suggests: '{suggested_command}'. Run it? [Y/n]: ").strip().lower()
            if confirm in {"", "y", "yes"}:
                result = execute_command(suggested_command)
                print(result)
            else:
                print("❎ Skipped.")
        else:
            print("🟡 Not an execute_command suggestion.")

    except json.JSONDecodeError as e:
        print(f"⚠️ Invalid JSON from assistant. Cannot parse suggestion.\n{e}")
    except Exception as e:
        print(f"⚠️ Failed to process suggestion: {e}")


def main():
    config = load_config()

    if not all(k in config and config[k] for k in ("api_key", "base_url", "model")):
        print("❌ ERROR: config.txt must include non-empty api_key, base_url, and model.")
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

if __name__ == "__main__":
    main()
