# Bitácora de uso de IA

## 1. Diseño de interfaz

- **Prompt:** «Propón una interfaz simple y accesible para una aplicación de inventario y préstamos comunitarios en Django, con navegación clara para socio y encargado».
- **Respuesta:** navegación por rol, tablas para inventario y préstamos, etiquetas de estado y mensajes visibles para confirmar operaciones.
- **Aceptado/corregido:** se implementó navegación condicional por `is_staff`, tablas HTML y mensajes de Django. Se ajustaron textos y rutas al dominio de Villa Los Aromos.

## 2. Estructura del código

- **Prompt:** «Sugiere una estructura Django para modelos Categoria, Herramienta y Prestamo, con formularios propios, CRUD protegido para encargado y solicitud de préstamo en sesión».
- **Respuesta:** separar modelos, formularios, vistas, rutas y templates; usar `ModelForm`, decoradores de autenticación y formularios POST para cambios.
- **Aceptado/corregido:** se usó esa separación y se añadieron transacciones al confirmar solicitudes, cancelar y registrar devoluciones para mantener inventario y préstamos consistentes.

## 3. Revisión de seguridad

- **Prompt:** «Revisa riesgos de control de acceso en un CRUD Django de préstamos: protección de rutas, cambios de estado y acceso por identificador».
- **Respuesta:** validar permisos en cada vista, restringir las consultas de socios a sus propios registros, exigir POST para acciones que modifican estado y conservar CSRF.
- **Aceptado/corregido:** se aplicó `login_required`, comprobación `is_staff`, filtro por `socio=request.user`, POST requerido y tokens CSRF en formularios de acciones. Se agregó una prueba para impedir acceso a préstamos ajenos.
