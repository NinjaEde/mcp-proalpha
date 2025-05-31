import os
import json

PROMPTS_FILE = os.path.join(os.path.dirname(__file__), "..", "mcp_prompts.json")

def load_prompts():
    with open(PROMPTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f).get("prompts", {})

def get_prompt_template(prompt_name: str) -> str:
    prompts = load_prompts()
    prompt = prompts.get(prompt_name)
    if prompt:
        return prompt.get("template", "")
    raise KeyError(f"Prompt '{prompt_name}' not found in mcp_prompts.json")

def render_prompt(template: str, **kwargs) -> str:
    # Simple variable replacement using str.format
    return template.replace("{{", "{").replace("}}", "}").format(**kwargs)

def load_prompt(prompt_name: str, prompts_dir: str = "prompts") -> str:
    """
    Load a prompt template from a file in the prompts directory.
    """
    path = os.path.join(prompts_dir, f"{prompt_name}.txt")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

# Placeholder for future prompt logic or loading
# You can implement prompt loading or prompt-related utilities here if needed
