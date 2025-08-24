import os
import asyncio
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from portia import Config, LLMProvider, Portia, ToolRegistry, example_tool_registry

# Import your tools
from tools.pexels_tool import PexelsSearchTool
from tools.amadeus_tool import AmadeusScheduleTool
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

# FastAPI app
app = FastAPI(title="Travel Guide API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request body schema
class TravelRequest(BaseModel):
    source: str
    destination: str
    journey_date: str


# Health check response model
class HealthResponse(BaseModel):
    message: str
    status: str


# Configure Portia
try:
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

    all_custom_tools = [pexels_tool, flight_tool]
    custom_registry = ToolRegistry(all_custom_tools)
    combined_registry = example_tool_registry + custom_registry

    portia = Portia(config=google_config, tools=combined_registry)

except Exception as e:
    print(f"Error initializing Portia: {e}")
    portia = None

@app.get("/health")
async def health_check():
    """Additional health check endpoint"""
    return {"status": "OK", "message": "Service is running"}

#
# @app.post("/travel-guide")
# async def travel_guide(request: TravelRequest):
#     """Generate a comprehensive travel guide"""
#     if portia is None:
#         raise HTTPException(status_code=500, detail="Service not properly initialized")
#
#     try:
#         query = f"""
#         Create a detailed travel guide covering the following:
#
#         1. **Destination Overview**: Provide information about {request.destination}, including its tourist appeal and live weather.
#         2. **Places to Visit**: List the top attractions in {request.destination}, with significance.
#         3. **Flight Search**: Using AmadeusScheduleTool, search flights from {request.source} to {request.destination} on {request.journey_date}, include timings and estimated fares.
#         4. **Images**: Fetch images of attractions in {request.destination} using PexelsSearchTool.
#         """
#
#         # Use asyncio.to_thread for the blocking operation
#         result = await asyncio.to_thread(portia.run, query)
#         return {"result": result.outputs.final_output.value}
#
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error generating travel guide: {str(e)}"}


@app.post("/travel-guide")
async def travel_guide(request: TravelRequest):
    if portia is None:
        raise HTTPException(status_code=500, detail="Service not properly initialized")

    try:
        query = f"""
        Create a detailed travel guide in pure JSON with this exact structure:
        {{
          "destination": {{
            "name": "{request.destination}",
            "overview": "string"
          }},
          "weather": {{
            "description": "string",
            "temperature": "string"
          }},
          "attractions": [
            {{
              "name": "string",
              "description": "string"
            }}
          ],
          "flights": [
            {{
              "airline": "string",
              "flight_number": "string",
              "departure": "ISO8601 datetime",
              "arrival": "ISO8601 datetime",
              "duration": "string",
              "price": "string"
            }}
          ],
          "images": [
            "image_url"
          ]
        }}

        Rules:
        - Always fill `overview` with 3–4 sentences about the destination.
        - Each attraction must include both `name` and a short `description`.
        - Use **AmadeusScheduleTool** to search flights from **{request.source}** to **{request.destination}** on {request.journey_date}.
        - Include ALL flights returned by AmadeusScheduleTool, do not truncate.
        - List at least 3 images from Pexels for attractions.
        """

        result = portia.run(query)

        # always enforce JSON return
        raw_output = result.outputs.final_output.value

        import re, json

        # strip markdown fencing if present
        cleaned = re.sub(r"```json|```", "", raw_output).strip()

        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError:
            # fallback: wrap plain text into JSON
            parsed = {"text": cleaned}

        return {"result": parsed}

    except Exception as e:
        import traceback; traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error generating travel guide: {str(e)}")


#uvicorn api:app --reload