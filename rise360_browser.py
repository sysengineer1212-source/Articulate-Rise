"""
Articulate Rise 360 Browser Automation Module
Automatiza la creación de cursos en Rise 360 usando Playwright
"""

import asyncio
import json
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime
from loguru import logger
from playwright.async_api import async_playwright, Page, Browser, BrowserContext


class Rise360BrowserAutomation:
    """Automatización de Articulate Rise 360 usando Playwright"""

    def __init__(
        self,
        email: str,
        password: str,
        headless: bool = False,
        screenshots_dir: str = "screenshots",
    ):
        self.email = email
        self.password = password
        self.headless = headless
        self.screenshots_dir = Path(screenshots_dir)
        self.screenshots_dir.mkdir(exist_ok=True)

        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.base_url = "https://rise.articulate.com"

        # Cargar selectores
        self.selectors = self._load_selectors()

        logger.info(f"Rise360BrowserAutomation initialized (headless={headless})")

    def _load_selectors(self) -> Dict[str, str]:
        """Cargar selectores CSS desde archivo de configuración"""
        selectors_file = Path("selectors.json")
        if selectors_file.exists():
            with open(selectors_file) as f:
                return json.load(f)
        logger.warning("selectors.json no encontrado, usando selectores por defecto")
        return {}

    async def launch_browser(self) -> None:
        """Iniciar el navegador"""
        logger.info("Lanzando navegador Playwright...")
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=self.headless)
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()

        # Configurar timeouts
        self.page.set_default_navigation_timeout(30000)
        self.page.set_default_timeout(10000)

        logger.info("Navegador iniciado")

    async def close_browser(self) -> None:
        """Cerrar el navegador"""
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        logger.info("Navegador cerrado")

    async def take_screenshot(self, name: str) -> None:
        """Tomar captura de pantalla para debugging"""
        if self.page:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = self.screenshots_dir / f"{timestamp}_{name}.png"
            await self.page.screenshot(path=str(screenshot_path))
            logger.debug(f"Screenshot guardada: {screenshot_path}")

    async def login(self) -> bool:
        """Autenticarse en Rise 360"""
        try:
            logger.info(f"Iniciando login en Rise 360 como {self.email}...")

            # Navegar a página de login
            await self.page.goto(f"{self.base_url}/login")
            await self.page.wait_for_load_state("networkidle")

            # Esperar y llenar email
            email_selector = self.selectors.get("login_email", "input[type='email']")
            await self.page.fill(email_selector, self.email)
            logger.debug("Email ingresado")

            # Esperar y llenar contraseña
            password_selector = self.selectors.get("login_password", "input[type='password']")
            await self.page.fill(password_selector, self.password)
            logger.debug("Contraseña ingresada")

            # Click en botón de login
            login_button_selector = self.selectors.get("login_button", "button[type='submit']")
            await self.page.click(login_button_selector)

            # Esperar a que se redirija al dashboard
            await self.page.wait_for_url("**/dashboard**", timeout=15000)
            await self.page.wait_for_load_state("networkidle")

            logger.info("✅ Login exitoso")
            await self.take_screenshot("login_success")
            return True

        except Exception as e:
            logger.error(f"❌ Error en login: {e}")
            await self.take_screenshot("login_error")
            return False

    async def create_course(self, course_name: str, course_description: str) -> Optional[str]:
        """Crear un nuevo curso"""
        try:
            logger.info(f"Creando curso: {course_name}")

            # Click en botón "New Course" o "Create Course"
            create_course_selector = self.selectors.get(
                "create_course_button",
                "button:has-text('New Course')"
            )
            await self.page.click(create_course_selector)
            await self.page.wait_for_load_state("networkidle")

            # Llenar formulario del curso
            course_name_selector = self.selectors.get("course_name_input", "input[placeholder*='Course']")
            await self.page.fill(course_name_selector, course_name)
            logger.debug(f"Nombre del curso: {course_name}")

            # Llenar descripción si existe el campo
            course_desc_selector = self.selectors.get("course_description_input", "textarea")
            if await self.page.query_selector(course_desc_selector):
                await self.page.fill(course_desc_selector, course_description)
                logger.debug("Descripción ingresada")

            # Click en Create/Save
            save_course_selector = self.selectors.get("save_course_button", "button:has-text('Create')")
            await self.page.click(save_course_selector)
            await self.page.wait_for_load_state("networkidle")

            # Extraer Course ID de la URL
            course_id = self._extract_course_id()
            logger.info(f"✅ Curso creado con ID: {course_id}")
            await self.take_screenshot("course_created")

            return course_id

        except Exception as e:
            logger.error(f"❌ Error creando curso: {e}")
            await self.take_screenshot("course_creation_error")
            return None

    async def create_unit(self, course_id: str, unit_title: str, unit_number: int) -> Optional[str]:
        """Crear una unidad dentro del curso"""
        try:
            logger.info(f"Creando unidad {unit_number}: {unit_title}")

            # Navegar al editor del curso
            await self.page.goto(f"{self.base_url}/courses/{course_id}/edit")
            await self.page.wait_for_load_state("networkidle")

            # Click en agregar unidad
            add_unit_selector = self.selectors.get(
                "add_unit_button",
                "button:has-text('Add Unit')"
            )
            await self.page.click(add_unit_selector)
            await self.page.wait_for_load_state("networkidle")

            # Llenar nombre de la unidad
            unit_name_selector = self.selectors.get("unit_name_input", "input[placeholder*='Unit']")
            await self.page.fill(unit_name_selector, unit_title)

            # Confirmar
            confirm_selector = self.selectors.get("confirm_button", "button:has-text('Create')")
            await self.page.click(confirm_selector)
            await self.page.wait_for_load_state("networkidle")

            unit_id = self._extract_unit_id()
            logger.info(f"✅ Unidad {unit_number} creada con ID: {unit_id}")
            await self.take_screenshot(f"unit_{unit_number}_created")

            return unit_id

        except Exception as e:
            logger.error(f"❌ Error creando unidad: {e}")
            await self.take_screenshot(f"unit_creation_error_{unit_number}")
            return None

    async def create_lesson(
        self,
        course_id: str,
        unit_id: str,
        lesson_title: str,
        unit_number: int,
        lesson_number: int
    ) -> Optional[str]:
        """Crear una lección/tema dentro de una unidad"""
        try:
            logger.info(f"Creando lección {unit_number}.{lesson_number}: {lesson_title}")

            # Navegar al editor de unidad
            await self.page.goto(f"{self.base_url}/courses/{course_id}/units/{unit_id}/edit")
            await self.page.wait_for_load_state("networkidle")

            # Click en agregar lección
            add_lesson_selector = self.selectors.get(
                "add_lesson_button",
                "button:has-text('Add Lesson')"
            )
            await self.page.click(add_lesson_selector)
            await self.page.wait_for_load_state("networkidle")

            # Llenar nombre de la lección
            lesson_name_selector = self.selectors.get("lesson_name_input", "input[placeholder*='Lesson']")
            await self.page.fill(lesson_name_selector, lesson_title)

            # Confirmar
            confirm_selector = self.selectors.get("confirm_button", "button:has-text('Create')")
            await self.page.click(confirm_selector)
            await self.page.wait_for_load_state("networkidle")

            lesson_id = self._extract_lesson_id()
            logger.info(f"✅ Lección {unit_number}.{lesson_number} creada con ID: {lesson_id}")
            await self.take_screenshot(f"lesson_{unit_number}_{lesson_number}_created")

            return lesson_id

        except Exception as e:
            logger.error(f"❌ Error creando lección: {e}")
            await self.take_screenshot(f"lesson_creation_error_{unit_number}_{lesson_number}")
            return None

    async def insert_text_block(
        self,
        course_id: str,
        lesson_id: str,
        title: str,
        content: str,
        block_type: str = "Narrative"
    ) -> bool:
        """Insertar un bloque de texto en una lección"""
        try:
            logger.debug(f"Insertando bloque {block_type}: {title[:50]}...")

            # Navegar al editor de lección
            await self.page.goto(f"{self.base_url}/courses/{course_id}/lessons/{lesson_id}/edit")
            await self.page.wait_for_load_state("networkidle")

            # Click en Add Content
            add_content_selector = self.selectors.get(
                "add_content_button",
                "button:has-text('Add Content')"
            )
            await self.page.click(add_content_selector)
            await self.page.wait_for_load_state("networkidle")

            # Seleccionar tipo "Text"
            text_type_selector = self.selectors.get(
                "text_block_type",
                "button:has-text('Text')"
            )
            await self.page.click(text_type_selector)
            await self.page.wait_for_load_state("networkidle")

            # Llenar título
            title_selector = self.selectors.get("block_title_input", "input[placeholder*='Title']")
            await self.page.fill(title_selector, title)

            # Llenar contenido
            content_selector = self.selectors.get("block_content_input", "div[contenteditable='true']")
            await self.page.fill(content_selector, content)

            # Guardar bloque
            save_selector = self.selectors.get("save_block_button", "button:has-text('Save')")
            await self.page.click(save_selector)
            await self.page.wait_for_load_state("networkidle")

            logger.debug(f"✅ Bloque {block_type} insertado")
            return True

        except Exception as e:
            logger.error(f"❌ Error insertando bloque de texto: {e}")
            return False

    def _extract_course_id(self) -> Optional[str]:
        """Extraer Course ID de la URL actual"""
        try:
            url = self.page.url if self.page else ""
            # Patrón: /courses/{courseId}
            parts = url.split("/")
            if "courses" in parts:
                idx = parts.index("courses")
                if idx + 1 < len(parts):
                    return parts[idx + 1]
        except Exception as e:
            logger.debug(f"Error extrayendo Course ID: {e}")
        return None

    def _extract_unit_id(self) -> Optional[str]:
        """Extraer Unit ID de la URL actual"""
        try:
            url = self.page.url if self.page else ""
            parts = url.split("/")
            if "units" in parts:
                idx = parts.index("units")
                if idx + 1 < len(parts):
                    return parts[idx + 1]
        except Exception as e:
            logger.debug(f"Error extrayendo Unit ID: {e}")
        return None

    def _extract_lesson_id(self) -> Optional[str]:
        """Extraer Lesson ID de la URL actual"""
        try:
            url = self.page.url if self.page else ""
            parts = url.split("/")
            if "lessons" in parts:
                idx = parts.index("lessons")
                if idx + 1 < len(parts):
                    return parts[idx + 1]
        except Exception as e:
            logger.debug(f"Error extrayendo Lesson ID: {e}")
        return None

    async def publish_course(self, course_id: str) -> bool:
        """Publicar el curso"""
        try:
            logger.info("Publicando curso...")

            await self.page.goto(f"{self.base_url}/courses/{course_id}/settings")
            await self.page.wait_for_load_state("networkidle")

            # Click en botón Publish
            publish_selector = self.selectors.get("publish_button", "button:has-text('Publish')")
            await self.page.click(publish_selector)
            await self.page.wait_for_load_state("networkidle")

            logger.info("✅ Curso publicado")
            await self.take_screenshot("course_published")
            return True

        except Exception as e:
            logger.error(f"❌ Error publicando curso: {e}")
            return False

    def get_current_url(self) -> str:
        """Obtener la URL actual"""
        return self.page.url if self.page else ""


async def run_automation(
    email: str,
    password: str,
    course_config: Dict,
    headless: bool = False
) -> bool:
    """Ejecutar la automatización completa"""

    automation = Rise360BrowserAutomation(
        email=email,
        password=password,
        headless=headless
    )

    try:
        await automation.launch_browser()

        # Login
        if not await automation.login():
            return False

        # Crear curso
        course_id = await automation.create_course(
            course_name=course_config["name"],
            course_description=course_config.get("description", "")
        )

        if not course_id:
            return False

        # Crear unidades y lecciones
        for unit_idx, unit in enumerate(course_config.get("units", []), 1):
            unit_id = await automation.create_unit(
                course_id=course_id,
                unit_title=unit["title"],
                unit_number=unit_idx
            )

            if not unit_id:
                continue

            for lesson_idx, lesson in enumerate(unit.get("lessons", []), 1):
                lesson_id = await automation.create_lesson(
                    course_id=course_id,
                    unit_id=unit_id,
                    lesson_title=lesson["title"],
                    unit_number=unit_idx,
                    lesson_number=lesson_idx
                )

                if not lesson_id:
                    continue

                # Insertar contenido
                for content in lesson.get("content", []):
                    await automation.insert_text_block(
                        course_id=course_id,
                        lesson_id=lesson_id,
                        title=content["title"],
                        content=content["text"],
                        block_type=content.get("type", "Text")
                    )

        # Publicar curso
        await automation.publish_course(course_id)

        logger.info("✅ Automatización completada exitosamente")
        return True

    except Exception as e:
        logger.error(f"❌ Error en automatización: {e}")
        return False

    finally:
        await automation.close_browser()


if __name__ == "__main__":
    # Ejemplo de uso
    async def main():
        config = {
            "name": "Test Course",
            "description": "Test Description",
            "units": [
                {
                    "title": "Unit 1",
                    "lessons": [
                        {
                            "title": "Lesson 1",
                            "content": [
                                {
                                    "title": "Introduction",
                                    "text": "This is the introduction",
                                    "type": "Narrative"
                                }
                            ]
                        }
                    ]
                }
            ]
        }

        success = await run_automation(
            email="info@griky.co",
            password="GrikyRise2026!",
            course_config=config,
            headless=False
        )

        logger.info(f"Resultado: {'✅ Éxito' if success else '❌ Fallo'}")

    asyncio.run(main())
