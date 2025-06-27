# Sistema de Gestión de Condominios
Sistema integral construido sobre ERPNext/Frappe framework.

## 🏗️ Arquitectura

### Sistema Principal
- **Gestión Multi-Company**: Separación financiera completa entre condominios
- **Espacios Físicos Jerárquicos**: Anidamiento ilimitado con modelo nested set
- **Mantenimiento Profesional**: Programación multi-nivel y órdenes flexibles
- **Control de Accesos**: Sistema integrado con QR dinámicos
- **Gestión Democrática**: Comités, asambleas y votación electrónica
- **Generación de Documentos**: Estatutos y reglamentos dinámicos


### Módulos Core
condominium_management/
├── companies/              # Multi-company y master data
├── physical_spaces/        # Espacios físicos jerárquicos
├── residents/              # Gestión de usuarios y perfiles
├── access_control/         # Control de accesos avanzado
├── maintenance_professional/ # Mantenimiento multi-nivel
├── committee_management/   # Gestión democrática y asambleas
├── compliance_legal/       # Compliance completo
├── document_generation/    # Generación dinámica documentos
├── communication_system/   # Comunicación segmentada
├── package_correspondence/ # Gestión de paquetería
├── financial_basic/        # Contabilidad básica
├── analytics_dashboard/    # Analytics completos
└── helpdesk_integration/   # Integración con tickets

## 🚀 Instalación

### Requisitos Previos
- Frappe/ERPNext v15+
- Python 3.8+
- MariaDB/MySQL
- Node.js (para compilación de assets)

### Instalación en Frappe Bench
```bash
# En tu frappe-bench
bench get-app https://github.com/[tu-usuario]/condominium_management
bench install-app condominium_management --site [tu-sitio]
bench migrate
```

📄 Licenciamiento

Sistema Principal: GPL v3 (obligatorio por ERPNext)
Productos Standalone: Dual License (MIT/Comercial)
Features Premium: Comercial Propietario

🤝 Contribuir

Fork el proyecto
Crear feature branch (git checkout -b feature/nueva-funcionalidad)
Commit cambios (git commit -am 'feat: agregar nueva funcionalidad')
Push al branch (git push origin feature/nueva-funcionalidad)
Crear Pull Request

📞 Contacto

Email: it@buzola.mx
Empresa: Buzola



## Estado: Desarrollo Activo
