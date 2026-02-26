# 🚀 Automatización con Navegador - Articulate Rise 360

## 📋 Resumen

Sistema de automatización que simula un usuario real navegando por Articulate Rise 360 para crear cursos automáticamente.

**Problema resuelto:** Articulate Rise 360 NO tiene API pública. La solución: automatizar el navegador web usando Playwright.

**Cambio fundamental:**
- ❌ ANTES: Intentaba usar una API inexistente (rise360_client.py)
- ✅ AHORA: Automatiza el navegador real con Playwright (rise360_browser.py)

---

## 🎯 ¿Qué hace?

1. **Descarga contenido educativo del Word** (.docx)
2. **Extrae la estructura** de unidades, temas y contenido
3. **Abre navegador Chromium** de forma automática
4. **Simula login** en Rise 360 con tus credenciales
5. **Crea estructura completa:**
   - 5 Unidades
   - 15+ Temas/Lecciones
   - Bloques de contenido (Narrativa, Conceptos, Académico, Video, Interactividad)
6. **Publica el curso** cuando termina

---

## 🛠️ Instalación

### Paso 1: Clonar/Acceder al repositorio
```bash
cd /home/user/Articulate-Rise
```

### Paso 2: Crear entorno virtual (recomendado)
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### Paso 3: Instalar dependencias
```bash
pip install -r requirements.txt
```

### Paso 4: Instalar navegadores de Playwright
```bash
python -m playwright install chromium
```

Si hay problemas de conectividad, intenta:
```bash
python -m playwright install chromium --with-deps
```

### Paso 5: Verificar archivo de contenido
El archivo Word debe estar en el directorio raíz:
```bash
ls -lh course_content.docx
```

Si no está ahí, descárgalo desde GitHub:
```bash
wget "https://github.com/JimeOb/Articulate-Rise/raw/master/MCU-ALTEA%20150%20_%20Creaci%C3%B3n%20de%20Cursos%20Virtuales%20con%20IA%20para%20Profesores%20Universitarios.docx" \
  -O course_content.docx
```

---

## ▶️ Ejecución

### Opción 1: Modo SIMULACIÓN (Sin Rise 360)
```bash
python main.py --mode simulation
```
- Genera la estructura del curso
- NO conecta a Rise 360
- Produce reportes (CSV, JSON, TXT)
- **Tiempo:** ~40 segundos

### Opción 2: Modo BROWSER (Automación Real)
```bash
python main.py --mode browser --word-file course_content.docx
```

**Variantes:**
```bash
# Con navegador visible (debugging)
python main.py --mode browser --word-file course_content.docx

# Navegador headless (sin ventana visible, más rápido)
python main.py --mode browser --word-file course_content.docx --headless

# Con archivo Word personalizado
python main.py --mode browser --word-file /ruta/a/tu/archivo.docx
```

### Opción 3: Modo LEGACY (API - No disponible)
```bash
python main.py --mode production
```
- Intenta usar API de Rise 360 (probablemente no funcione sin API real)

---

## 🔐 Configurar Credenciales

### Opción A: Usar credenciales en config.py (actual)
Las credenciales ya están configuradas en `config.py`:
```python
RISE_EMAIL: str = "info@griky.co"
RISE_PASSWORD: str = "GrikyRise2026!"
```

### Opción B: Usar variables de entorno (más seguro)
Crear archivo `.env`:
```bash
RISE_EMAIL=tu@email.com
RISE_PASSWORD=tu_contraseña
MODE=browser
```

Luego usar en `config.py`:
```python
RISE_EMAIL: str = os.getenv("RISE_EMAIL", "info@griky.co")
RISE_PASSWORD: str = os.getenv("RISE_PASSWORD", "GrikyRise2026!")
```

---

## 📁 Estructura de Archivos

```
Articulate-Rise/
├── main.py                          # Punto de entrada (actualizado)
├── rise360_browser.py              # ✨ NUEVO: Automatización con Playwright
├── word_content_extractor.py       # ✨ NUEVO: Extrae contenido del Word
├── selectors.json                  # ✨ NUEVO: Selectores CSS para UI
├── course_content.docx             # ✨ NUEVO: Archivo de contenido
├── extracted_course_content.json   # Generado automáticamente
├── config.py                        # Configuración
├── requirements.txt                 # Dependencias (actualizado)
├── logs/                           # Logs de ejecución
├── screenshots/                    # Screenshots en caso de error
└── output/                         # Reportes generados
    ├── course_structure.json
    ├── course_creation_report.csv
    └── COURSE_SUMMARY.txt
```

---

## 🔧 Cómo Funcionan los Selectores CSS

El archivo `selectors.json` contiene selectores CSS para encontrar elementos en Rise 360.

**Ejemplo:**
```json
{
  "login_email": "input[type='email']",
  "login_password": "input[type='password']",
  "login_button": "button[type='submit']"
}
```

### Si el navegador no encuentra elementos:
1. **Ejecutar con navegador visible:**
   ```bash
   python main.py --mode browser  # sin --headless
   ```

2. **Inspeccionar elementos:**
   - Click derecho en el elemento → Inspect
   - Copiar el selector CSS
   - Actualizar `selectors.json`

3. **Ejemplo de selector encontrado:**
   ```bash
   # En Chrome DevTools, copiar:
   "create_course_button": "button.btn-primary:has-text('New Course')"
   ```

4. **Probar el selector con Playwright:**
   ```python
   await page.locator("button:has-text('New Course')").click()
   ```

---

## 📊 Salida Esperada

### Cuando ejecutas `--mode browser`:

1. **Navegador se abre** → Ves las acciones en pantalla
2. **Login automático** con info@griky.co
3. **Creación de curso** progresivamente
4. **Logs en consola** con estado de cada operación
5. **Screenshots** guardadas en `/screenshots/` si hay errores
6. **Archivo JSON** con contenido extraído

**Ejemplo de salida:**
```
INFO | Lanzando navegador Playwright...
INFO | Navegador iniciado
INFO | Iniciando login en Rise 360 como info@griky.co...
DEBUG | Email ingresado
DEBUG | Contraseña ingresada
INFO | ✅ Login exitoso
INFO | Creando curso: MCU-ALTEA 150 | Creación de Cursos...
INFO | ✅ Curso creado con ID: course_12345
INFO | Creando unidad 1: FUNDAMENTOS DEL DISEÑO...
INFO | ✅ Unidad 1 creada
```

---

## 🐛 Troubleshooting

### Problema: "playwright: command not found"
```bash
python -m playwright install chromium
```

### Problema: Socket timeout / Connection refused
```bash
# Esperar unos segundos y reintentar
# O ejecutar con headless=True para menos recursos
python main.py --mode browser --headless
```

### Problema: Selectores no funcionan
1. Abrir navegador visible: `python main.py --mode browser`
2. Inspeccionar elementos en Rise 360 real
3. Actualizar `selectors.json` con selectores correctos

### Problema: Login falla
1. Verificar credenciales en `config.py`
2. Verificar que la URL es correcta: `https://rise.articulate.com`
3. Tomar screenshot para debugging: revisar `/screenshots/`

### Problema: Navegador se cierra prematuramente
- Aumentar timeouts en `rise360_browser.py`:
  ```python
  self.page.set_default_timeout(20000)  # 20 segundos
  ```

---

## 📝 Archivos Modificados/Creados

### ✨ Nuevos (Browser Automation):
- `rise360_browser.py` - Core de automatización con Playwright
- `word_content_extractor.py` - Parsea documentos Word
- `selectors.json` - Configuración de selectores CSS
- `course_content.docx` - Contenido del curso (descargado)
- `BROWSER_AUTOMATION_README.md` - Este archivo

### 🔄 Actualizados:
- `main.py` - Agregado soporte para `--mode browser`
- `requirements.txt` - Agregadas: `playwright>=1.40.0`, `python-docx>=1.0.0`

### ✅ Mantenidos (sin cambios):
- `config.py`
- `models.py`
- `course_creator.py` (para modo simulación)
- `rise360_client.py` (heredado, no se usa en browser mode)

---

## 🔄 Flujo de Ejecución

```
┌─────────────────────────────────────────┐
│ Ejecutar: python main.py --mode browser │
└────────────────┬────────────────────────┘
                 │
         ┌───────▼────────┐
         │ Leer main.py   │
         └───────┬────────┘
                 │
     ┌───────────▼──────────────┐
     │ Crear WordContentExtractor│
     │ Cargar course_content.docx│
     └───────────┬──────────────┘
                 │
     ┌───────────▼──────────────────┐
     │ Extraer estructura del curso  │
     │ (5 unidades, 15+ temas)      │
     └───────────┬──────────────────┘
                 │
     ┌───────────▼───────────────────────┐
     │ Crear Rise360BrowserAutomation    │
     │ Instanciar navegador Playwright   │
     └───────────┬───────────────────────┘
                 │
     ┌───────────▼────────────────────┐
     │ Navegar a Rise 360 login       │
     │ Ingresar credenciales         │
     │ Hacer click en botón login    │
     └───────────┬────────────────────┘
                 │
     ┌───────────▼────────────────────┐
     │ Para cada unidad:              │
     │  ├─ Crear unidad              │
     │  └─ Para cada tema:           │
     │      ├─ Crear tema/lección    │
     │      └─ Insertar bloques      │
     │          ├─ Narrativa         │
     │          ├─ Conceptos         │
     │          ├─ Académico         │
     │          ├─ Video             │
     │          └─ Interactividad    │
     └───────────┬────────────────────┘
                 │
     ┌───────────▼──────────────┐
     │ Publicar curso           │
     │ Capturar URL del curso   │
     │ Generar reportes         │
     └───────────┬──────────────┘
                 │
     ┌───────────▼──────────────┐
     │ ✅ Curso creado exitosamente
     │ 📊 Reportes en /output/
     │ 📸 Logs en /logs/
     └──────────────────────────┘
```

---

## 💡 Tips de Uso

### Para debugging:
```bash
# Abre navegador visible, toma screenshots de todo
python main.py --mode browser
```

### Para optimizar tiempo:
```bash
# Usa headless mode si todo está funcionando
python main.py --mode browser --headless
```

### Para probar con otro Word:
```bash
python main.py --mode browser --word-file /ruta/a/otro.docx
```

### Para revisar lo que se extrajo:
```bash
cat extracted_course_content.json | python -m json.tool | less
```

---

## 🎓 Próximos Pasos

1. **Ejecutar en simulación primero:**
   ```bash
   python main.py --mode simulation
   ```

2. **Revisar estructura generada:**
   ```bash
   cat output/COURSE_SUMMARY.txt
   ```

3. **Instalar navegadores Playwright:**
   ```bash
   python -m playwright install chromium
   ```

4. **Ejecutar en modo browser:**
   ```bash
   python main.py --mode browser
   ```

5. **Refinar selectores basado en errores** (si es necesario)

6. **Publicar en producción** cuando todo funcione

---

## 📞 Soporte

- Revisar logs: `logs/rise360_automation_browser.log`
- Revisar screenshots: `screenshots/` (si hay errores)
- Revisar estructura extraída: `extracted_course_content.json`

---

**Versión:** 2.0 (Browser Automation)
**Fecha:** 2026-02-26
**Estado:** ✅ Implementado y listo para pruebas
