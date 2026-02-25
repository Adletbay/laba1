from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

from ps.constants import FS_ENCODING, NAME_ENCODING
from ps.errors import PSUserError


@dataclass
class PrdHeader:
    rec_len: int
    head_ptr: int
    free_ptr: int
    prs_name: str


@dataclass
class PrdRecord:
    deleted: int
    spec_ptr: int
    next_ptr: int
    data: bytes


@dataclass
class PrsHeader:
    head_ptr: int
    free_ptr: int


@dataclass
class PrsRecord:
    deleted: int
    prod_ptr: int
    qty: int
    next_ptr: int


def read_exact(f, n: int) -> bytes:
    b = f.read(n)
    if len(b) != n:
        raise PSUserError("Повреждён файл или неожиданное окончание файла")
    return b


def pad_bytes(s: str, size: int) -> bytes:
    b = s.encode(NAME_ENCODING, errors="replace")
    if len(b) > size:
        raise PSUserError(f"Имя слишком длинное для заданного максДлинаИмени={size}")
    return b + b" " * (size - len(b))


def norm_base_name(name: str) -> str:
    name = name.strip()
    if not name:
        raise PSUserError("Имя файла пустое")
    if name.lower().endswith(".prd"):
        name = name[:-4]
    return name


def component_key(name: str) -> str:
    return name.strip().lower()


def type_to_code(t: str) -> str:
    tt = t.strip().lower()
    if tt in ("изделие", "изделия"):
        return "P"
    if tt in ("узел", "узла"):
        return "U"
    if tt in ("деталь", "детали"):
        return "D"
    raise PSUserError("Тип должен быть: Изделие | Узел | Деталь")


def code_to_type(code: str) -> str:
    return {"P": "Изделие", "U": "Узел", "D": "Деталь"}.get(code, "?")


def pack_name_field(name: str, size: int) -> bytes:
    return pad_bytes(name, size)


def unpack_name_field(data: bytes) -> str:
    return data.decode(NAME_ENCODING, errors="replace").rstrip(" ")


def pack_prs_name(prs_name: str, size: int = 16) -> bytes:
    b = prs_name.encode(FS_ENCODING, errors="replace")[:size]
    return b + b"\x00" * (size - len(b))


def unpack_prs_name(field16: bytes) -> str:
    return field16.split(b"\x00", 1)[0].decode(FS_ENCODING, errors="replace").strip()