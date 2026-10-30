"""Expt 2 - Data Dashboard Connector (MCP).

Tool: get_current_weather(location) -> fetches live data from wttr.in (no API key needed).
"""
from urllib.parse import quote

import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("weather-dashboard")


@mcp.tool()
def get_current_weather(location: str) -> str:
    """Get the current weather for a city or place.

    Args:
        location: City or place name, e.g. "Tokyo" or "Chennai".
    """
    url = f"https://wttr.in/{quote(location.strip())}"
    try:
        resp = httpx.get(
            url, params={"format": "j1"}, timeout=10,
            headers={"User-Agent": "mcp-weather-lab/1.0"},
        )
        resp.raise_for_status()
        data = resp.json()
        cur = data["current_condition"][0]
        area = data["nearest_area"][0]
    except httpx.TimeoutException:
        return f"ERROR: the weather service timed out for '{location}'. Try again."
    except httpx.HTTPStatusError as e:
        return f"ERROR: could not find weather for '{location}' (HTTP {e.response.status_code})."
    except (httpx.HTTPError, ValueError, KeyError, IndexError):
        return f"ERROR: could not get valid weather data for '{location}'."

    place = f"{area['areaName'][0]['value']}, {area['country'][0]['value']}"
    return (
        f"Location: {place}\n"
        f"Condition: {cur['weatherDesc'][0]['value']}\n"
        f"Temperature: {cur['temp_C']} C (feels like {cur['FeelsLikeC']} C)\n"
        f"Humidity: {cur['humidity']}%\n"
        f"Wind: {cur['windspeedKmph']} km/h {cur['winddir16Point']}\n"
        f"Precipitation: {cur['precipMM']} mm\n"
        f"Visibility: {cur['visibility']} km\n"
        f"UV index: {cur['uvIndex']}"
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")
