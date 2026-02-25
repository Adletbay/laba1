from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Command:
    name: str
    args_raw: str
    raw: str


def parse_command(line: str) -> Command:
    s = line.strip()
    if not s:
        return Command("", "", line)

    name_chars = []
    i = 0
    while i < len(s) and not s[i].isspace() and s[i] != "(":
        name_chars.append(s[i])
        i += 1
    name = "".join(name_chars).lower()
    rest = s[i:].strip()

    if rest.startswith("("):
        j = rest.rfind(")")
        if j == -1:
            raise ValueError("Нет закрывающей скобки ')'")
        args = rest[1:j].strip()
        return Command(name, args, line)

    return Command(name, rest, line)


def split_csv(args_raw: str) -> list[str]:
    if args_raw.strip() == "":
        return []
    return [a.strip() for a in args_raw.split(",")]


def parse_parent_child(args_raw: str) -> tuple[str, str, int]:
    parts = split_csv(args_raw)
    if not parts:
        raise ValueError("Нужно указать parent/child")
    if "/" not in parts[0]:
        raise ValueError("Ожидается формат имяКомпонента/имяКомплектующего")
    parent, child = [x.strip() for x in parts[0].split("/", 1)]
    qty = 1
    if len(parts) >= 2:
        qty = int(parts[1])
    return parent, child, qty