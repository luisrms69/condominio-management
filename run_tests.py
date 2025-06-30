#!/usr/bin/env python3
"""
Test Runner para el módulo Companies
Sistema de Gestión de Condominios

Este script ejecuta todos los unit tests del módulo Companies
y genera un reporte de cobertura.

Uso:
    python run_tests.py [--verbose] [--doctype DOCTYPE_NAME]

Ejemplos:
    python run_tests.py
    python run_tests.py --verbose
    python run_tests.py --doctype "Nearby Reference"
"""

import argparse
import sys
import unittest

import frappe
from frappe.utils import cint


def init_frappe():
	"""Inicializar Frappe para los tests."""
	try:
		frappe.init(site="domika.dev")
		frappe.connect()
		print("✅ Frappe inicializado correctamente")
		return True
	except Exception as e:
		print(f"❌ Error inicializando Frappe: {e}")
		return False


def get_test_modules():
	"""Obtener todos los módulos de test del módulo Companies."""
	test_modules = [
		"condominium_management.companies.doctype.nearby_reference.test_nearby_reference",
		"condominium_management.companies.doctype.access_point_detail.test_access_point_detail",
		"condominium_management.companies.doctype.sync_data_type.test_sync_data_type",
		"condominium_management.companies.doctype.service_management_contract.test_service_management_contract",
		"condominium_management.companies.doctype.condominium_information.test_condominium_information",
		"condominium_management.companies.doctype.contact_information.test_contact_information",
		"condominium_management.companies.doctype.contract_service_item.test_contract_service_item",
		"condominium_management.companies.doctype.master_data_sync_configuration.test_master_data_sync_configuration",
		"condominium_management.companies.doctype.operating_hours.test_operating_hours",
		"condominium_management.companies.doctype.public_transport_option.test_public_transport_option",
		"condominium_management.companies.doctype.service_information.test_service_information",
		"condominium_management.companies.doctype.target_company_sync.test_target_company_sync",
	]
	return test_modules


def run_single_doctype_test(doctype_name):
	"""Ejecutar tests para un DocType específico."""
	doctype_to_module = {
		"Nearby Reference": "condominium_management.companies.doctype.nearby_reference.test_nearby_reference",
		"Access Point Detail": "condominium_management.companies.doctype.access_point_detail.test_access_point_detail",
		"Sync Data Type": "condominium_management.companies.doctype.sync_data_type.test_sync_data_type",
		"Service Management Contract": "condominium_management.companies.doctype.service_management_contract.test_service_management_contract",
		"Condominium Information": "condominium_management.companies.doctype.condominium_information.test_condominium_information",
	}

	if doctype_name not in doctype_to_module:
		print(f"❌ DocType '{doctype_name}' no encontrado en los tests disponibles")
		print("📋 DocTypes disponibles:")
		for dt in doctype_to_module.keys():
			print(f"   - {dt}")
		return False

	module_name = doctype_to_module[doctype_name]
	suite = unittest.TestLoader().loadTestsFromName(module_name)
	runner = unittest.TextTestRunner(verbosity=2)
	result = runner.run(suite)

	return result.wasSuccessful()


def run_all_tests(verbose=False):
	"""Ejecutar todos los tests del módulo Companies."""
	print("🧪 Ejecutando tests del módulo Companies...")
	print("=" * 60)

	test_modules = get_test_modules()
	all_suites = []

	verbosity = 2 if verbose else 1

	for module_name in test_modules:
		try:
			suite = unittest.TestLoader().loadTestsFromName(module_name)
			all_suites.append(suite)
			print(f"✅ Cargado: {module_name.split('.')[-1]}")
		except ImportError as e:
			print(f"⚠️  No se pudo cargar: {module_name.split('.')[-1]} - {e}")
		except Exception as e:
			print(f"❌ Error cargando: {module_name.split('.')[-1]} - {e}")

	# Combinar todos los test suites
	combined_suite = unittest.TestSuite(all_suites)

	print("\n🚀 Ejecutando tests...")
	print("-" * 60)

	# Ejecutar los tests
	runner = unittest.TextTestRunner(verbosity=verbosity)
	result = runner.run(combined_suite)

	# Mostrar resumen
	print("\n📊 RESUMEN DE TESTS")
	print("=" * 60)
	print(f"Tests ejecutados: {result.testsRun}")
	print(f"Éxitos: {result.testsRun - len(result.failures) - len(result.errors)}")
	print(f"Fallos: {len(result.failures)}")
	print(f"Errores: {len(result.errors)}")

	if result.failures:
		print(f"\n❌ FALLOS ({len(result.failures)}):")
		for test, traceback in result.failures:
			print(f"   - {test}: {traceback.split(chr(10))[-2] if chr(10) in traceback else traceback}")

	if result.errors:
		print(f"\n💥 ERRORES ({len(result.errors)}):")
		for test, traceback in result.errors:
			print(f"   - {test}: {traceback.split(chr(10))[-2] if chr(10) in traceback else traceback}")

	success_rate = (
		((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100)
		if result.testsRun > 0
		else 0
	)
	print(f"\n🎯 Tasa de éxito: {success_rate:.1f}%")

	if result.wasSuccessful():
		print("✅ TODOS LOS TESTS PASARON")
	else:
		print("❌ ALGUNOS TESTS FALLARON")

	return result.wasSuccessful()


def main():
	"""Función principal del test runner."""
	parser = argparse.ArgumentParser(description="Ejecutar tests del módulo Companies")
	parser.add_argument("--verbose", "-v", action="store_true", help="Ejecutar en modo verbose")
	parser.add_argument("--doctype", "-d", type=str, help="Ejecutar tests solo para un DocType específico")

	args = parser.parse_args()

	print("🏗️  CONDOMINIUM MANAGEMENT - TEST RUNNER")
	print("📋 Módulo: Companies")
	print("🌐 Framework: Frappe v15")
	print("=" * 60)

	# Inicializar Frappe
	if not init_frappe():
		sys.exit(1)

	try:
		if args.doctype:
			# Ejecutar tests para un DocType específico
			print(f"🎯 Ejecutando tests para: {args.doctype}")
			success = run_single_doctype_test(args.doctype)
		else:
			# Ejecutar todos los tests
			success = run_all_tests(args.verbose)

		if success:
			print("\n🎉 TESTS COMPLETADOS EXITOSAMENTE")
			sys.exit(0)
		else:
			print("\n💥 TESTS FALLARON")
			sys.exit(1)

	except KeyboardInterrupt:
		print("\n\n⚠️  Tests interrumpidos por el usuario")
		sys.exit(1)
	except Exception as e:
		print(f"\n💥 Error ejecutando tests: {e}")
		sys.exit(1)
	finally:
		try:
			frappe.destroy()
		except Exception:
			pass


if __name__ == "__main__":
	main()
