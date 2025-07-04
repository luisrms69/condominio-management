# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import json

import frappe
from frappe.model.document import Document


class ContributionCategory(Document):
	"""
	Configuración específica de contribuciones por módulo.

	Funcionalidades principales:
	- Definir qué tipos de contribuciones acepta cada módulo
	- Configurar workflow de aprobación específico
	- Establecer validaciones requeridas
	- Configurar formato de export para fixtures

	Parámetros importantes:
	    module_name (Select): Nombre del módulo que acepta contribuciones
	    contribution_type (Data): Tipo específico de contribución
	    approval_workflow (Link): Workflow de aprobación a aplicar
	    export_doctype (Data): DocType destino en fixtures
	    required_fields (JSON): Campos obligatorios para validación

	Ejemplo de uso:
	    category = frappe.new_doc("Contribution Category")
	    category.module_name = "Document Generation"
	    category.contribution_type = "Infrastructure Template"
	    category.export_doctype = "Master Template Registry"
	    category.save()
	"""

	def validate(self):
		"""
		Validar configuración de categoría de contribución.

		Verifica que la configuración sea consistente y válida.
		"""
		self.validate_required_fields_json()
		self.validate_unique_category()

	def validate_required_fields_json(self):
		"""
		Validar que el JSON de campos requeridos tenga formato válido.

		Raises:
		    ValidationError: Si el JSON no es válido
		"""
		if self.required_fields:
			try:
				json.loads(self.required_fields)
			except json.JSONDecodeError:
				frappe.throw(frappe._("Campos obligatorios debe ser un JSON válido"))

	def validate_unique_category(self):
		"""
		Validar que no exista otra categoría con la misma combinación módulo-tipo.

		Raises:
		    ValidationError: Si ya existe la combinación
		"""
		existing = frappe.db.exists(
			"Contribution Category",
			{
				"module_name": self.module_name,
				"contribution_type": self.contribution_type,
				"name": ("!=", self.name if not self.is_new() else ""),
			},
		)

		if existing:
			frappe.throw(
				frappe._("Ya existe una categoría para {0} - {1}").format(
					self.module_name, self.contribution_type
				)
			)

	def get_required_fields_list(self):
		"""
		Obtener lista de campos requeridos desde JSON.

		Returns:
		    list: Lista de campos requeridos
		"""
		if not self.required_fields:
			return []

		try:
			return json.loads(self.required_fields)
		except json.JSONDecodeError:
			return []

	def validate_contribution_data(self, contribution_data):
		"""
		Validar que los datos de contribución cumplan con los requerimientos.

		Args:
		    contribution_data (dict): Datos de la contribución a validar

		Raises:
		    ValidationError: Si faltan campos requeridos
		"""
		required_fields = self.get_required_fields_list()

		missing_fields = []
		for field in required_fields:
			if not contribution_data.get(field):
				missing_fields.append(field)

		if missing_fields:
			frappe.throw(frappe._("Campos requeridos faltantes: {0}").format(", ".join(missing_fields)))

	def get_module_handler_path(self):
		"""
		Obtener ruta del handler específico del módulo.

		Returns:
		    str: Ruta del módulo handler
		"""
		module_paths = {
			"Document Generation": "condominium_management.document_generation.contrib.handler",
			"Maintenance": "condominium_management.maintenance.contrib.handler",
			"Contracts": "condominium_management.contracts.contrib.handler",
			"Physical Spaces": "condominium_management.physical_spaces.contrib.handler",
			"Financial Management": "condominium_management.financial_management.contrib.handler",
			"Security": "condominium_management.security.contrib.handler",
		}

		return module_paths.get(self.module_name)
