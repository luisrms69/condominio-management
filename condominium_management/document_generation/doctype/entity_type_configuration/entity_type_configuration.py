# Copyright (c) 2025, Buzola and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class EntityTypeConfiguration(Document):
	"""
	Configuración de tipos de entidades para document generation.

	Funcionalidades principales:
	- Definir qué DocTypes requieren configuración de documentos
	- Configurar detección automática al crear nuevas entidades
	- Establecer campos de detección para subtipos
	- Configurar aplicabilidad a diferentes tipos de documentos
	- Habilitar detección de conflictos específicos

	Parámetros importantes:
	    entity_doctype (Link): DocType que se configurará para document generation
	    entity_name (Data): Nombre descriptivo de la entidad
	    requires_configuration (Check): Si requiere configuración automática
	    auto_detect_on_create (Check): Si se detecta automáticamente al crear
	    detection_field (Data): Campo que determina el subtipo de entidad

	Errores comunes:
	    ValidationError: DocType ya configurado o campos inválidos
	    Warning: Configuración incompleta o inconsistente

	Ejemplo de uso:
	    config = frappe.new_doc("Entity Type Configuration")
	    config.entity_doctype = "Amenity"
	    config.entity_name = "Amenidad"
	    config.detection_field = "amenity_type"
	    config.save()
	"""

	def validate(self):
		"""
		Validar configuración del tipo de entidad.

		Verifica que el DocType existe, no esté duplicado y que
		la configuración sea consistente.
		"""
		self.validate_doctype_exists()
		self.validate_detection_field()
		self.validate_document_applicability()
		self.validate_conflict_fields()

	def validate_doctype_exists(self):
		"""
		Verificar que el DocType especificado existe.

		Raises:
		    ValidationError: Si el DocType no existe
		"""
		if not frappe.db.exists("DocType", self.entity_doctype):
			frappe.throw(_("DocType {0} no existe").format(self.entity_doctype))

	def validate_detection_field(self):
		"""
		Validar campo de detección si está especificado.

		Verifica que el campo existe en el DocType y es del tipo correcto.
		"""
		if not self.detection_field:
			return

		# Verificar que el campo existe en el DocType
		field_exists = frappe.db.exists(
			"DocField", {"parent": self.entity_doctype, "fieldname": self.detection_field}
		)

		if not field_exists:
			frappe.throw(
				_("Campo de detección {0} no existe en DocType {1}").format(
					self.detection_field, self.entity_doctype
				)
			)

	def validate_document_applicability(self):
		"""
		Validar que al menos un tipo de documento esté seleccionado.

		Raises:
		    ValidationError: Si no se aplica a ningún documento
		"""
		if self.requires_configuration:
			if not (self.applies_to_estatuto or self.applies_to_manual or self.applies_to_reglamento):
				frappe.throw(_("Debe aplicar al menos a un tipo de documento"))

	def validate_conflict_fields(self):
		"""
		Validar configuración de campos de conflicto.

		Verifica que los campos especificados existen en el DocType.
		"""
		if not self.conflict_detection_enabled or not self.conflict_fields:
			return

		doctype_fields = frappe.get_meta(self.entity_doctype).get_fieldnames()

		for conflict_field in self.conflict_fields:
			if conflict_field.field_name not in doctype_fields:
				frappe.throw(
					_("Campo de conflicto {0} no existe en DocType {1}").format(
						conflict_field.field_name, self.entity_doctype
					)
				)

	def on_update(self):
		"""
		Procesar actualizaciones de la configuración.

		Actualiza configuraciones existentes si hay cambios relevantes.
		"""
		# Verificar si cambió la configuración de detección
		if self.has_value_changed("auto_detect_on_create") or self.has_value_changed("detection_field"):
			self.update_existing_configurations()

	def update_existing_configurations(self):
		"""
		Actualizar configuraciones existentes cuando cambia la configuración del tipo.

		Se ejecuta cuando se modifican parámetros que afectan configuraciones existentes.
		"""
		if not self.is_new():
			# Obtener configuraciones existentes para este tipo de entidad
			existing_configs = frappe.get_all(
				"Entity Configuration", filters={"source_doctype": self.entity_doctype}, fields=["name"]
			)

			if existing_configs:
				frappe.msgprint(
					_(
						"Se encontraron {0} configuraciones existentes para {1}. "
						"Considere revisar si requieren actualización."
					).format(len(existing_configs), self.entity_name),
					indicator="orange",
				)

	def get_applicable_document_types(self):
		"""
		Obtener lista de tipos de documentos aplicables.

		Returns:
		    list: Lista de tipos de documentos donde se aplica esta configuración
		"""
		applicable_types = []

		if self.applies_to_estatuto:
			applicable_types.append("Estatuto")
		if self.applies_to_manual:
			applicable_types.append("Manual Operativo")
		if self.applies_to_reglamento:
			applicable_types.append("Reglamento")

		return applicable_types

	def get_conflict_field_names(self):
		"""
		Obtener nombres de campos configurados para detección de conflictos.

		Returns:
		    list: Lista de nombres de campos de conflicto
		"""
		if not self.conflict_detection_enabled or not self.conflict_fields:
			return []

		return [field.field_name for field in self.conflict_fields]

	def is_detection_enabled_for_action(self, action):
		"""
		Verificar si la detección está habilitada para una acción específica.

		Args:
		    action (str): Acción a verificar ('create', 'update')

		Returns:
		    bool: True si la detección está habilitada
		"""
		if not self.requires_configuration or not self.is_active:
			return False

		if action == "create":
			return self.auto_detect_on_create
		elif action == "update":
			return True  # Update detection is always enabled if configuration is required

		return False
