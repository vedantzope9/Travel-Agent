import os
from dotenv import load_dotenv
from tools.pexels_tool import PexelsSearchTool
from tools.amadeus_tool import FlightSearchTool
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
flight_tool = FlightSearchTool(
    api_key=os.getenv("AMADEUS_API_KEY"),
    api_secret=os.getenv("AMADEUS_API_SECRET")
)

# Use the SAME configured instance in registry
custom_registry = ToolRegistry([pexels_tool,flight_tool])
combined_registry = example_tool_registry + custom_registry

# Instantiate Portia with Pexels tool
portia = Portia(config=google_config, tools=combined_registry)

# Run query
result = portia.run("find flights from nagpur to mumbai this month")
print(result.outputs.final_output.value)
