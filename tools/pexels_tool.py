from typing import ClassVar, Tuple
from pydantic import BaseModel, Field
import requests
from portia import Tool, ToolRunContext


class PexelsSearchInput(BaseModel):
    query: str = Field(..., description="The search query for finding travel images")


class PexelsSearchTool(Tool):
    id: str = "pexels_search"
    name: str = "Pexels Image Search"
    description: str = "Search and retrieve travel images from Pexels API using a search query"
    args_schema: type[BaseModel] = PexelsSearchInput
    output_schema: ClassVar[Tuple[str, str]] = ("string", "Returns search results with image URLs from Pexels")

    # Define api_key as a Pydantic field
    api_key: str = Field(..., description="Pexels API key for authentication")

    def run(self, context: ToolRunContext, query: str) -> str:
        headers = {"Authorization": self.api_key}
        url = f"https://api.pexels.com/v1/search?query={query}&per_page=5"
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        results = response.json()
        photos = results.get('photos', [])

        if photos:
            urls = [photo['src']['medium'] for photo in photos[:5]]
            image_list = "\n".join([f"{i + 1}. {url}" for i, url in enumerate(urls)])
            return f"Found {len(urls)} images for '{query}':\n{image_list}"
        else:
            return f"No images found for '{query}' on Pexels"
