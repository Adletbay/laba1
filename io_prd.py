from __future__ import annotations

import os
import struct
from typing import Optional

from ps.constants import SIGNATURE, NULL_PTR, PRD_HEADER_SIZE
from ps.errors import PSUserError
from ps.models import (
    PrdHeader,
    PrdRecord,
    read_exact,
    pack_prs_name,
    unpack_prs_name,
)


class PrdFile:
    def __init__(self) -> None:
        self.path: Optional[str] = None
        self.f = None
        self.header: Optional[PrdHeader] = None

    def close(self) -> None:
        if self.f:
            self.f.flush()
            self.f.close()
        self.f = None
        self.header = None
        self.path = None

    def create(self, path: str, rec_len: int, prs_name: str) -> None:
        self.close()
        self.path = path
        self.f = open(path, "w+b")

        if rec_len <= 0:
            raise PSUserError("максДлинаИмени должна быть > 0")

        self.header = PrdHeader(
            rec_len=rec_len,
            head_ptr=NULL_PTR,
            free_ptr=PRD_HEADER_SIZE,
            prs_name=prs_name,
        )
        self.write_header()

    def open(self, path: str) -> None:
        if not os.path.exists(path):
            raise PSUserError(f"Файл не найден: {path}")
        self.close()
        self.path = path
        self.f = open(path, "r+b")

        self.f.seek(0)
        sig = read_exact(self.f, 2)
        if sig != SIGNATURE:
            raise PSUserError("Сигнатура .prd не совпадает (ожидается 'PS')")

        rec_len, head_ptr, free_ptr = struct.unpack("<HII", read_exact(self.f, 2 + 4 + 4))
        prs_name = unpack_prs_name(read_exact(self.f, 16))

        if not prs_name:
            raise PSUserError("В заголовке .prd отсутствует имя файла спецификаций")

        self.header = PrdHeader(rec_len=rec_len, head_ptr=head_ptr, free_ptr=free_ptr, prs_name=prs_name)

    def write_header(self) -> None:
        assert self.f and self.header
        h = self.header
        self.f.seek(0)
        self.f.write(SIGNATURE)
        self.f.write(struct.pack("<HII", h.rec_len, h.head_ptr, h.free_ptr))
        self.f.write(pack_prs_name(h.prs_name, 16))
        self.f.flush()

    def rec_size(self) -> int:
        assert self.header
        return 1 + 4 + 4 + self.header.rec_len

    def read_record(self, ptr: int) -> PrdRecord:
        assert self.f and self.header
        if ptr == NULL_PTR:
            raise PSUserError("Чтение по пустому указателю")
        self.f.seek(ptr)
        deleted = struct.unpack("<B", read_exact(self.f, 1))[0]
        spec_ptr, next_ptr = struct.unpack("<II", read_exact(self.f, 8))
        data = read_exact(self.f, self.header.rec_len)
        return PrdRecord(deleted=deleted, spec_ptr=spec_ptr, next_ptr=next_ptr, data=data)

    def write_record(self, ptr: int, rec: PrdRecord) -> None:
        assert self.f and self.header
        if len(rec.data) != self.header.rec_len:
            raise PSUserError("Внутренняя ошибка: неверная длина data поля prd")
        self.f.seek(ptr)
        self.f.write(struct.pack("<BII", rec.deleted, rec.spec_ptr, rec.next_ptr))
        self.f.write(rec.data)
        self.f.flush()

    def append_record(self, rec: PrdRecord) -> int:
        assert self.header
        ptr = self.header.free_ptr
        self.write_record(ptr, rec)
        self.header.free_ptr = ptr + self.rec_size()
        self.write_header()
        return ptr