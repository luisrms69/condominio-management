import frappe


def execute():
	"""Migrar Committee Member al modelo redesignado.

	Cambios:
	  - Añade columna 'company' derivada de property_registry.company
	  - Crea Committee Positions para cada company+role encontrado
	  - Migra 'role_in_committee' → 'committee_position'

	Idempotente: puede correr múltiples veces sin efectos secundarios.
	"""
	# 1. Añadir company a registros existentes si la columna existe y está vacía
	if frappe.db.has_column("Committee Member", "company"):
		frappe.db.sql("""
			UPDATE `tabCommittee Member` cm
			INNER JOIN `tabProperty Registry` pr ON cm.property_registry = pr.name
			SET cm.company = pr.company
			WHERE (cm.company IS NULL OR cm.company = '')
			  AND cm.property_registry IS NOT NULL
			  AND cm.property_registry != ''
		""")

	# 2. Migrar role_in_committee → committee_position
	if not (
		frappe.db.has_column("Committee Member", "role_in_committee")
		and frappe.db.has_column("Committee Member", "committee_position")
	):
		return

	# Obtener pares únicos (company, role) que necesitan Committee Position
	pairs = frappe.db.sql(
		"""
		SELECT DISTINCT cm.company, cm.role_in_committee
		FROM `tabCommittee Member` cm
		WHERE cm.committee_position IS NULL OR cm.committee_position = ''
		  AND cm.role_in_committee IS NOT NULL
		  AND cm.role_in_committee != ''
		  AND cm.company IS NOT NULL
		  AND cm.company != ''
	""",
		as_dict=True,
	)

	hierarchy_map = {"Presidente": 4, "Secretario": 3, "Tesorero": 2, "Vocal": 1}

	for pair in pairs:
		company = pair.get("company")
		role = pair.get("role_in_committee")
		if not company or not role:
			continue

		pos_name = f"{company}::{role}"
		if not frappe.db.exists("Committee Position", pos_name):
			pos = frappe.get_doc(
				{
					"doctype": "Committee Position",
					"company": company,
					"position_name": role,
					"hierarchy_level": hierarchy_map.get(role, 1),
				}
			)
			pos.insert(ignore_permissions=True)

		# Vincular los registros de ese par
		frappe.db.sql(
			"""
			UPDATE `tabCommittee Member`
			SET committee_position = %(pos_name)s
			WHERE company = %(company)s
			  AND role_in_committee = %(role)s
			  AND (committee_position IS NULL OR committee_position = '')
		""",
			{"pos_name": pos_name, "company": company, "role": role},
		)

	frappe.db.commit()
