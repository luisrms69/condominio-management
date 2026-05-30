import frappe


def execute():
	"""Migrar datos de tabProperty Copropiedad a tabProperty Declared Owner.

	Motivo: renombrado de DocType y campo para eliminar la terminología "copropiedad"
	de la UI. Cada fila representa un período de titularidad declarada.

	Idempotente: puede correr múltiples veces sin duplicar ni perder datos.
	"""
	src = "tabProperty Copropiedad"
	dst = "tabProperty Declared Owner"
	reg = "tabProperty Registry"
	reg_doctype = "Property Registry"

	# 1. Migrar datos de columna renombrada en Property Registry
	# Después de bench migrate, Frappe habrá creado current_owners_total_percentage (vacía).
	# Copiamos los valores desde total_copropiedades_percentage.
	if frappe.db.has_column(reg_doctype, "total_copropiedades_percentage") and frappe.db.has_column(
		reg_doctype, "current_owners_total_percentage"
	):
		frappe.db.sql(f"""
			UPDATE `{reg}`
			SET `current_owners_total_percentage` = `total_copropiedades_percentage`
			WHERE (`current_owners_total_percentage` IS NULL OR `current_owners_total_percentage` = 0)
			  AND `total_copropiedades_percentage` IS NOT NULL
			  AND `total_copropiedades_percentage` != 0
		""")

	# 2. Migrar filas de child table
	if not frappe.db.table_exists(src):
		return

	if not frappe.db.table_exists(dst):
		frappe.log_error(
			f"Tabla {dst} no existe — ejecutar bench migrate antes de este patch",
			"migrate_property_copropiedad_to_declared_owner",
		)
		return

	src_count = frappe.db.sql(f"SELECT COUNT(*) FROM `{src}`")[0][0]
	if src_count == 0:
		return

	dst_count = frappe.db.sql(f"SELECT COUNT(*) FROM `{dst}`")[0][0]
	if dst_count >= src_count:
		# Idempotente: ya migrado previamente
		return

	# Copiar filas mapeando:
	#   copropiedad_percentage → ownership_percentage
	#   parentfield 'copropiedades_table' → 'declared_owners'
	frappe.db.sql(f"""
		INSERT INTO `{dst}` (
			name, parent, parentfield, parenttype, idx,
			owner_name, owner_id, owner_type, ownership_percentage,
			is_current, start_date, end_date,
			acquisition_date, acquisition_type,
			notes, source_reference, is_active,
			docstatus, `owner`, creation, modified, modified_by
		)
		SELECT
			name, parent,
			'declared_owners',
			parenttype, idx,
			owner_name, owner_id, owner_type, copropiedad_percentage,
			is_current, start_date, end_date,
			acquisition_date, acquisition_type,
			notes, source_reference, is_active,
			docstatus, `owner`, creation, modified, modified_by
		FROM `{src}`
	""")

	frappe.db.commit()

	# Validar integridad de migración
	new_count = frappe.db.sql(f"SELECT COUNT(*) FROM `{dst}`")[0][0]
	if new_count < src_count:
		frappe.log_error(
			f"Migración incompleta: {src} tenía {src_count} filas, {dst} tiene {new_count}",
			"migrate_property_copropiedad_to_declared_owner",
		)
