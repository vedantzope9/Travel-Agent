import os
from dotenv import load_dotenv
from tools.pexels_tool import PexelsSearchTool
from portia import (
    Config,
    LLMProvider,
    Portia,
    ToolRegistry,
    example_tool_registry,
)

load_dotenv()
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
PEXELS_API_KEY = os.getenv('PEXELS_API_KEY')

# Create Portia config
google_config = Config.from_default(
    llm_provider=LLMProvider.GOOGLE,
    default_model="google/gemini-2.5-pro",
    google_api_key=GOOGLE_API_KEY
)

# Create tool instance with API key (using Pydantic field)
pexels_tool = PexelsSearchTool(api_key=PEXELS_API_KEY)

# Use the SAME configured instance in registry
pexels_registry = ToolRegistry([pexels_tool])
combined_registry = example_tool_registry + pexels_registry

# Instantiate Portia with Pexels tool
portia = Portia(config=google_config, tools=combined_registry)

# Run query
result = portia.run("Search for travel images of the place Mumbai, Maharashtra, India using Pexels")
print(result.outputs.final_output.value)
