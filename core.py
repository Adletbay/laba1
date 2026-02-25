from __future__ import annotations

import os
from typing import Iterable, Optional

from ps.constants import NULL_PTR, PRS_HEADER_SIZE, PRS_REC_SIZE
from ps.errors import PSUserError
from ps.io_prd import PrdFile
from ps.io_prs import PrsFile
from ps.models import (
    PrdRecord,
    PrsRecord,
    code_to_type,
    component_key,
    norm_base_name,
    pack_name_field,
    type_to_code,
    unpack_name_field,
)


class PSCore:
    def __init__(self) -> None:
        self.prd = PrdFile()
        self.prs = PrsFile()

        self._type_by_ptr: dict[int, str] = {}

    def close(self) -> None:
        self.prd.close()
        self.prs.close()
        self._type_by_ptr.clear()

    def is_open(self) -> bool:
        return (
            self.prd.f is not None
            and self.prs.f is not None
            and self.prd.header is not None
            and self.prs.header is not None
        )

    # Create/Open

    def create(self, base_name: str, max_len: int, prs_name_opt: Optional[str]) -> tuple[str, str]:
        base = norm_base_name(base_name)
        prd_path = base + ".prd"

        prs_name = (prs_name_opt.strip() if prs_name_opt else (base + ".prs"))
        if not prs_name.lower().endswith(".prs"):
            prs_name += ".prs"
        prs_path = prs_name

        try:
            self.prs.create(prs_path)
            self.prd.create(prd_path, rec_len=max_len, prs_name=prs_name)
        except OSError as e:
            raise PSUserError(f"Ошибка файловой операции: {e}")

        self._type_by_ptr.clear()
        return prd_path, prs_path

    def open(self, base_name: str) -> tuple[str, str]:
        base = norm_base_name(base_name)
        prd_path = base + ".prd"

        try:
            self.prd.open(prd_path)
            assert self.prd.header
            prs_path = self.prd.header.prs_name
            self.prs.open(prs_path)
        except OSError as e:
            raise PSUserError(f"Ошибка файловой операции: {e}")

        self._rebuild_types_from_structure()

        return prd_path, prs_path

    # Итерация/поиск по PRD логическому списку

    def iter_products(self, include_deleted: bool) -> Iterable[tuple[int, PrdRecord, str]]:
        assert self.prd.header
        ptr = self.prd.header.head_ptr
        while ptr != NULL_PTR:
            rec = self.prd.read_record(ptr)
            name = unpack_name_field(rec.data)
            if include_deleted or rec.deleted == 0:
                yield ptr, rec, name
            ptr = rec.next_ptr

    def find_product(self, name: str, include_deleted: bool) -> Optional[tuple[int, PrdRecord, str]]:
        k = component_key(name)
        for ptr, rec, nm in self.iter_products(include_deleted=include_deleted):
            if component_key(nm) == k:
                return ptr, rec, nm
        return None

    def _name_exists_any(self, name: str) -> bool:
        return self.find_product(name, include_deleted=True) is not None

    # Добавление компонента

    def add_component(self, name: str, type_str: str) -> str:
        if not self.is_open():
            raise PSUserError("Сначала выполните Create или Open")

        assert self.prd.header
        name = name.strip()
        if not name:
            raise PSUserError("Имя компонента пустое")

        if self._name_exists_any(name):
            raise PSUserError("Дублирование имен компонентов")

        code = type_to_code(type_str)

        rec = PrdRecord(
            deleted=0,
            spec_ptr=NULL_PTR,   # пустой указатель = 1
            next_ptr=NULL_PTR,
            data=pack_name_field(name, self.prd.header.rec_len),
        )
        new_ptr = self.prd.append_record(rec)
        self._type_by_ptr[new_ptr] = code

        self._insert_sorted(new_ptr)
        return f"Добавлен компонент: {name} ({code_to_type(code)})"

    def _insert_sorted(self, new_ptr: int) -> None:
        assert self.prd.header
        new_rec = self.prd.read_record(new_ptr)
        new_name = unpack_name_field(new_rec.data)

        if self.prd.header.head_ptr == NULL_PTR:
            self.prd.header.head_ptr = new_ptr
            self.prd.write_header()
            return

        def lt(a: str, b: str) -> bool:
            return a.lower() < b.lower()

        head_ptr = self.prd.header.head_ptr
        head_rec = self.prd.read_record(head_ptr)
        head_name = unpack_name_field(head_rec.data)

        if lt(new_name, head_name):
            new_rec.next_ptr = head_ptr
            self.prd.write_record(new_ptr, new_rec)
            self.prd.header.head_ptr = new_ptr
            self.prd.write_header()
            return

        prev_ptr = head_ptr
        prev_rec = head_rec
        cur_ptr = head_rec.next_ptr

        while cur_ptr != NULL_PTR:
            cur_rec = self.prd.read_record(cur_ptr)
            cur_name = unpack_name_field(cur_rec.data)
            if lt(new_name, cur_name):
                break
            prev_ptr = cur_ptr
            prev_rec = cur_rec
            cur_ptr = cur_rec.next_ptr

        new_rec.next_ptr = cur_ptr
        self.prd.write_record(new_ptr, new_rec)
        prev_rec.next_ptr = new_ptr
        self.prd.write_record(prev_ptr, prev_rec)

    # Добавление в спецификацию

    def add_spec_item(self, parent: str, child: str, qty: int) -> str:
        if not self.is_open():
            raise PSUserError("Сначала выполните Create или Open")
        if qty <= 0 or qty > 65535:
            raise PSUserError("Кратность должна быть в диапазоне 1..65535")

        p = self.find_product(parent, include_deleted=False)
        if not p:
            raise PSUserError("Отсутствие в списке заданного компонента (родитель)")
        p_ptr, p_rec, p_name = p

        if self._type_by_ptr.get(p_ptr) == "D":
            raise PSUserError("Несоответствие команды с типом компонента: у детали нет спецификации")

        c = self.find_product(child, include_deleted=False)
        if not c:
            raise PSUserError("Отсутствие в списке заданного компонента (комплектующее)")
        c_ptr, _, c_name = c

        if self._spec_has_child(p_rec.spec_ptr, c_ptr):
            raise PSUserError("Комплектующее уже есть в спецификации")

        new_spec_ptr = self.prs.append_record(PrsRecord(deleted=0, prod_ptr=c_ptr, qty=qty, next_ptr=NULL_PTR))

        if p_rec.spec_ptr == NULL_PTR:
            p_rec.spec_ptr = new_spec_ptr
            self.prd.write_record(p_ptr, p_rec)

            if self._type_by_ptr.get(p_ptr) == "D":
                self._type_by_ptr[p_ptr] = "U"
            return f"Добавлено в спецификацию: {p_name} <- {c_name} x{qty}"

        cur = p_rec.spec_ptr
        while True:
            r = self.prs.read_record(cur)
            if r.next_ptr == NULL_PTR:
                r.next_ptr = new_spec_ptr
                self.prs.write_record(cur, r)
                break
            cur = r.next_ptr

        if self._type_by_ptr.get(p_ptr) == "D":
            self._type_by_ptr[p_ptr] = "U"
        return f"Добавлено в спецификацию: {p_name} <- {c_name} x{qty}"

    def _spec_has_child(self, spec_head: int, child_ptr: int) -> bool:
        cur = spec_head
        while cur != NULL_PTR:
            r = self.prs.read_record(cur)
            if r.deleted == 0 and r.prod_ptr == child_ptr:
                return True
            cur = r.next_ptr
        return False

    # Delete

    def delete_component(self, name: str) -> str:
        p = self.find_product(name, include_deleted=False)
        if not p:
            raise PSUserError("Отсутствие в списке заданного компонента")
        ptr, rec, nm = p

        if self._has_any_active_reference(ptr):
            raise PSUserError("Наличие ссылок на компонент при попытке удалить его из списка")

        rec.deleted = 1
        self.prd.write_record(ptr, rec)

        if self._type_by_ptr.get(ptr) != "D" and rec.spec_ptr != NULL_PTR:
            self._mark_spec_deleted(rec.spec_ptr)

        return f"Компонент помечен на удаление: {nm}"

    def delete_spec_item(self, parent: str, child: str) -> str:
        p = self.find_product(parent, include_deleted=False)
        if not p:
            raise PSUserError("Отсутствие в списке заданного компонента (родитель)")
        p_ptr, p_rec, p_name = p

        if self._type_by_ptr.get(p_ptr) == "D":
            raise PSUserError("Несоответствие команды с типом компонента: у детали нет спецификации")

        c = self.find_product(child, include_deleted=False)
        if not c:
            raise PSUserError("Отсутствие в списке заданного компонента (комплектующее)")
        c_ptr, _, c_name = c

        cur = p_rec.spec_ptr
        while cur != NULL_PTR:
            r = self.prs.read_record(cur)
            if r.deleted == 0 and r.prod_ptr == c_ptr:
                r.deleted = 1
                self.prs.write_record(cur, r)
                return f"Комплектующее помечено на удаление: {p_name}/{c_name}"
            cur = r.next_ptr

        raise PSUserError("Комплектующее отсутствует в спецификации")

    def _has_any_active_reference(self, prod_ptr: int) -> bool:
        assert self.prs.header
        end = self.prs.header.free_ptr
        ptr = PRS_HEADER_SIZE
        while ptr + PRS_REC_SIZE <= end:
            r = self.prs.read_record(ptr)
            if r.deleted == 0 and r.prod_ptr == prod_ptr:
                return True
            ptr += PRS_REC_SIZE
        return False

    def _mark_spec_deleted(self, spec_head: int) -> None:
        cur = spec_head
        while cur != NULL_PTR:
            r = self.prs.read_record(cur)
            r.deleted = 1
            self.prs.write_record(cur, r)
            cur = r.next_ptr

    # Restore

    def restore(self, name_or_star: str) -> str:
        if name_or_star.strip() == "*":
            restored_prd = 0
            for ptr, rec, _ in self.iter_products(include_deleted=True):
                if rec.deleted != 0:
                    rec.deleted = 0
                    self.prd.write_record(ptr, rec)
                    restored_prd += 1

            restored_prs = self._restore_all_prs()
            self._rebuild_sorted_links(active_only=True)
            self._rebuild_types_from_structure()
            return f"Restore(*): восстановлено компонентов: {restored_prd}, записей спецификаций: {restored_prs}"

        p = self.find_product(name_or_star, include_deleted=True)
        if not p:
            raise PSUserError("Отсутствие в списке заданного компонента")
        ptr, rec, nm = p

        if rec.deleted != 0:
            rec.deleted = 0
            self.prd.write_record(ptr, rec)

        # восстановить записи спецификации этого компонента
        if self._type_by_ptr.get(ptr) != "D" and rec.spec_ptr != NULL_PTR:
            self._restore_spec_list(rec.spec_ptr)

        self._rebuild_sorted_links(active_only=True)
        self._rebuild_types_from_structure()
        return f"Restore({nm}): выполнено"

    def _restore_all_prs(self) -> int:
        assert self.prs.header
        end = self.prs.header.free_ptr
        ptr = PRS_HEADER_SIZE
        cnt = 0
        while ptr + PRS_REC_SIZE <= end:
            r = self.prs.read_record(ptr)
            if r.deleted != 0:
                r.deleted = 0
                self.prs.write_record(ptr, r)
                cnt += 1
            ptr += PRS_REC_SIZE
        return cnt

    def _restore_spec_list(self, head: int) -> int:
        cur = head
        cnt = 0
        while cur != NULL_PTR:
            r = self.prs.read_record(cur)
            if r.deleted != 0:
                r.deleted = 0
                self.prs.write_record(cur, r)
                cnt += 1
            cur = r.next_ptr
        return cnt

    def _rebuild_sorted_links(self, active_only: bool) -> None:
        assert self.prd.header
        items = []
        for ptr, rec, name in self.iter_products(include_deleted=not active_only):
            if active_only and rec.deleted != 0:
                continue
            items.append((name.lower(), ptr))
        items.sort(key=lambda x: x[0])

        if not items:
            self.prd.header.head_ptr = NULL_PTR
            self.prd.write_header()
            return

        self.prd.header.head_ptr = items[0][1]
        self.prd.write_header()

        for i, (_, ptr) in enumerate(items):
            rec = self.prd.read_record(ptr)
            rec.next_ptr = items[i + 1][1] if i + 1 < len(items) else NULL_PTR
            self.prd.write_record(ptr, rec)

    # Print

    def print_all(self) -> str:
        lines = ["Наименование\tТип"]
        for ptr, rec, name in self.iter_products(include_deleted=False):
            code = self._type_by_ptr.get(ptr, "?")
            lines.append(f"{name}\t{code_to_type(code)}")
        return "\n".join(lines)

    def print_tree(self, name: str) -> str:
        p = self.find_product(name, include_deleted=False)
        if not p:
            raise PSUserError("Отсутствие в списке заданного компонента")
        ptr, rec, nm = p

        if self._type_by_ptr.get(ptr) == "D":
            raise PSUserError("Несоответствие команды с типом компонента: деталь не имеет спецификации")

        lines = [nm]
        visited: set[int] = {ptr}
        self._print_spec_recursive(rec.spec_ptr, prefix="", lines=lines, visited=visited)
        return "\n".join(lines)

    def _print_spec_recursive(self, head: int, prefix: str, lines: list[str], visited: set[int]) -> None:
        cur = head
        while cur != NULL_PTR:
            r = self.prs.read_record(cur)
            if r.deleted == 0:
                child_ptr = r.prod_ptr
                child_rec = self.prd.read_record(child_ptr)
                child_name = unpack_name_field(child_rec.data)
                lines.append(f"{prefix}└─ {child_name} x{r.qty}")

                if self._type_by_ptr.get(child_ptr) != "D":
                    if child_ptr in visited:
                        lines.append(f"{prefix}   (цикл обнаружен)")
                    else:
                        visited.add(child_ptr)
                        self._print_spec_recursive(child_rec.spec_ptr, prefix + "   ", lines, visited)
            cur = r.next_ptr

    # Truncate

    def truncate(self) -> str:
        if not self.is_open():
            raise PSUserError("Сначала выполните Create или Open")
        assert self.prd.header and self.prs.header and self.prd.path and self.prs.path

        old_prd_path = self.prd.path
        old_prs_path = self.prs.path
        rec_len = self.prd.header.rec_len
        prs_name = self.prd.header.prs_name

        active_products: list[tuple[int, PrdRecord, str]] = []
        for old_ptr, rec, name in self.iter_products(include_deleted=True):
            if rec.deleted == 0:
                active_products.append((old_ptr, rec, name))

        # алфавитный порядок
        active_products.sort(key=lambda x: x[2].lower())

        active_ptrs_set = {old_ptr for (old_ptr, _, _) in active_products}

        def read_spec_list(head_ptr: int) -> list[tuple[int, int]]:
            """Возвращает [(child_old_ptr, qty)] только для активных (не deleted) записей."""
            out: list[tuple[int, int]] = []
            cur = head_ptr
            while cur != NULL_PTR:
                r = self.prs.read_record(cur)
                if r.deleted == 0:
                    out.append((r.prod_ptr, r.qty))
                cur = r.next_ptr
            return out

        specs_by_parent_old: dict[int, list[tuple[int, int]]] = {}
        for old_ptr, rec, _ in active_products:
            if rec.spec_ptr != NULL_PTR:
                specs_by_parent_old[old_ptr] = read_spec_list(rec.spec_ptr)
            else:
                specs_by_parent_old[old_ptr] = []

        self.close()

        prd_tmp = old_prd_path + ".tmp"
        prs_tmp = old_prs_path + ".tmp"

        from ps.io_prd import PrdFile
        from ps.io_prs import PrsFile
        from ps.models import PrdRecord, PrsRecord

        prd_new = PrdFile()
        prs_new = PrsFile()

        prs_new.create(prs_tmp)
        prd_new.create(prd_tmp, rec_len=rec_len, prs_name=prs_name)


        ptr_map: dict[int, int] = {}
        new_ptrs_in_order: list[int] = []

        for old_ptr, old_rec, _name in active_products:
            new_rec = PrdRecord(
                deleted=0,
                spec_ptr=NULL_PTR,
                next_ptr=NULL_PTR,
                data=old_rec.data,
            )
            new_ptr = prd_new.append_record(new_rec)
            ptr_map[old_ptr] = new_ptr
            new_ptrs_in_order.append(new_ptr)

        # next_ptr по алфавитному порядку
        for i, cur_ptr in enumerate(new_ptrs_in_order):
            rec = prd_new.read_record(cur_ptr)
            rec.next_ptr = new_ptrs_in_order[i + 1] if i + 1 < len(new_ptrs_in_order) else NULL_PTR
            prd_new.write_record(cur_ptr, rec)

        # head_ptr
        assert prd_new.header
        prd_new.header.head_ptr = new_ptrs_in_order[0] if new_ptrs_in_order else NULL_PTR
        prd_new.write_header()

        for old_parent_ptr, _old_rec, _name in active_products:
            new_parent_ptr = ptr_map[old_parent_ptr]
            parent_new_rec = prd_new.read_record(new_parent_ptr)

            items = specs_by_parent_old.get(old_parent_ptr, [])
            items2: list[tuple[int, int]] = []
            for child_old_ptr, qty in items:
                if child_old_ptr in ptr_map:
                    items2.append((ptr_map[child_old_ptr], qty))

            if not items2:
                parent_new_rec.spec_ptr = NULL_PTR
                prd_new.write_record(new_parent_ptr, parent_new_rec)
                continue

            first_spec_ptr: int | None = None
            prev_spec_ptr: int | None = None

            for child_new_ptr, qty in items2:
                s_ptr = prs_new.append_record(
                    PrsRecord(deleted=0, prod_ptr=child_new_ptr, qty=qty, next_ptr=NULL_PTR)
                )
                if first_spec_ptr is None:
                    first_spec_ptr = s_ptr
                if prev_spec_ptr is not None:
                    prev_rec = prs_new.read_record(prev_spec_ptr)
                    prev_rec.next_ptr = s_ptr
                    prs_new.write_record(prev_spec_ptr, prev_rec)
                prev_spec_ptr = s_ptr

            parent_new_rec.spec_ptr = first_spec_ptr if first_spec_ptr is not None else NULL_PTR
            prd_new.write_record(new_parent_ptr, parent_new_rec)

        prd_new.close()
        prs_new.close()

        os.replace(prd_tmp, old_prd_path)
        os.replace(prs_tmp, old_prs_path)

        base = norm_base_name(old_prd_path)
        self.open(base)

        return "Truncate: выполнено (физическое удаление + уплотнение)"


    def _rebuild_types_from_structure(self) -> None:
        if not self.is_open():
            return
        assert self.prs.header

        referenced: set[int] = set()
        end = self.prs.header.free_ptr
        p = PRS_HEADER_SIZE
        while p + PRS_REC_SIZE <= end:
            r = self.prs.read_record(p)
            if r.deleted == 0:
                referenced.add(r.prod_ptr)
            p += PRS_REC_SIZE

        has_active_spec: set[int] = set()
        for ptr, rec, _ in self.iter_products(include_deleted=True):
            if rec.spec_ptr == NULL_PTR:
                continue
            cur = rec.spec_ptr
            while cur != NULL_PTR:
                rr = self.prs.read_record(cur)
                if rr.deleted == 0:
                    has_active_spec.add(ptr)
                    break
                cur = rr.next_ptr

        self._type_by_ptr.clear()
        for ptr, rec, _ in self.iter_products(include_deleted=True):
            if ptr in has_active_spec:
                self._type_by_ptr[ptr] = "U" if ptr in referenced else "P"
            else:
                self._type_by_ptr[ptr] = "D"