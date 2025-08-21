from typing import ClassVar, Tuple
from pydantic import BaseModel, Field
import requests
from portia import Tool, ToolRunContext


class FlightSearchInput(BaseModel):
    origin: str = Field(..., description="IATA code of the origin city (e.g., DEL)")
    destination: str = Field(..., description="IATA code of the destination city (e.g., BOM)")
    date: str = Field(..., description="Date of travel in YYYY-MM-DD format")


class FlightSearchTool(Tool):
    id: str = "flight_search"
    name: str = "Flight Search"
    description: str = "Search available flights between two airports for a given date"
    args_schema: type[BaseModel] = FlightSearchInput
    output_schema: ClassVar[Tuple[str, str]] = ("string", "Returns available flights and their details")

    api_key: str = Field(..., description="Amadeus API key for authentication")
    api_secret: str = Field(..., description="Amadeus API secret for authentication")

    def _get_access_token(self) -> str:
        """Authenticate with Amadeus API and return an access token"""
        url = "https://test.api.amadeus.com/v1/security/oauth2/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "client_credentials",
            "client_id": self.api_key,
            "client_secret": self.api_secret
        }

        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        return response.json()["access_token"]

    def run(self, context: ToolRunContext, origin: str, destination: str, date: str) -> str:
        # Step 1: Get OAuth token
        token = self._get_access_token()

        # Step 2: Call flight search endpoint
        url = "https://test.api.amadeus.com/v2/shopping/flight-offers"
        headers = {"Authorization": f"Bearer {token}"}
        params = {
            "originLocationCode": origin,
            "destinationLocationCode": destination,
            "departureDate": date,
            "adults": 1
        }

        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()

        data = response.json()
        offers = data.get("data", [])

        if not offers:
            return f"No flights found from {origin} to {destination} on {date}"

        flights = []
        for offer in offers[:5]:  # take top 5 flights
            price = offer["price"]["total"]
            segments = offer["itineraries"][0]["segments"]
            carrier = segments[0]["carrierCode"]
            flights.append(f"{carrier} | Price: {price} EUR")

        return "\n".join(flights)
