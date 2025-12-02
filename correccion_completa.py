# correccion_completa.py
import os
import re

# Archivos a corregir
archivos_settings = [
    'sistemaTBC_demo/sistematbc_demo/settings.py',
    'sistemaTBC_demo/settings/development.py',
    'sistemaTBC_demo/settings/production.py',
    'sistemaTBC_demo/settings/base.py',
    'sistemaTBC_demo/settings_old.py'  # También este
]

for archivo in archivos_settings:
    if not os.path.exists(archivo):
        print(f"⚠️  No existe: {archivo}")
        continue
    
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Guardar copia original
        with open(archivo + '.backup', 'w', encoding='utf-8') as f:
            f.write(contenido)
        
        # ELIMINAR COMPLETAMENTE debug_toolbar
        lineas = contenido.split('\n')
        nuevas_lineas = []
        
        for linea in lineas:
            # Comentar cualquier línea que contenga debug_toolbar, djdt o django_browser_reload
            if any(term in linea.lower() for term in ['debug_toolbar', 'djdt', 'django_browser_reload', 'debugtoolbarmiddleware', 'browserreloadmiddleware']):
                # Mantener comentarios existentes, agregar si no está comentado
                if not linea.strip().startswith('#'):
                    nueva_linea = '# ' + linea
                    # Agregar nota explicativa
                    if not nueva_linea.strip().endswith('# ELIMINADO POR ERROR djdt'):
                        nueva_linea += '  # ELIMINADO POR ERROR djdt'
                    nuevas_lineas.append(nueva_linea)
                else:
                    nuevas_lineas.append(linea)
            else:
                nuevas_lineas.append(linea)
        
        contenido_corregido = '\n'.join(nuevas_lineas)
        
        # Guardar archivo corregido
        with open(archivo, 'w', encoding='utf-8') as f:
            f.write(contenido_corregido)
        
        # Contar cambios
        lineas_originales = len(lineas)
        lineas_corregidas = len(nuevas_lineas)
        cambios = sum(1 for i in range(min(lineas_originales, lineas_corregidas)) 
                     if lineas[i] != nuevas_lineas[i])
        
        print(f"✅ {archivo}: {cambios} líneas corregidas")
        
    except Exception as e:
        print(f"❌ Error en {archivo}: {str(e)}")

print("\n🔍 Verificando que no queden referencias...")

# Buscar referencias restantes
os.system('findstr /s /i "debug_toolbar djdt django_browser_reload" *.py *.html *.txt 2>nul | findstr /v "venv\\Lib\\site-packages" | findstr /v ".backup"')

print("\n🎯 LISTO. Ahora verifica qué settings está usando Django.")