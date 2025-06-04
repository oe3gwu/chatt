from openai import OpenAI
import json
from tools import execute_command

# Connect to your vLLM-compatible OpenAI endpoint
client = OpenAI(
    api_key="empty",
    base_url="empty"
)

# Tool definition for MCP-style tool call
tools = [
    {
        "type": "function",
        "function": {
            "name": "execute_command",
            "description": "Executes a bash command. Interactive ones will launch in a new terminal.",
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

def main():
    print("🤖 Shell Agent ready. Type commands (or 'exit' to quit).")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            print("👋 Goodbye.")
            break

        try:
            # Send user input to the model
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
