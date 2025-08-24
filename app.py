import os
from dotenv import load_dotenv
from typing import Any, Dict, List, Optional
from pydantic import BaseModel
import json

# Correct imports for current Portia SDK version
from portia import (
    Config,
    LLMProvider,
    Portia,
    ToolRegistry,
    example_tool_registry,
)
from portia.plan import PlanBuilder

# Import your custom tools
from tools.pexels_tool import PexelsSearchTool
from tools.amadeus_tool import AmadeusScheduleTool

load_dotenv()

# Disable telemetry
os.environ["ANONYMIZED_TELEMETRY"] = "false"

class WeatherInfo(BaseModel):
    temperature: Optional[str] = None
    condition: Optional[str] = None
    humidity: Optional[str] = None
    wind_speed: Optional[str] = None
    error: Optional[str] = None


class DestinationInfo(BaseModel):
    city_name: str
    description: Optional[str] = None
    best_time_to_visit: Optional[str] = None
    culture_info: Optional[str] = None
    weather: Optional[WeatherInfo] = None
    error: Optional[str] = None


class PlaceToVisit(BaseModel):
    name: str
    description: Optional[str] = None
    significance: Optional[str] = None
    why_visit: Optional[str] = None
    location: Optional[str] = None
    best_time_to_visit: Optional[str] = None


class PlacesToVisit(BaseModel):
    places: List[PlaceToVisit] = []
    total_places: int = 0
    error: Optional[str] = None


class FlightOffer(BaseModel):
    airline: Optional[str] = None
    flight_number: Optional[str] = None
    departure_time: Optional[str] = None
    arrival_time: Optional[str] = None
    duration: Optional[str] = None
    price: Optional[str] = None
    currency: Optional[str] = None
    stops: Optional[int] = None


class FlightSearchResults(BaseModel):
    flights: List[FlightOffer] = []
    search_date: Optional[str] = None
    source: Optional[str] = None
    destination: Optional[str] = None
    total_results: int = 0
    error: Optional[str] = None


class ImageResult(BaseModel):
    url: str
    photographer: Optional[str] = None
    alt_text: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None


class ImageSearchResults(BaseModel):
    images: List[ImageResult] = []
    query: Optional[str] = None
    total_images: int = 0
    error: Optional[str] = None



def create_travel_plan():
    """Create travel planning agent using stable PlanBuilder with CORRECT tool IDs"""

    plan = PlanBuilder(
        "Comprehensive Travel Planning Agent - Corrected Version"

        # Define plan inputs first
    ).input(
        name="source",
        description="Source airport code (e.g., DEL)"
    ).input(
        name="destination",
        description="Destination airport code (e.g., BLR)"
    ).input(
        name="date_of_journey",
        description="Journey date in YYYY-MM-DD format"
    ).input(
        name="destination_city_name",
        description="Full destination city name for information search"

        # STEP 1: Get detailed destination information including weather
    ).step(
        task="Search for comprehensive destination information about the city including current weather conditions, climate, best time to visit, cultural highlights, historical significance, and general tourist information",
        tool_id="search_tool",
        output="$destination_info"
    ).input(
        name="destination_city_name",
        description="Full destination city name for information search"

        # STEP 2: Get places to visit with significance and reasons
    ).step(
        task="Search for top tourist attractions, historical sites, cultural landmarks, and must-visit places in the destination city. Include detailed descriptions, historical significance, cultural importance, and compelling reasons why tourists should visit each place",
        tool_id="search_tool",
        output="$places_to_visit"
    ).input(
        name="destination_city_name",
        description="Destination city name for places search"

        # STEP 3: Search flights using Amadeus tool - CORRECTED TOOL ID
    ).step(
        task="Search for available flight options from source to destination on the specified date using Amadeus API. Include comprehensive flight details like airlines, departure/arrival times, duration, prices, and number of stops",
        tool_id="amadeus_schedule",  # ← CORRECTED: Use actual tool ID from AmadeusScheduleTool.id
        output="$flight_results"
    ).input(
        name="source",
        description="Source airport code (e.g., DEL)"
    ).input(
        name="destination",
        description="Destination airport code (e.g., BLR)"
    ).input(
        name="date_of_journey",
        description="Journey date in YYYY-MM-DD format"
    ).condition(
        condition="source and destination and date_of_journey are provided and not empty"

        # STEP 4: Get destination images using Pexels tool - CORRECTED TOOL ID
    ).step(
        task="Search for high-quality, beautiful images of tourist attractions, landmarks, cultural sites, and scenic places in the destination city for holiday planning and visual inspiration",
        tool_id="pexels_search",  # ← CORRECTED: Use actual tool ID from PexelsSearchTool.id
        output="$destination_images"
    ).input(
        name="destination_city_name",
        description="Destination city name for image search"

        # STEP 5: Compile comprehensive travel plan with error handling
    ).step(
        task="Create a comprehensive travel plan by combining all gathered information. Handle any API failures gracefully by acknowledging failures and providing recommendations based on available data. Generate detailed summary, travel recommendations, and status report. If any step failed, include appropriate error messages without generating false data.",
        tool_id="llm_tool",
        output="$final_plan"
    ).input(
        name="$destination_info",
        description="Destination information from search step"
    ).input(
        name="$places_to_visit",
        description="Places to visit information from search step"
    ).input(
        name="$flight_results",
        description="Flight search results from Amadeus API"
    ).input(
        name="$destination_images",
        description="Destination images from Pexels API"
    ).input(
        name="source",
        description="Source airport code for context"
    ).input(
        name="destination",
        description="Destination airport code for context"
    ).input(
        name="date_of_journey",
        description="Journey date for context"
    ).input(
        name="destination_city_name",
        description="Destination city name for context"
    ).build()

    return plan


# =============================================================================
# CORRECTED MAIN EXECUTION FUNCTION
# =============================================================================

def run_travel_planning_agent(source: str, destination: str, date_of_journey: str, destination_city_name: str):
    """Execute the travel planning agent with corrected tool registration"""

    try:
        # Setup configuration - EXACT SAME AS YOUR WORKING EXAMPLE
        config = Config.from_default(
            llm_provider=LLMProvider.GOOGLE,
            default_model="google/gemini-2.5-flash",
            google_api_key=os.getenv('GOOGLE_API_KEY')
        )

        # Setup tools - EXACT SAME AS YOUR WORKING EXAMPLE
        pexels_tool = PexelsSearchTool(api_key=os.getenv('PEXELS_API_KEY'))
        flight_tool = AmadeusScheduleTool(
            api_key=os.getenv("AMADEUS_API_KEY"),
            api_secret=os.getenv("AMADEUS_API_SECRET")
        )

        # Debug: Print tool IDs to verify
        print(f"Pexels tool ID: {pexels_tool.id}")
        print(f"Amadeus tool ID: {flight_tool.id}")

        # Create registry - EXACT SAME AS YOUR WORKING EXAMPLE
        all_custom_tools = [pexels_tool, flight_tool]
        custom_registry = ToolRegistry(all_custom_tools)
        combined_registry = example_tool_registry + custom_registry

        # Debug: Print all available tool IDs
        print("Available tools:")
        for tool in combined_registry.tools:
            print(f"- {tool.id}")

        # Initialize Portia - EXACT SAME AS YOUR WORKING EXAMPLE
        portia = Portia(config=config, tools=combined_registry)

        # Create and run plan
        plan = create_travel_plan()

        # Execute with inputs - CORRECTED: Remove $ prefix for plan_run_inputs
        plan_run_inputs = {
            "source": source,
            "destination": destination,
            "date_of_journey": date_of_journey,
            "destination_city_name": destination_city_name
        }

        plan_run = portia.run_plan(plan, plan_run_inputs=plan_run_inputs)

        # Extract outputs safely
        step_outputs = plan_run.outputs.step_outputs
        final_output = plan_run.outputs.final_output.value if hasattr(plan_run.outputs.final_output, 'value') else str(
            plan_run.outputs.final_output)

        # Parse outputs with error handling
        def safe_parse_output(output_data):
            if isinstance(output_data, dict) and 'value' in output_data:
                return output_data['value']
            return output_data or {}

        destination_info = safe_parse_output(step_outputs.get("$destination_info", {}))
        places_info = safe_parse_output(step_outputs.get("$places_to_visit", {}))
        flight_info = safe_parse_output(step_outputs.get("$flight_results", {}))
        images_info = safe_parse_output(step_outputs.get("$destination_images", {}))

        # Create structured response
        result = {
            "destination_info": {
                "city_name": destination_city_name,
                "description": str(destination_info)[:500] if destination_info else "Information not available",
                "error": None if destination_info else "Failed to get destination info"
            },
            "places_to_visit": {
                "places": places_info if isinstance(places_info, list) else [],
                "total_places": len(places_info) if isinstance(places_info, list) else 0,
                "error": None if places_info else "Failed to get places information"
            },
            "flight_results": {
                "flights": flight_info if isinstance(flight_info, list) else [],
                "search_date": date_of_journey,
                "source": source,
                "destination": destination,
                "total_results": len(flight_info) if isinstance(flight_info, list) else 0,
                "error": None if flight_info else "Failed to invoke Amadeus API"
            },
            "destination_images": {
                "images": images_info if isinstance(images_info, list) else [],
                "query": destination_city_name,
                "total_images": len(images_info) if isinstance(images_info, list) else 0,
                "error": None if images_info else "Failed to invoke Pexels API"
            },
            "summary": final_output,
            "recommendations": [
                "Check weather conditions before traveling",
                "Book flights in advance for better prices",
                "Plan your itinerary based on place significance"
            ],
            "status": "SUCCESS" if all(
                [destination_info, places_info, flight_info, images_info]) else "PARTIAL_SUCCESS",
            "generated_at": "2025-08-24T11:12:00Z"
        }

        return result

    except Exception as e:
        return {
            "destination_info": {"city_name": destination_city_name, "error": f"System error: {str(e)}"},
            "places_to_visit": {"places": [], "total_places": 0, "error": "System error prevented places search"},
            "flight_results": {"flights": [], "search_date": date_of_journey, "source": source,
                               "destination": destination, "total_results": 0,
                               "error": "Failed to invoke Amadeus API - system error"},
            "destination_images": {"images": [], "query": destination_city_name, "total_images": 0,
                                   "error": "Failed to invoke Pexels API - system error"},
            "summary": f"Travel planning failed: {str(e)}",
            "recommendations": ["Check API keys", "Verify connectivity", "Try again later"],
            "status": "ERROR",
            "generated_at": "2025-08-24T11:12:00Z"
        }


if __name__ == "__main__":
    # Disable telemetry logging
    os.environ["ANONYMIZED_TELEMETRY"] = "false"

    result = run_travel_planning_agent(
        source="DEL",
        destination="BLR",
        date_of_journey="2025-09-18",
        destination_city_name="Bengaluru"
    )

    # Print JSON result for frontend
    print(json.dumps(result, indent=2, ensure_ascii=False))

    # Safe status checking
    print(f"\n✅ Status: {result['status']}")

    # Only check dictionary values for errors, avoid strings
    successful_components = sum(1 for key, value in result.items()
                                if isinstance(value, dict) and not value.get('error'))
    print(f"📊 Components: {successful_components} successful")
