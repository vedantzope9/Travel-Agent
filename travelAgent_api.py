import os
import asyncio
import json
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from tools.pexels_tool import PexelsSearchTool
from tools.amadeus_tool import AmadeusScheduleTool
from portia import Config, LLMProvider, Portia, ToolRegistry, example_tool_registry

load_dotenv()

# --- FastAPI app setup ---
app = FastAPI(title="Travel Planner API")
from datetime import date

class TripRequest(BaseModel):
    source: str = Field(..., example="DEL")
    destination: str = Field(..., example="BLR")
    journey_date: date = Field(..., example="2025-09-18")

class Attraction(BaseModel):
    name: str
    significance: str
    image_url: str | None = None

class FlightOption(BaseModel):
    flight_no: str
    departure: str
    arrival: str
    price: str

class TripResponse(BaseModel):
    overview: str
    attractions: list[Attraction]
    flights: list[FlightOption]
    images: list[dict]  # fallback, rarely used

# --- Portia / Tools setup ---
google_config = Config.from_default(
    llm_provider=LLMProvider.GOOGLE,
    default_model="google/gemini-2.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY")
)
pexels_tool = PexelsSearchTool(api_key=os.getenv("PEXELS_API_KEY"))
flight_tool = AmadeusScheduleTool(
    api_key=os.getenv("AMADEUS_API_KEY"),
    api_secret=os.getenv("AMADEUS_API_SECRET")
)
custom_registry = ToolRegistry([pexels_tool, flight_tool])
portia = Portia(config=google_config, tools=example_tool_registry + custom_registry)

# --- Helper to run Portia query asynchronously ---
async def run_portia_query(prompt: str) -> str:
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, portia.run, prompt)
    return result.outputs.final_output.value

def build_prompt(req: TripRequest) -> str:
    return (
        f"Give me a detailed travel guide for {req.destination} covering the following:\n\n"
        "1. **Destination Overview**: Provide in-depth information about "
        f"{req.destination}, including its significance, tourist appeal, and the current live weather conditions.\n\n"
        "2. **Places to Visit**: List the top places to visit in "
        f"{req.destination}, explaining the significance and reasons why each is recommended for holiday travelers.\n\n"
        "3. **Flight Search**: Using AmadeusScheduleTool, search for flights from "
        f"{req.source} to {req.destination} for the journey date {req.journey_date} and show options with timings and estimated fares.\n\n"
        "4. **Images**: Fetch images of the recommended attractions and places to visit in "
        f"{req.destination} using PexelsSearchTool for a visual reference."
    )

def parse_flights(text: str) -> list[FlightOption]:
    flights = []
    # look for lines starting with '*' or numbers and parse entries
    lines = text.splitlines()
    for line in lines:
        if line.strip().startswith("*") and "Departure:" in line:
            # e.g. "*   **AI2995**"
            continue
        if line.strip().startswith("*") and "Departure:" not in line:
            # flight header line
            parts = line.split("**")
            flight_no = parts[1]
            flights.append(FlightOption(flight_no=flight_no, departure="", arrival="", price=""))
        if flights and "Departure:" in line:
            flights[-1].departure = line.split("Departure:")[1].strip()
        if flights and "Arrival:" in line:
            flights[-1].arrival = line.split("Arrival:")[1].strip()
        if flights and "Price:" in line:
            flights[-1].price = line.split("Price:")[1].strip()
    return flights

def parse_attractions_and_images(text: str) -> list[Attraction]:
    attractions = []
    sections = text.split("### ")
    for block in sections:
        if block.startswith("Top Attractions") or block.startswith("Places to Visit"):
            for line in block.splitlines():
                if line.startswith("*"):
                    # parse name
                    name = line.split("**")[1]
                    # next line for significance
                    idx = block.splitlines().index(line)
                    sig_line = block.splitlines()[idx+1].strip()
                    significance = sig_line.replace("*", "").strip()
                    attractions.append(Attraction(name=name, significance=significance))
    # attempt to attach image URLs found later
    for block in sections:
        if block.startswith("*   **") and "Image: [" in block:
            # pattern: *   **Gateway of India** ... Image: [Gateway of India](url)
            parts = block.split("Image: [")[1].split("](")
            name = block.split("**")[1]
            url = parts[1].rstrip(")")
            for attr in attractions:
                if attr.name == name:
                    attr.image_url = url
    return attractions

@app.post("/plan-trip", response_model=TripResponse)
async def plan_trip(req: TripRequest):
    raw = await run_portia_query(build_prompt(req))

    try:
        # Option A: split-and-parse
        overview = raw.split("###")[1].split("\n",1)[1].split("\n###")[0].strip()
        attractions = parse_attractions_and_images(raw)
        flights = parse_flights(raw)
        return TripResponse(
            overview=overview,
            attractions=attractions,
            flights=flights,
            images=[]
        )
    except Exception:
        # Option B: fallback LLM JSON extraction
        json_prompt = (
            "Extract the following JSON from the text below:\n"
            "{overview, attractions:[{name, significance, image_url}], flights:[{flight_no, departure, arrival, price}]}\n\n"
            f"Text:\n{raw}"
        )
        json_text = await run_portia_query(json_prompt)
        try:
            data = json.loads(json_text)
            return TripResponse(**data)
        except Exception as e:
            raise HTTPException(status_code=502, detail="Failed to parse response as JSON")

# To run:
# uvicorn travelAgent_api:app --reload
