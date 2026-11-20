"""
Content that comes with a reply, for the page to render next to the chat. The type says what is in data.
The agent adds them from what its tools found, and the page draws them on the canvas.

The keys are the JSON the page reads, which is why they are in camelCase.
"""

from typing import Literal, NotRequired, TypedDict


class PlaceCard(TypedDict):
    """A place, as a card on the page."""

    name: str
    rating: NotRequired[str | None]  # for example "4.6★ (3,803)"
    description: str
    url: str


class WeatherSource(TypedDict):
    title: str
    url: str


class WeatherCard(TypedDict):
    """The weather, as a card on the page."""

    city: str
    when: str  # the day (YYYY-MM-DD), or "now"
    temperature: str
    condition: str
    rainChance: float
    airQuality: NotRequired[str | None]
    pollen: NotRequired[str | None]
    source: NotRequired[WeatherSource | None]  # where it comes from, to be shown with it


class PlaceAttachment(TypedDict):
    type: Literal["place"]
    data: PlaceCard


class WeatherAttachment(TypedDict):
    type: Literal["weather"]
    data: WeatherCard


Attachment = PlaceAttachment | WeatherAttachment
