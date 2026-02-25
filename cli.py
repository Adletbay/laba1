from __future__ import annotations

import os

from ps.core import PSCore
from ps.errors import PSUserError
from ps.help_text import HELP_TEXT
from ps.parser import parse_command, split_csv, parse_parent_child
from ps.models import norm_base_name
from ps.constants import SIGNATURE


class PSApp:

    def is_open(self) -> bool:
        """Проверка, открыты ли файлы"""
        return self.core.is_open()


    def __init__(self) -> None:
        self.core = PSCore()
        # (base_name, max_len, prs_name)
        self._pending_create: tuple[str, int, str | None] | None = None

    def close(self) -> None:
        self.core.close()

    def execute(self, line: str) -> str:
        cmd = parse_command(line)

        # подтверждение Create
        if self._pending_create and cmd.name in ("y", "yes", "n", "no"):
            base_name, max_len, prs_name = self._pending_create
            self._pending_create = None
            if cmd.name in ("n", "no"):
                return "Create отменён."
            prd, prs = self.core.create(base_name, max_len, prs_name)
            return f"Создано: {prd}, {prs}"

        if cmd.name == "exit":
            self.close()
            raise SystemExit

        if cmd.name == "help":
            target = cmd.args_raw.strip()
            if not target:
                return HELP_TEXT
            with open(target, "w", encoding="utf-8") as f:
                f.write(HELP_TEXT)
            return f"Help: записано в файл {target}"

        if cmd.name == "create":

            s = cmd.args_raw.strip()
            if not s:
                raise PSUserError("Create: ожидается имяФайла(максДлина[, prs])")

            lpar = s.find("(")
            rpar = s.rfind(")")
            if lpar == -1 or rpar == -1 or rpar < lpar:
                raise PSUserError("Create: ожидается формат имяФайла(максДлина[, prs])")

            base_name = s[:lpar].strip()
            inner = s[lpar + 1 : rpar].strip()

            parts = split_csv(inner)
            if len(parts) < 1 or not parts[0]:
                raise PSUserError("Create: нужно указать максДлинаИмени")
            try:
                max_len = int(parts[0])
            except ValueError:
                raise PSUserError("Create: максДлинаИмени должно быть целым числом")

            prs_name = parts[1] if len(parts) >= 2 else None

            base = norm_base_name(base_name)
            prd_path = base + ".prd"

            prs_path = (prs_name.strip() if prs_name else (base + ".prs"))
            if not prs_path.lower().endswith(".prs"):
                prs_path += ".prs"

            # если .prd существует - проверить сигнатуру
            if os.path.exists(prd_path):
                try:
                    with open(prd_path, "rb") as f:
                        sig = f.read(2)
                except OSError as e:
                    raise PSUserError(f"Ошибка файловой операции: {e}")

                if sig != SIGNATURE:
                    raise PSUserError("Create: файл существует, но сигнатура отсутствует/не соответствует заданию")

                self._pending_create = (base_name, max_len, prs_name)
                return "Файлы уже существуют и сигнатура верная. Перезаписать? (Y/N)"

            # если только prs существует — тоже подтверждение
            if os.path.exists(prs_path):
                self._pending_create = (base_name, max_len, prs_name)
                return "Файл спецификаций уже существует. Перезаписать? (Y/N)"

            prd, prs = self.core.create(base_name, max_len, prs_name)
            return f"Создано: {prd}, {prs}"

        if cmd.name == "open":
            base = cmd.args_raw.strip()
            if not base:
                raise PSUserError("Open: нужно имя файла")
            prd, prs = self.core.open(base)
            return f"Открыто: {prd}, {prs}"

        if cmd.name == "input":
            if "/" in cmd.args_raw:
                parent, child, qty = parse_parent_child(cmd.args_raw)
                return self.core.add_spec_item(parent, child, qty)
            parts = split_csv(cmd.args_raw)
            if len(parts) != 2:
                raise PSUserError("Input(имя, тип): нужно 2 аргумента")
            return self.core.add_component(parts[0], parts[1])

        if cmd.name == "delete":
            if "/" in cmd.args_raw:
                parent, child = [x.strip() for x in cmd.args_raw.split("/", 1)]
                return self.core.delete_spec_item(parent, child)
            name = cmd.args_raw.strip()
            if not name:
                raise PSUserError("Delete: нужно имя компонента")
            return self.core.delete_component(name)

        if cmd.name == "restore":
            arg = cmd.args_raw.strip()
            if not arg:
                raise PSUserError("Restore: нужно имя или *")
            return self.core.restore(arg)

        if cmd.name == "truncate":
            return self.core.truncate()

        if cmd.name == "print":
            arg = cmd.args_raw.strip()
            if not arg:
                raise PSUserError("Print: нужно имя или *")
            if arg == "*":
                return self.core.print_all()
            return self.core.print_tree(arg)

        raise PSUserError("Неизвестная команда. Введите Help.")