from __future__ import annotations

import os
import struct
from typing import Optional

from ps.constants import NULL_PTR, PRS_HEADER_SIZE, PRS_REC_SIZE
from ps.errors import PSUserError
from ps.models import PrsHeader, PrsRecord, read_exact


class PrsFile:
    def __init__(self) -> None:
        self.path: Optional[str] = None
        self.f = None
        self.header: Optional[PrsHeader] = None

    def close(self) -> None:
        if self.f:
            self.f.flush()
            self.f.close()
        self.f = None
        self.header = None
        self.path = None

    def create(self, path: str) -> None:
        self.close()
        self.path = path
        self.f = open(path, "w+b")
        self.header = PrsHeader(head_ptr=NULL_PTR, free_ptr=PRS_HEADER_SIZE)
        self.write_header()

    def open(self, path: str) -> None:
        if not os.path.exists(path):
            raise PSUserError(f"Файл не найден: {path}")
        self.close()
        self.path = path
        self.f = open(path, "r+b")
        self.f.seek(0)
        head_ptr, free_ptr = struct.unpack("<II", read_exact(self.f, 8))
        self.header = PrsHeader(head_ptr=head_ptr, free_ptr=free_ptr)

    def write_header(self) -> None:
        assert self.f and self.header
        h = self.header
        self.f.seek(0)
        self.f.write(struct.pack("<II", h.head_ptr, h.free_ptr))
        self.f.flush()

    def read_record(self, ptr: int) -> PrsRecord:
        assert self.f
        if ptr == NULL_PTR:
            raise PSUserError("Чтение по пустому указателю")
        self.f.seek(ptr)
        deleted = struct.unpack("<B", read_exact(self.f, 1))[0]
        prod_ptr = struct.unpack("<I", read_exact(self.f, 4))[0]
        qty = struct.unpack("<H", read_exact(self.f, 2))[0]
        next_ptr = struct.unpack("<I", read_exact(self.f, 4))[0]
        return PrsRecord(deleted=deleted, prod_ptr=prod_ptr, qty=qty, next_ptr=next_ptr)

    def write_record(self, ptr: int, rec: PrsRecord) -> None:
        assert self.f
        self.f.seek(ptr)
        self.f.write(struct.pack("<B", rec.deleted))
        self.f.write(struct.pack("<I", rec.prod_ptr))
        self.f.write(struct.pack("<H", rec.qty))
        self.f.write(struct.pack("<I", rec.next_ptr))
        self.f.flush()

    def append_record(self, rec: PrsRecord) -> int:
        assert self.header
        ptr = self.header.free_ptr
        self.write_record(ptr, rec)
        self.header.free_ptr = ptr + PRS_REC_SIZE
        self.write_header()
        return ptr