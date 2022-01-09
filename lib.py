import json
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Response:
    code: int
    payload: Optional[dict] = None

    @classmethod
    def from_json_str(cls, json_str: str) -> "Response":
        payload = json.loads(json_str)

        if not payload.get("code") or not payload.get("payload"):
            raise AttributeError()

        return cls(
            code=payload["code"],
            payload=payload["payload"],
        )

    def to_json_str(self) -> str:
        if not self.payload:
            return json.dumps({"code": self.code})

        return json.dumps({"code": self.code, "payload": self.payload})


@dataclass
class Command:
    name: str
    options: list = field(default_factory=list)

    @classmethod
    def from_json_str(cls, json_str: str) -> "Command":
        payload = json.loads(json_str)

        if not payload.get("name"):
            raise AttributeError()

        return cls(
            name=payload["name"],
            options=payload.get("options"),
        )

    def to_json_str(self) -> str:
        return json.dumps({"name": self.name, "options": self.options})


@dataclass
class FileResponse:
    content: str
    part_index: int
    total_parts: int

    @property
    def is_last_part(self) -> bool:
        return self.part_index + 1 == self.total_parts

    @classmethod
    def from_json_str(cls, json_str: str) -> "FileResponse":
        payload = json.loads(json_str)

        return cls(
            content=payload["content"],
            part_index=payload.get("part_index"),
            total_parts=payload.get("total_parts"),
        )

    def to_json_str(self) -> str:
        return json.dumps({"content": self.content, "part_index": self.part_index, "total_parts": self.total_parts})
