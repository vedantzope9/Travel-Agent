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
# query = "Give flights from HYD to BLR on 2025-09-18 \n 2. give some images of places to visit in Bengaluru "

query= "Give me information about places to visit in Pune and information about it \n 2. Give me images where to visit in Pune \n3. Search flight tickets from NGP to PNQ on 2025-09-18 "
result = portia.run(query)
print(result.outputs.final_output.value)
