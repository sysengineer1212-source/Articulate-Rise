"""Main entry point for MCU-ALTEA 150 Course Automation"""
import sys
import argparse
from loguru import logger
from pathlib import Path
from config import settings
from course_creator import MCUAltea150CourseCreator


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
        choices=["simulation", "production"],
        default="simulation",
        help="Execution mode: simulation (default) or production"
    )
    parser.add_argument(
        "--skip-validation",
        action="store_true",
        help="Skip content validation"
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging()

    logger.info("="*80)
    logger.info("MCU-ALTEA 150 COURSE AUTOMATION")
    logger.info("="*80)
    logger.info(f"Mode: {args.mode}")
    logger.info(f"Skip Validation: {args.skip_validation}")

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


if __name__ == "__main__":
    sys.exit(main())
