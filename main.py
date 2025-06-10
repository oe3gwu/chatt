import os
import json
import re
import readline
import atexit
from openai import OpenAI
from tools import execute_command

# Setup persistent history
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

# OpenAI-compatible client (works with vLLM)
client = OpenAI(
    api_key="empty",
    base_url="empty"
)

# Tool declaration for function calling
tools = [
    {
        "type": "function",
        "function": {
            "name": "execute_command",
            "description": "Executes a bash command. Interactive ones run in Konsole, dangerous ones ask for confirmation.",
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

def main():
    show_boot_screen()
    print("Type your command. Type 'exit' to quit.\n")

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
                model="RedHatAI/Llama-4-Scout-17B-16E-Instruct-quantized.w4a16",
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
