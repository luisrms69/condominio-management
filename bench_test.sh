#!/bin/bash

echo "🔧 Testing usando bench directamente..."
cd /home/erpnext/frappe-bench

echo "📋 Verificando sites con bench:"
echo "List sites:"
ls sites/*.dev 2>/dev/null || echo "No .dev sites found with ls"

echo "📋 Configurando site por defecto:"
echo "condo1.dev" > sites/currentsite.txt
echo "✅ Site configurado: $(cat sites/currentsite.txt)"

echo "🧪 Testing con bench console:"
echo "exit()" | bench console

echo "📊 Verificando DocTypes específicos:"
echo "
import frappe
frappe.get_all('DocType', filters={'module': 'Community Contributions'}, fields=['name'])
exit()
" | bench console