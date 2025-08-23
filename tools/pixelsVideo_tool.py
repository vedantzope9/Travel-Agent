import os
import requests
from typing import ClassVar, Tuple
from pydantic import BaseModel, Field
from portia import Tool, ToolRunContext


class PexelsVideoSearchInput(BaseModel):
    query: str = Field(..., description="The search query for finding travel videos")


class PexelsVideoSearchTool(Tool):
    id: str = "pexels_video_search"
    name: str = "Pexels Video Search"
    description: str = "Search and retrieve travel videos from Pexels API using a search query"

    args_schema: type[BaseModel] = PexelsVideoSearchInput
    output_schema: ClassVar[Tuple[str, str]] = (
        "string",
        "Returns search results with video URLs from Pexels"
    )

    # Declare the API key as a Pydantic field
    api_key: str = Field(..., description="Pexels API key for authentication")

    def run(self, context: ToolRunContext, query: str) -> str:
        headers = {"Authorization": self.api_key}
        url = f"https://api.pexels.com/videos/search?query={query}&per_page=5"
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        results = response.json()
        videos = results.get("videos", [])

        if not videos:
            return f"No videos found for '{query}' on Pexels"

        # Extract video URLs (HD or fallback)
        video_list = []
        for i, video in enumerate(videos[:5], 1):
            # prefer HD file if available
            files = video.get("video_files", [])
            # find the first HD or fallback to first file
            src = None
            for f in files:
                if f.get("quality") == "hd":
                    src = f.get("link")
                    break
            if not src and files:
                src = files[0].get("link")
            if src:
                video_list.append(f"{i}. {src}")

        if not video_list:
            return f"No valid video URLs found for '{query}'"

        return f"Found {len(video_list)} videos for '{query}':\n" + "\n".join(video_list)