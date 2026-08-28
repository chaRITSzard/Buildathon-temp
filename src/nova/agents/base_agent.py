import json
import inspect

from litellm import completion

from nova.llm.client import LLM_MODEL, LLM_API_KEY


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
                "description": (
                    f"Argument for {name}."
                )
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

            response = completion(
                model=LLM_MODEL,
                api_key=LLM_API_KEY,
                messages=messages,
                tools=self.tool_schemas,
                tool_choice="auto"
            )

            message = response.choices[0].message

            if not message.tool_calls:
                return message.content

            messages.append(message)

            for tool_call in message.tool_calls:

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

                result = tool(**arguments)

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_name,
                    "content": json.dumps(
                        result,
                        default=str
                    )
                })