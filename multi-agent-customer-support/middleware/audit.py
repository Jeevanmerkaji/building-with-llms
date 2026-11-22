from langchain.agents.middleware import wrap_tool_call

@wrap_tool_call
def log_tool_calls(requests, handler):
    name = requests.tool_call["name"]
    print(f"audit")