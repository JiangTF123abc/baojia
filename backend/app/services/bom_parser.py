from decimal import Decimal, InvalidOperation

import openpyxl

from ..extensions import db
from ..models.base_component import BaseComponent
from ..models.material import Material
from ..models.structure_component import StructureComponent

# 列名映射
_COLUMN_ALIASES = {
    "model_number": {"型号", "model_number", "model number", "物料编号", "料号"},
    "name": {"名称", "name", "物料名称", "元件名称"},
    "quantity": {"数量", "quantity", "qty", "用量"},
    "specification": {"规格", "specification", "spec", "规格型号", "描述"},
}


def _detect_columns(header_row) -> dict:
    mapping = {}
    for col_idx, cell in enumerate(header_row):
        if cell.value is None:
            continue
        cell_lower = str(cell.value).strip().lower()
        for field, aliases in _COLUMN_ALIASES.items():
            if cell_lower in aliases and field not in mapping:
                mapping[field] = col_idx
    return mapping


def _match_material(model_number: str, name: str):
    if model_number:
        mat = Material.query.filter_by(model_number=model_number, is_active=True).first()
        if mat:
            return mat
    if name:
        mat = Material.query.filter(
            Material.name.ilike(f"%{name}%"),
            Material.is_active == True,
        ).first()
        if mat:
            return mat
    return None


def _safe_decimal(value, default="0.0000") -> str:
    if value is None:
        return default
    try:
        return str(Decimal(str(value)).quantize(Decimal("0.0001")))
    except InvalidOperation:
        return default


class BomParser:

    def parse_excel(self, file_path: str) -> dict:
        wb = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
        ws = wb.active

        rows_iter = ws.iter_rows()
        col_mapping = {}
        for row in rows_iter:
            if any(c.value is not None for c in row):
                col_mapping = _detect_columns(row)
                break

        if not col_mapping:
            wb.close()
            return {"rows": [], "total": 0, "matched_count": 0, "unmatched_count": 0}

        result_rows = []
        row_index = 1

        for row in rows_iter:
            if all(c.value is None for c in row):
                continue

            def get_val(field):
                idx = col_mapping.get(field)
                if idx is None:
                    return None
                val = row[idx].value if idx < len(row) else None
                return str(val).strip() if val is not None else None

            model_number = get_val("model_number") or ""
            name = get_val("name") or ""
            quantity = _safe_decimal(get_val("quantity"), "1.0000")
            specification = get_val("specification") or ""

            matched = _match_material(model_number, name)
            if matched:
                status = "matched"
                unit_price = str(matched.unit_price) if matched.unit_price is not None else None
                matched_dict = matched.to_dict()
            else:
                status = "unmatched"
                unit_price = None
                matched_dict = None

            result_rows.append({
                "row_index": row_index,
                "model_number": model_number,
                "name": name,
                "quantity": quantity,
                "specification": specification,
                "matched_material": matched_dict,
                "unit_price": unit_price,
                "status": status,
            })
            row_index += 1

        wb.close()
        matched_count = sum(1 for r in result_rows if r["status"] == "matched")
        return {
            "rows": result_rows,
            "total": len(result_rows),
            "matched_count": matched_count,
            "unmatched_count": len(result_rows) - matched_count,
        }

    def import_bom(self, rows: list, target_sc_id: int) -> list:
        sc = StructureComponent.query.get(target_sc_id)
        if sc is None:
            raise LookupError(f"结构组件 {target_sc_id} 不存在")

        existing_max = db.session.query(
            db.func.max(BaseComponent.sort_order)
        ).filter_by(structure_component_id=target_sc_id).scalar() or 0

        created = []
        try:
            for idx, row in enumerate(rows):
                matched = row.get("matched_material")
                material_id = matched["id"] if matched else None
                if material_id:
                    mat = Material.query.get(material_id)
                    unit_price = mat.unit_price if mat and mat.unit_price is not None else Decimal("0")
                else:
                    unit_price = Decimal(_safe_decimal(row.get("unit_price"), "0.0000"))

                bc = BaseComponent(
                    structure_component_id=target_sc_id,
                    material_id=material_id,
                    model_number=row.get("model_number") or "",
                    name=row.get("name") or "",
                    specification=row.get("specification") or "",
                    quantity=Decimal(_safe_decimal(row.get("quantity"), "1.0000")),
                    unit_price=unit_price,
                    discount_rate=Decimal("1.0000"),
                    sort_order=existing_max + idx + 1,
                )
                db.session.add(bc)
                created.append(bc)

            db.session.commit()
            return created
        except Exception:
            db.session.rollback()
            raise


bom_parser = BomParser()
