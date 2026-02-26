"""Main entry point for MCU-ALTEA 150 Course Automation"""
import sys
import asyncio
import argparse
from loguru import logger
from pathlib import Path
from config import settings
from course_creator import MCUAltea150CourseCreator
from word_content_extractor import WordContentExtractor
from rise360_browser import run_automation


def setup_logging(log_dir: str = None):
    """Setup logging configuration

    Args:
        log_dir: Directory for logs
    """
    if log_dir is None:
        log_dir = settings.LOGS_DIR

    Path(log_dir).mkdir(exist_ok=True)

    # Remove default handler
    logger.remove()

    # Add file handler
    log_file = f"{log_dir}/rise360_automation_{settings.MODE}.log"
    logger.add(
        log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        level="DEBUG"
    )

    # Add console handler
    logger.add(
        sys.stdout,
        format="<level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> | {message}",
        level="INFO"
    )

    logger.info(f"Logging configured. Log file: {log_file}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="MCU-ALTEA 150 Course Automation for Rise 360"
    )
    parser.add_argument(
        "--mode",
        choices=["simulation", "production", "browser"],
        default="simulation",
        help="Execution mode: simulation, production (API), or browser (Playwright automation)"
    )
    parser.add_argument(
        "--skip-validation",
        action="store_true",
        help="Skip content validation"
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run browser in headless mode (only for --mode browser)"
    )
    parser.add_argument(
        "--word-file",
        default="course_content.docx",
        help="Path to Word file with course content (default: course_content.docx)"
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging()

    logger.info("="*80)
    logger.info("MCU-ALTEA 150 COURSE AUTOMATION")
    logger.info("="*80)
    logger.info(f"Mode: {args.mode}")
    logger.info(f"Skip Validation: {args.skip_validation}")

    # Handle different modes
    if args.mode == "browser":
        return main_browser(args)
    else:
        return main_legacy(args)


def main_legacy(args):
    """Ejecutar automatización con modo simulación/API (código original)"""
    logger.info(f"Usando automatización LEGACY (API/Simulation)")

    # Create course creator
    creator = MCUAltea150CourseCreator(mode=args.mode)

    # Run automation
    success = creator.run()

    # Print results
    if success:
        logger.info("\n" + "="*80)
        logger.info("✅ AUTOMATION COMPLETED SUCCESSFULLY")
        logger.info("="*80)
        logger.info(f"\nReports available in: {settings.OUTPUT_DIR}/")
        logger.info(f"Course URL: {creator.client.get_course_url()}")
        return 0
    else:
        logger.error("\n" + "="*80)
        logger.error("❌ AUTOMATION FAILED")
        logger.error("="*80)
        logger.error(f"Check logs in: {settings.LOGS_DIR}/")
        return 1


def main_browser(args):
    """Ejecutar automatización con navegador Playwright"""
    logger.info(f"Usando automatización BROWSER (Playwright)")
    logger.info(f"Headless mode: {args.headless}")

    # Extraer contenido del archivo Word
    logger.info(f"Extrayendo contenido de: {args.word_file}")
    extractor = WordContentExtractor(args.word_file)

    if not extractor.doc:
        logger.error(f"No se pudo cargar el archivo: {args.word_file}")
        return 1

    # Obtener contenido extraído
    content = extractor.extract_all_content()
    structure = extractor.get_course_structure()

    logger.info(f"Contenido extraído:")
    logger.info(f"  - Título: {structure['name']}")
    logger.info(f"  - Unidades: {len(structure['units'])}")

    for unit in structure['units']:
        logger.info(f"    - {unit['title']}: {len(unit['lessons'])} temas")

    # Exportar contenido para referencia
    extractor.export_json("extracted_course_content.json")

    # Ejecutar automatización del navegador
    try:
        logger.info("\nIniciando automatización del navegador...")

        success = asyncio.run(
            run_automation(
                email=settings.RISE_EMAIL,
                password=settings.RISE_PASSWORD,
                course_config=structure,
                headless=args.headless
            )
        )

        if success:
            logger.info("\n" + "="*80)
            logger.info("✅ BROWSER AUTOMATION COMPLETED SUCCESSFULLY")
            logger.info("="*80)
            logger.info(f"\nCheck extracted content in: extracted_course_content.json")
            return 0
        else:
            logger.error("\n" + "="*80)
            logger.error("❌ BROWSER AUTOMATION FAILED")
            logger.error("="*80)
            logger.error(f"Check logs in: {settings.LOGS_DIR}/")
            logger.error(f"Check screenshots in: screenshots/")
            return 1

    except Exception as e:
        logger.error(f"Error ejecutando automatización: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
