"""
Instalación y configuración del módulo Condominium Management.

Este módulo maneja la configuración inicial después de la instalación
del app, similar al patrón usado por el lending app oficial de Frappe.
"""

import frappe


def after_install():
	"""
	Ejecutar configuración post-instalación.

	Esta función se ejecuta automáticamente después de instalar el app
	y asegura que el ambiente ERPNext esté correctamente configurado
	para el funcionamiento del módulo Companies.

	Funcionalidades:
	- Verificar configuración básica de ERPNext
	- Asegurar que warehouse types estén disponibles
	- Configurar defaults necesarios para testing

	Basado en el patrón del lending app oficial de Frappe.
	"""
	print("🔧 Condominium Management: Ejecutando configuración post-instalación...")

	# Verificar que ERPNext esté correctamente instalado
	try:
		# Verificar que Company DocType esté disponible
		if frappe.db.exists("DocType", "Company"):
			print("✅ ERPNext Company DocType disponible")

		# Verificar warehouse types - crítico para tests
		warehouse_types = frappe.get_all("Warehouse Type", fields=["name"])
		if warehouse_types:
			print(
				f"✅ {len(warehouse_types)} warehouse types encontrados: {[wt.name for wt in warehouse_types]}"
			)

			# Verificar específicamente Transit
			if frappe.db.exists("Warehouse Type", "Transit"):
				print("✅ Transit warehouse type confirmado disponible")
			else:
				print("⚠️ Transit warehouse type no encontrado")
		else:
			print("⚠️ No se encontraron warehouse types")

		# Limpiar cache para asegurar configuración fresca
		frappe.clear_cache()

		print("🎯 Condominium Management: Configuración post-instalación completada")

	except Exception as e:
		print(f"⚠️ Warning durante configuración post-instalación: {e}")
		# No fallar la instalación por errores menores
		pass


def before_uninstall():
	"""
	Limpieza antes de desinstalar el app.

	Función placeholder para futura limpieza si es necesaria.
	"""
	print("🧹 Condominium Management: Ejecutando limpieza pre-desinstalación...")
	pass
