import os
import shutil

base_path = "/home/erpnext/frappe-bench/apps/condominium_management/condominium_management/companies/doctype"

# Lista de DocTypes a reorganizar
doctypes = [
	"service_management_contract",
	"master_data_sync_configuration",
	"condominium_information",
	"contract_service_item",
	"target_company_sync",
	"sync_data_type",
	"public_transport_option",
	"nearby_reference",
	"access_point_detail",
	"contact_information",
	"service_information",
	"operating_hours",
]


def find_json_file(doctype):
	"""Buscar recursivamente el archivo JSON de un DocType"""
	for root, _dirs, files in os.walk(base_path):
		for file in files:
			if file == f"{doctype}.json":
				return os.path.join(root, file)
	return None


def reorganize_doctype(doctype):
	# Encontrar el archivo JSON
	json_path = find_json_file(doctype)

	if not json_path:
		print(f"No se encontró JSON para: {doctype}")
		return

	# Ruta del directorio del DocType
	doctype_dir = os.path.join(base_path, doctype)

	# Crear subdirectorio si no existe
	os.makedirs(doctype_dir, exist_ok=True)

	# Ruta del nuevo archivo JSON
	new_json_path = os.path.join(doctype_dir, f"{doctype}.json")

	# Copiar el archivo
	shutil.copy(json_path, new_json_path)
	print(f"Reorganizado: {doctype}")


# Reorganizar todos los DocTypes
for doctype in doctypes:
	reorganize_doctype(doctype)

print("Reorganización completada.")
