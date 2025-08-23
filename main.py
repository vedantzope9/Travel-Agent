import os
from dotenv import load_dotenv
from tools.pexels_tool import PexelsSearchTool
from tools.amadeus_tool import AmadeusScheduleTool
from portia import (
    Config,
    LLMProvider,
    Portia,
    ToolRegistry,
    example_tool_registry,
)

load_dotenv()

# Create Portia config
google_config = Config.from_default(
    llm_provider=LLMProvider.GOOGLE,
    default_model="google/gemini-2.5-pro",
    google_api_key=os.getenv('GOOGLE_API_KEY')
)

# Create tool instance with API key (using   Pydantic field)
pexels_tool = PexelsSearchTool(api_key=os.getenv('PEXELS_API_KEY'))
flight_tool = AmadeusScheduleTool(
    api_key=os.getenv("AMADEUS_API_KEY"),
    api_secret=os.getenv("AMADEUS_API_SECRET")
)

# Use the SAME configured instance in registry

all_custom_tools = [pexels_tool , flight_tool]
custom_registry = ToolRegistry(all_custom_tools)
combined_registry = example_tool_registry + custom_registry

# Instantiate Portia with Pexels tool
portia = Portia(config=google_config, tools=combined_registry)

# Run query
result = portia.run( "Fetch  scheduled flights from BOM to BLR on 2025-08-27")
print(result.outputs.final_output.value)
