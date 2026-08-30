import json
import inspect

from nova.llm.client import completion_with_fallback


class BaseAgent:

    def __init__(
        self,
        name: str,
        system_prompt: str,
        tools: list
    ):
        self.name = name
        self.system_prompt = system_prompt
        self.tools = tools

        self.tool_map = {
            tool.__name__: tool
            for tool in tools
        }

        self.tool_schemas = [
            self._build_tool_schema(tool)
            for tool in tools
        ]

    def _build_tool_schema(self, tool):

        signature = inspect.signature(tool)

        properties = {}
        required = []

        for name, parameter in signature.parameters.items():

            properties[name] = {
                "type": "string",
                "description": f"Argument for {name}."
            }

            if parameter.default is inspect.Parameter.empty:
                required.append(name)

        return {
            "type": "function",
            "function": {
                "name": tool.__name__,
                "description": (
                    tool.__doc__
                    or f"Use {tool.__name__}."
                ),
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required
                }
            }
        }

    def run(self, question: str):

        messages = [
            {
                "role": "system",
                "content": self.system_prompt
            },
            {
                "role": "user",
                "content": question
            }
        ]

        while True:

            print(f"\n===== {self.name} LLM CALL =====")
            print(
                "TOOLS:",
                [
                    tool["function"]["name"]
                    for tool in self.tool_schemas
                ]
            )
            print("================================")

            response = completion_with_fallback(
                messages=messages,
                tools=self.tool_schemas
            )

            message = response.choices[0].message

            tool_calls = (
                getattr(message, "tool_calls", None)
                or []
            )

            if not tool_calls:
                return message.content or ""

            assistant_message = {
                "role": message.role,
                "content": message.content or "",
                "tool_calls": [
                    (
                        tool_call.model_dump(
                            exclude_none=True
                        )
                        if hasattr(tool_call, "model_dump")
                        else tool_call
                    )
                    for tool_call in tool_calls
                ]
            }

            messages.append(assistant_message)

            for tool_call in tool_calls:

                tool_name = tool_call.function.name

                arguments = json.loads(
                    tool_call.function.arguments
                    or "{}"
                )

                tool = self.tool_map.get(tool_name)

                if tool is None:
                    raise ValueError(
                        f"Unknown tool requested: {tool_name}"
                    )

                if inspect.signature(tool).parameters:
                    result = tool(**arguments)
                else:
                    result = tool()

                print(
                    f"\n===== {self.name} TOOL RESULT ====="
                )
                print("TOOL:", tool_name)
                print("RESULT TYPE:", type(result).__name__)
                print("===================================")

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_name,
                    "content": str(result)
                })