"""Configuration for MCU-ALTEA 150 Course Automation"""
import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings from environment variables"""

    # Rise 360 Credentials
    RISE_EMAIL: str = "info@griky.co"
    RISE_PASSWORD: str = "GrikyRise2026!"
    RISE_BASE_URL: str = "https://rise.articulate.com"
    RISE_API_URL: str = "https://cloud.articulate.com/api"

    # Course Configuration
    COURSE_NAME: str = "Creación de Cursos Virtuales con IA para Profesores Universitarios"
    COURSE_CODE: str = "EDUTEC-CVIA-001"
    COURSE_AREA: str = "Educación y Tecnología Educativa"
    COURSE_LEVEL: str = "Master/Especialización (EQF Nivel 7)"
    COURSE_LANGUAGE: str = "es"
    COURSE_DURATION_HOURS: float = 112.5
    TARGET_AUDIENCE: str = "Docentes Universitarios (mínimo 1 año experiencia)"

    # Content Specifications
    NARRATIVE_WORDS_TARGET: int = 1800
    NARRATIVE_TOLERANCE: int = 50
    ACADEMIC_WORDS_TARGET: int = 1900
    ACADEMIC_TOLERANCE: int = 50
    VIDEO_SCRIPT_WORDS_TARGET: int = 950
    VIDEO_SCRIPT_TOLERANCE: int = 50
    VIDEO_DURATION_MINUTES: int = 5
    VIDEO_DURATION_SECONDS: int = 300
    INFOGRAPHIC_WIDTH: int = 1200
    INFOGRAPHIC_HEIGHT: int = 900
    ACTIVITY_DURATION_MINUTES: int = 60
    CONCEPTS_PER_THEME: int = 5

    # Automation Settings
    UNITS_COUNT: int = 5
    THEMES_PER_UNIT: int = 3
    ELEMENTS_PER_THEME: int = 5
    MAX_RETRIES: int = 3
    RETRY_DELAYS: list = [2, 4, 8, 16]  # Exponential backoff in seconds
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 100

    # Directories
    OUTPUT_DIR: str = "output"
    LOGS_DIR: str = "logs"
    CONTENT_DIR: str = "content"
    RESOURCES_DIR: str = "resources"

    # Mode (simulation or production)
    MODE: str = "simulation"  # 'simulation' or 'production'

    # Anthropic API for content generation
    ANTHROPIC_API_KEY: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
