import os
from dotenv import load_dotenv
from sympy.polys.polyconfig import query

from tools.pexels_tool import PexelsSearchTool
from tools.amadeus_tool import AmadeusScheduleTool
from tools.railradar_tool import RailRadarSearchTool, RailRadarSearchParams
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
    default_model="google/gemini-2.5-flash",
    google_api_key=os.getenv('GOOGLE_API_KEY')
)

# Create tool instance with API key (using   Pydantic field)
pexels_tool = PexelsSearchTool(api_key=os.getenv('PEXELS_API_KEY'))
flight_tool = AmadeusScheduleTool(
    api_key=os.getenv("AMADEUS_API_KEY"),
    api_secret=os.getenv("AMADEUS_API_SECRET")
)

# Use the SAME configured instance in registry

all_custom_tools = [pexels_tool , flight_tool ]
custom_registry = ToolRegistry(all_custom_tools)
combined_registry = example_tool_registry + custom_registry

# Instantiate Portia with Pexels tool
portia = Portia(config=google_config, tools=combined_registry)

# Run query
#query= "Give me information about places to visit in Bengaluru and information about it\n2. Why shou2. Using AmadeusScheduleTool:  Search flight tickets from DEL to BLR on 2025-09-18 \n 3. Give me images where to visit in Bengaluru and enjoy holidays "

query = """Give me a detailed travel guide for Mumbai covering the following:
1. **Destination Overview**: Provide in-depth information about Mumbai, including its significance, tourist appeal, and the current live weather conditions.
2. **Places to Visit**: List the top places to visit in Pune, explaining the significance and reasons why each is recommended for holiday travelers.
3. **Flight Search**: Using AmadeusScheduleTool, search for flights from Delhi (DEL) to Bombay (BOM) for the journey date 2025-09-18 and show options with timings and estimated fares.
4. **Images**: Fetch images of the recommended attractions and places to visit in Mumbai using PexelsSearchTool for a visual reference."""

result = portia.run(query)
print(result.outputs.final_output.value)
