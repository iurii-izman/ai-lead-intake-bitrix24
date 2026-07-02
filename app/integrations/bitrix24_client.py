"""Bitrix24 client boundary for mock and real portal calls."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Protocol

import httpx
from tenacity import AsyncRetrying, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.config import Settings


class BitrixClientError(RuntimeError):
    """Base error for Bitrix24 adapter failures."""


class BitrixConfigurationError(BitrixClientError):
    """Raised when the Bitrix24 connection is not configured correctly."""


class BitrixRequestError(BitrixClientError):
    """Raised when Bitrix24 rejects the request with a non-retryable 4xx error."""


class BitrixRetryableError(BitrixClientError):
    """Raised for transient Bitrix24 failures that should be retried."""


class Bitrix24Client(Protocol):
    provider_name: str

    async def create_crm_item(self, payload: dict[str, Any]) -> "BitrixCallResult":
        """Create a CRM entity in universal mode."""

    async def create_lead(self, payload: dict[str, Any]) -> "BitrixCallResult":
        """Create a lead in legacy mode."""

    async def create_task(self, payload: dict[str, Any]) -> "BitrixCallResult":
        """Create a Bitrix task."""


@dataclass(slots=True, frozen=True)
class BitrixCallResult:
    method: str
    entity_type: str
    bitrix_id: int
    bitrix_url: str
    payload: dict[str, Any]
    raw_response: dict[str, Any]


@dataclass(slots=True)
class MockBitrix24Client:
    """Deterministic mock client used for demos and tests."""

    settings: Settings
    provider_name: str = "mock"

    async def create_crm_item(self, payload: dict[str, Any]) -> BitrixCallResult:
        return self._build_result("crm.item.add", "crm.item", payload)

    async def create_lead(self, payload: dict[str, Any]) -> BitrixCallResult:
        return self._build_result("crm.lead.add", "crm.lead", payload)

    async def create_task(self, payload: dict[str, Any]) -> BitrixCallResult:
        return self._build_result("tasks.task.add", "task", payload)

    def _build_result(
        self, method: str, entity_type: str, payload: dict[str, Any]
    ) -> BitrixCallResult:
        bitrix_id = _deterministic_id(method, payload)
        bitrix_url = f"https://mock.bitrix24.local/{entity_type.replace('.', '/')}/{bitrix_id}/"
        raw_response = {"result": {"id": bitrix_id}}
        return BitrixCallResult(
            method=method,
            entity_type=entity_type,
            bitrix_id=bitrix_id,
            bitrix_url=bitrix_url,
            payload=payload,
            raw_response=raw_response,
        )


@dataclass(slots=True)
class RealBitrix24Client:
    """HTTP client for incoming webhook Bitrix24 calls."""

    settings: Settings
    provider_name: str = "real"
    transport: httpx.AsyncBaseTransport | None = None

    async def create_crm_item(self, payload: dict[str, Any]) -> BitrixCallResult:
        return await self._post("crm.item.add", "crm.item", payload)

    async def create_lead(self, payload: dict[str, Any]) -> BitrixCallResult:
        return await self._post("crm.lead.add", "crm.lead", payload)

    async def create_task(self, payload: dict[str, Any]) -> BitrixCallResult:
        return await self._post("tasks.task.add", "task", payload)

    async def _post(
        self, method: str, entity_type: str, payload: dict[str, Any]
    ) -> BitrixCallResult:
        webhook_url = self.settings.bitrix24_webhook_url.rstrip("/")
        if not webhook_url:
            raise BitrixConfigurationError("BITRIX24_WEBHOOK_URL is not configured")

        payload_copy = json.loads(json.dumps(payload, ensure_ascii=False))
        request_payload = payload_copy

        async def _attempt() -> BitrixCallResult:
            async with httpx.AsyncClient(
                timeout=self.settings.bitrix_timeout_seconds,
                transport=self.transport,
            ) as client:
                try:
                    response = await client.post(
                        f"{webhook_url}/{method}.json", json=request_payload
                    )
                except httpx.TimeoutException as exc:
                    raise BitrixRetryableError(f"Bitrix24 timeout calling {method}") from exc
                except httpx.RequestError as exc:
                    raise BitrixRetryableError(
                        f"Bitrix24 transport error calling {method}"
                    ) from exc

            if response.status_code in {401, 403}:
                raise BitrixConfigurationError(
                    f"Bitrix24 authentication failed with HTTP {response.status_code}"
                )
            if response.status_code == 400:
                raise BitrixRequestError(f"Bitrix24 rejected the request for {method}")
            if response.status_code == 429 or response.status_code >= 500:
                raise BitrixRetryableError(
                    f"Bitrix24 returned HTTP {response.status_code} for {method}"
                )
            if response.status_code >= 400:
                raise BitrixRequestError(
                    f"Bitrix24 returned non-retryable HTTP {response.status_code} for {method}"
                )
            body = response.json()
            bitrix_id = _extract_bitrix_id(body)
            bitrix_url = _build_portal_url(self.settings, entity_type, bitrix_id)
            return BitrixCallResult(
                method=method,
                entity_type=entity_type,
                bitrix_id=bitrix_id,
                bitrix_url=bitrix_url,
                payload=request_payload,
                raw_response=body,
            )

        async for attempt in AsyncRetrying(
            retry=retry_if_exception_type(BitrixRetryableError),
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=0.2, min=0.2, max=1.0),
            reraise=True,
        ):
            with attempt:
                return await _attempt()

        raise BitrixClientError(f"Bitrix24 call failed for {method}")


def build_bitrix24_client(settings: Settings) -> Bitrix24Client:
    mode = settings.bitrix_mode.lower()
    if mode == "mock":
        return MockBitrix24Client(settings=settings)
    if mode == "real":
        return RealBitrix24Client(settings=settings)
    raise ValueError(f"Unsupported Bitrix mode: {settings.bitrix_mode}")


def _deterministic_id(method: str, payload: dict[str, Any]) -> int:
    canonical = json.dumps(
        {"method": method, "payload": payload}, sort_keys=True, ensure_ascii=False
    )
    digest = hashlib.sha1(canonical.encode("utf-8")).hexdigest()
    return int(digest[:10], 16)


def _extract_bitrix_id(body: dict[str, Any]) -> int:
    candidates = [
        body.get("result"),
        body.get("data"),
        body.get("result", {}).get("task", {}).get("id")
        if isinstance(body.get("result"), dict)
        else None,
        body.get("result", {}).get("item", {}).get("id")
        if isinstance(body.get("result"), dict)
        else None,
    ]
    for candidate in candidates:
        bitrix_id = _coerce_id(candidate)
        if bitrix_id is not None:
            return bitrix_id

    raise BitrixClientError("Bitrix24 response did not include an entity id")


def _coerce_id(value: Any) -> int | None:
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)
    if isinstance(value, dict):
        for key in ("id", "ID", "task", "item"):
            nested = value.get(key)
            nested_id = _coerce_id(nested)
            if nested_id is not None:
                return nested_id
    return None


def _build_portal_url(settings: Settings, entity_type: str, bitrix_id: int) -> str:
    base_url = settings.bitrix24_base_url.rstrip("/")
    if not base_url and settings.bitrix24_webhook_url:
        base_url = _derive_base_url(settings.bitrix24_webhook_url)
    if not base_url:
        return f"https://mock.bitrix24.local/{entity_type.replace('.', '/')}/{bitrix_id}/"

    path = entity_type.replace(".", "/")
    if entity_type == "task":
        path = "company/personal/user/1/tasks/task/view"
        return f"{base_url}/{path}/{bitrix_id}/"

    if entity_type == "crm.lead":
        path = "crm/lead/details"
    elif entity_type == "crm.item":
        path = "crm/item/details"

    return f"{base_url}/{path}/{bitrix_id}/"


def _derive_base_url(webhook_url: str) -> str:
    trimmed = webhook_url.rstrip("/")
    if "/rest/" in trimmed:
        return trimmed.split("/rest/")[0]
    return trimmed
