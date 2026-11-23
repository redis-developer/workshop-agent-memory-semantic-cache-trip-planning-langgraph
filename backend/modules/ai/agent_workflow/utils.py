"""
Turning what the tools return into the cards the page shows, and the wording of the note for memories. `process_tool_call`
(`tools/middleware.py`) uses these after each tool call, so the cards are in the state, and on the page, before the
reply is written.
This is boilerplate. You do not need to change anything here.
"""

import json
import math
import re

from backend.modules.ai.types import Attachment, PlaceCard, WeatherCard


def get_nested(value, *path):
    """
    Read a value from nested data: get_nested(place, "attribution", "title") is place["attribution"]["title"].
    Gives None, not an error, as soon as one step is missing (the Python version of JavaScript's `?.`).
    """

    for key in path:
        if isinstance(value, dict):
            value = value.get(key)
        elif isinstance(value, list) and isinstance(key, int) and key < len(value):
            value = value[key]
        else:
            return None
    return value


def _round(number) -> int:
    """Round half up, like the page's JavaScript does (Python's `round` rounds halves to the even number)."""

    return math.floor((number or 0) + 0.5)


def _summaries_by_index(summary: str) -> dict[int, dict]:
    """
    Google writes one paragraph per place, such as "**Organi Chiado** [0] (4.7★ (3113)) offers a daily-changing menu."
    The number in brackets says which place it is about. Returns the rating and the sentence of each, by that number.
    """

    summaries: dict[int, dict] = {}
    for paragraph in re.split(r"\n\n+", summary):
        index = re.search(r"\[(\d+)\]", paragraph)
        if not index:
            continue
        rating = re.search(r"\((\d[\d.]*)★ \((\d+)\)", paragraph)
        description = re.sub(r"\*\*", "", paragraph)
        description = re.sub(r"\s*\[\d+\]", "", description, count=1)
        description = re.sub(r"\s*\(\d[\d.]*★ \(\d+\)\)", "", description, count=1)
        summaries[int(index.group(1))] = {
            "rating": f"{rating.group(1)}★ ({int(rating.group(2)):,})" if rating else None,
            "description": description.strip(),
        }
    return summaries


def place_cards(result: dict) -> list[PlaceCard]:
    summaries = _summaries_by_index(result.get("summary") or "")
    return [
        {
            "name": re.sub(r" - Google Maps$", "", str(get_nested(place, "attribution", "title") or "")),
            "rating": summaries.get(index, {}).get("rating"),
            "description": summaries.get(index, {}).get("description", ""),
            "url": get_nested(place, "googleMapsLinks", "placeUrl") or get_nested(place, "attribution", "url") or "",
        }
        for index, place in enumerate(result.get("places") or [])
    ]


def weather_card(result: dict) -> WeatherCard | None:
    weather = result.get("weather")
    if not weather:
        return None
    # A day's forecast has a high and a low. The weather right now has one temperature.
    day = weather.get("date")
    if weather.get("maxTemperature"):
        temperature = f"{_round(get_nested(weather, 'maxTemperature', 'degrees'))}° / {_round(get_nested(weather, 'minTemperature', 'degrees'))}°"
    else:
        temperature = f"{_round(get_nested(weather, 'temperature', 'degrees'))}°"
    air_quality = get_nested(result, "airQuality", "hourlyResults", 0, "indexes", 0)
    pollen_categories = get_nested(result, "pollen", "dailyForecast", "categories") or []
    return {
        "city": get_nested(result, "returnedLocation", "address") or "",
        "when": f"{day['year']}-{day['month']:02d}-{day['day']:02d}" if day else "now",
        "temperature": temperature,
        "condition": get_nested(weather, "weatherCondition", "description", "text") or "",
        "rainChance": get_nested(weather, "precipitation", "probability", "percent") or 0,
        "airQuality": f"{air_quality['category']} (AQI {air_quality['value']})" if air_quality else None,
        "pollen": " · ".join(f"{category['displayName']} {str(get_nested(category, 'index', 'category') or '').lower()}" for category in pollen_categories) or None,
        "source": weather.get("attribution"),
    }


def read_tool_result(message) -> dict | list:
    """What a tool returned, as the dict or list it was. Its message holds the JSON as text, or as a list of text parts."""

    content = message.content
    text = "".join(part.get("text", "") if isinstance(part, dict) else str(part) for part in content) if isinstance(content, list) else content
    try:
        return json.loads(text)
    except ValueError:
        return {}  # a tool that failed leaves an error message, not JSON


def maps_attachments(messages: list) -> list[Attachment]:
    """The places and weather the Google Maps tools found this turn, as cards for the page."""

    attachments: list[Attachment] = []
    for message in messages:
        if message.type != "tool":
            continue
        if message.name == "search_places":
            attachments.extend({"type": "place", "data": place} for place in place_cards(read_tool_result(message)))
        if message.name == "lookup_weather":
            weather = weather_card(read_tool_result(message))
            if weather:
                attachments.append({"type": "weather", "data": weather})
    return attachments


def memories_info(count: int) -> str:
    """The line for the page when memories were looked up, from the retrieve step and from the search tool alike."""

    return f"Found {count} memories" if count else "No memories found"
