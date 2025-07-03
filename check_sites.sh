#!/bin/bash

echo "🔍 Verificando sites disponibles..."
cd /home/erpnext/frappe-bench

echo "📁 Sites en directorio:"
ls -la sites/ | grep "\.dev"

echo "🔧 Site actual configurado:"
if [ -f "sites/currentsite.txt" ]; then
    cat sites/currentsite.txt
else
    echo "No hay currentsite.txt"
fi

echo "🧪 Probando acceso a domika.dev..."
python3 -c "
import frappe
try:
    frappe.init('domika.dev')
    frappe.connect()
    print('✅ domika.dev accesible')
except Exception as e:
    print(f'❌ domika.dev: {e}')
"

echo "🧪 Probando acceso a condo1.dev..."
python3 -c "
import frappe
try:
    frappe.init('condo1.dev')
    frappe.connect()
    print('✅ condo1.dev accesible')
except Exception as e:
    print(f'❌ condo1.dev: {e}')
"