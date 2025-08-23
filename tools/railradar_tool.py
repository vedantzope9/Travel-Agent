import os
import requests
from datetime import datetime
from typing import List
from pydantic import BaseModel, Field, PrivateAttr
from portia import Tool, ToolRunContext


class RailRadarSearchParams(BaseModel):
    origin: str = Field(..., description="Origin station code, e.g. 'NDLS'")
    destination: str = Field(..., description="Destination station code, e.g. 'BCT'")
    journey_date: str = Field(..., description="Journey date in YYYY-MM-DD format")


class TrainCoachInfo(BaseModel):
    class_code: str
    status: str
    available_seats: int
    waiting_list: int
    fare: str
    confirmation_probability: str


class TrainInfo(BaseModel):
    train_number: str
    train_name: str
    departure_time: str
    arrival_time: str
    coaches: List[TrainCoachInfo]


class RailRadarSearchTool(Tool):
    """RailRadar.in search tool for Portia AI"""

    id: str = "railradar_search"
    name: str = "RailRadar Train Search"
    description: str = "Search trains between stations with detailed seat availability"
    args_schema: type[BaseModel] = RailRadarSearchParams
    output_schema: tuple[str, str] = ("List[TrainInfo]", "List of trains with seat availability")

    _api_key: str = PrivateAttr()
    _base_url: str = PrivateAttr(default="https://railradar.in/api/v1/trains/between")

    def __init__(self):
        super().__init__()
        self._api_key = os.getenv("RAILRADAR_API_KEY", "")

    def run(self, context: ToolRunContext, origin: str, destination: str, journey_date: str) -> List[TrainInfo]:
        params = RailRadarSearchParams(origin=origin, destination=destination, journey_date=journey_date)
        date_api = datetime.strptime(params.journey_date, "%Y-%m-%d").strftime("%Y-%m-%d")  # keep YYYY-MM-DD

        query = {
            "from": params.origin,
            "to": params.destination,
            "date": date_api,
            "availability": "true",
            "coaches": "true",
        }

        headers = {"x-api-key": self._api_key}

        resp = requests.get(self._base_url, params=query, headers=headers, timeout=10)
        resp.raise_for_status()

        trains_data = resp.json().get("trains", [])
        results: List[TrainInfo] = []

        for t in trains_data:
            coaches: List[TrainCoachInfo] = []
            for cls in t.get("classes", []):
                coaches.append(TrainCoachInfo(
                    class_code=cls.get("code", ""),
                    status=cls.get("status", ""),
                    available_seats=int(cls.get("available", 0)),
                    waiting_list=int(cls.get("wl", 0)),
                    fare=str(cls.get("fare", "N/A")),
                    confirmation_probability=str(cls.get("confirm_prob", "N/A")),
                ))

            results.append(TrainInfo(
                train_number=str(t.get("number", "")),
                train_name=t.get("name", ""),
                departure_time=t.get("dep_time", ""),
                arrival_time=t.get("arr_time", ""),
                coaches=coaches,
            ))

        return results


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv(override=True)

    tool = RailRadarSearchTool()
    trains = tool.run(None, origin="NGP", destination="PNQ", journey_date="2025-08-23")

    for tr in trains:
        print(f"{tr.train_number} {tr.train_name} {tr.departure_time}→{tr.arrival_time}")
        for c in tr.coaches:
            print(f"  {c.class_code}: {c.status} Avl {c.available_seats} WL {c.waiting_list} Fare {c.fare}")
