"""Crawl phase, part 2: the service network — branches, ATMs and payment terminals.

The locator pages (``/filiallar``, ``/atm``, ``/terminallar``, ``/shobeler``,
``/xaricde``) build their content in the browser, so the HTML contains none of
it. The site loads the data from two sources, which are used here as well:

* **Next.js Server Actions** — server functions the page calls with a POST
  request that carries a ``Next-Action: <id>`` header; the answer is an RSC
  (Flight) payload. Used for branches, sub-branches ("şöbə"), offices abroad
  and the branch filters ("open on weekends", "has safe boxes" …). The action
  ids change with every deployment of the site, so they are looked up by
  function name in the page's JavaScript instead of being hard-coded.
* **A REST API** (``/web-api/service-network/atm|terminal``) for ATMs and
  payment terminals.

The data exists only in Azerbaijani (the EN/RU locator pages redirect to AZ).
"""

from __future__ import annotations

import json
import logging
import re
from datetime import datetime, timezone
from typing import Any

import httpx

from .config import ScraperConfig
from .extract.rsc import parse_flight_rows
from .http import create_client, request

log = logging.getLogger(__name__)

LOCATOR_PAGE = "/filiallar"
ACTION_NAMES = ("getBranchFilters", "getBranches", "getSubBranches", "getAbroadOffices")
REST_ENDPOINTS = {"atms": "/web-api/service-network/atm", "terminals": "/web-api/service-network/terminal"}

_CHUNK_RE = re.compile(r"/_next/static/chunks/[^\"'\\\s]+?\.js")
_ACTION_RE = re.compile(r'createServerReference\)\("([0-9a-f]+)"[^)]*?"(\w+)"\)')
_UNDEFINED = "$undefined"  # how React encodes an `undefined` argument


class ServiceNetworkError(RuntimeError):
    pass


async def fetch_service_network(config: ScraperConfig) -> dict[str, Any]:
    """Download the service network and store it as ``data/raw/service_network.json``."""
    async with create_client(config) as client:
        actions = await _discover_action_ids(client, config)

        async def call(name: str, *args: Any) -> Any:
            return await _call_action(client, config, actions[name], list(args))

        filters = _unwrap(await call("getBranchFilters"))
        data = {
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "branches": _unwrap(await call("getBranches", _UNDEFINED)),
            "sub_branches": _unwrap(await call("getSubBranches")),
            "abroad_offices": _unwrap(await call("getAbroadOffices")),
            # filter title → ids of the branches it applies to
            "branch_filters": {
                item["title"]: [branch["id"] for branch in _unwrap(await call("getBranches", item["key"]))]
                for item in filters
            },
        }
        for key, path in REST_ENDPOINTS.items():
            response = await request(client, config, "GET", config.base_url + path)
            response.raise_for_status()
            data[key] = _unwrap(response.json())

    config.service_network_path.parent.mkdir(parents=True, exist_ok=True)
    config.service_network_path.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    log.info(
        "Service network: %d branches, %d sub-branches, %d offices abroad, %d ATMs, %d terminals",
        len(data["branches"]), len(data["sub_branches"]), len(data["abroad_offices"]),
        len(data["atms"]), len(data["terminals"]),
    )
    return data


async def _discover_action_ids(client: httpx.AsyncClient, config: ScraperConfig) -> dict[str, str]:
    """Find the current ids of the server actions in the locator page's JavaScript."""
    page = await request(client, config, "GET", config.base_url + LOCATOR_PAGE)
    page.raise_for_status()

    found: dict[str, str] = {}
    for chunk in sorted(set(_CHUNK_RE.findall(page.text))):
        script = await request(client, config, "GET", config.base_url + chunk)
        for action_id, name in _ACTION_RE.findall(script.text):
            if name in ACTION_NAMES:
                found[name] = action_id
        if len(found) == len(ACTION_NAMES):
            return found
    missing = sorted(set(ACTION_NAMES) - found.keys())
    raise ServiceNetworkError(f"Server actions not found in the site's JavaScript: {missing}")


async def _call_action(client: httpx.AsyncClient, config: ScraperConfig, action_id: str, args: list[Any]) -> Any:
    """Invoke a server action the way the browser does and return its result."""
    response = await request(
        client, config, "POST", config.base_url + LOCATOR_PAGE,
        headers={"Next-Action": action_id, "Accept": "text/x-component", "Content-Type": "text/plain;charset=UTF-8"},
        content=json.dumps(args),
    )
    response.raise_for_status()
    # Row 0 is the action envelope ({"a": "$@1", ...}); row 1 holds the return value.
    rows = parse_flight_rows(response.text)
    if "1" not in rows:
        raise ServiceNetworkError(f"Unexpected server action response: {response.text[:200]}")
    return rows["1"]


def _unwrap(value: Any) -> list[dict[str, Any]]:
    """Results come either as a list or as a Strapi envelope ``{"data": [...], "meta": ...}``."""
    items = value.get("data", []) if isinstance(value, dict) else value
    return [item for item in items if isinstance(item, dict)]
