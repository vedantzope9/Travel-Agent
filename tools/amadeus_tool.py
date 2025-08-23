import requests
from typing import ClassVar, Tuple
from pydantic import BaseModel, Field, ConfigDict
from portia import Tool, ToolRunContext


class FlightScheduleInput(BaseModel):
    origin: str = Field(..., description="Origin IATA code (e.g., NAG)")
    destination: str = Field(..., description="Destination IATA code (e.g., PNQ)")
    departure_date: str = Field(..., description="Departure date YYYY-MM-DD")


class AmadeusScheduleTool(Tool):
    id: str = "amadeus_schedule"
    name: str = "amadeus_schedule"
    description: str = "Get upcoming flights using Amadeus Flight Offers API"

    api_key: str = Field(..., description="Amadeus API Key")
    api_secret: str = Field(..., description="Amadeus API Secret")

    args_schema: type[BaseModel] = FlightScheduleInput
    output_schema: ClassVar[Tuple[str, str]] = (
        "string",
        "Returns upcoming flights with times and prices"
    )
    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)

    def get_access_token(self) -> str:
        resp = requests.post(
            "https://test.api.amadeus.com/v1/security/oauth2/token",
            data={
                "grant_type": "client_credentials",
                "client_id": self.api_key,
                "client_secret": self.api_secret
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        resp.raise_for_status()
        return resp.json()["access_token"]

    def run(self, context: ToolRunContext, origin: str, destination: str, departure_date: str) -> str:
        try:
            token = self.get_access_token()
            url = "https://test.api.amadeus.com/v2/shopping/flight-offers"
            headers = {"Authorization": f"Bearer {token}"}
            params = {
                "originLocationCode": origin.upper(),
                "destinationLocationCode": destination.upper(),
                "departureDate": departure_date,
                "adults": 1,
                "max": 5
            }

            resp = requests.get(url, headers=headers, params=params)
            resp.raise_for_status()

            payload = resp.json()
            flights = payload.get("data", [])

            if not flights:
                return f"No flights found from {origin} to {destination} on {departure_date}"

            result = f"✈️ Flights from {origin} to {destination} on {departure_date}:\n\n"

            for i, offer in enumerate(flights, 1):
                # FIXED: Access first segment in list
                itineraries = offer.get("itineraries", [])
                if not itineraries:
                    continue

                segments = itineraries[0].get("segments", [])
                if not segments:
                    continue

                seg = segments[0]  # ← FIXED: Get first segment from list

                dep = seg.get("departure", {})
                arr = seg.get("arrival", {})
                airline = seg.get("carrierCode", "N/A")
                number = seg.get("number", "N/A")

                # Defensive price lookup
                price_block = offer.get("price", {})
                total = price_block.get("total") or price_block.get("grandTotal") or "N/A"
                currency = price_block.get("currency", "")

                result += f"{i}. {airline}{number}\n"
                result += f"   Departure: {dep.get('iataCode', 'N/A')} at {dep.get('at', 'N/A')}\n"
                result += f"   Arrival: {arr.get('iataCode', 'N/A')} at {arr.get('at', 'N/A')}\n"
                result += f"   Price: {total} {currency}\n\n"

            return result

        except Exception as e:
            return f"Error fetching flights: {e}"


# Add this at the very bottom of your file, after the AmadeusScheduleTool class

if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    load_dotenv(override=True)

    # Create tool instance
    tool = AmadeusScheduleTool(
        api_key=os.getenv("AMADEUS_API_KEY"),
        api_secret=os.getenv("AMADEUS_API_SECRET")
    )

    # Mock context
    class MockContext:
        pass

    # Test single query
    result = tool.run(MockContext(), "DEL", "BLR", "2025-08-25")
    print(result)
