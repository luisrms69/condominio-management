#!/bin/bash

# Script wrapper para ejecutar testing desde directorio base
echo "🔧 Ejecutando testing desde directorio base..."

# Cambiar al directorio base de frappe-bench
cd /home/erpnext/frappe-bench

# Verificar que estamos en el directorio correcto
if [ ! -d "sites/condo1.dev" ]; then
    echo "❌ Error: No se puede acceder a sites/condo1.dev"
    exit 1
fi

echo "✅ Directorio base confirmado: $(pwd)"
echo "✅ Site de testing: condo1.dev"

# Ejecutar el script de testing
python3 apps/condominium_management/quick_test.py

echo "🔄 Testing completado, regresando al directorio de trabajo..."