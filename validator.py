"""Validation for MCU-ALTEA 150 Course Content"""
import re
from typing import List, Dict, Tuple
from datetime import datetime
from loguru import logger
from models import (
    Narrative, AcademicText, VideoScript, Infographic,
    PracticalActivity, Theme, Unit, Course, ValidationResult, BlockType
)
from config import settings


class ContentValidator:
    """Validate course content against specifications"""

    def __init__(self):
        """Initialize validator"""
        self.validation_results: List[ValidationResult] = []

    def validate_course(self, course: Course) -> Dict[str, any]:
        """Validate complete course structure

        Args:
            course: Course to validate

        Returns:
            Dict: Validation summary
        """
        logger.info("Starting comprehensive course validation...")

        issues = {
            "errors": [],
            "warnings": [],
            "total_elements": 0,
            "valid_elements": 0,
            "invalid_elements": 0
        }

        # Check units count
        if len(course.units) != settings.UNITS_COUNT:
            issues["errors"].append(
                f"Expected {settings.UNITS_COUNT} units, got {len(course.units)}"
            )

        # Validate each unit
        for unit in course.units:
            unit_result = self.validate_unit(unit)
            issues["total_elements"] += unit_result["total_elements"]
            issues["valid_elements"] += unit_result["valid_elements"]
            issues["invalid_elements"] += unit_result["invalid_elements"]
            issues["errors"].extend(unit_result["errors"])
            issues["warnings"].extend(unit_result["warnings"])

        logger.info(f"Validation complete: {issues['valid_elements']}/{issues['total_elements']} valid")
        return issues

    def validate_unit(self, unit: Unit) -> Dict[str, any]:
        """Validate a unit

        Args:
            unit: Unit to validate

        Returns:
            Dict: Validation results
        """
        logger.info(f"Validating Unit {unit.unit_number}: {unit.title}")

        issues = {
            "errors": [],
            "warnings": [],
            "total_elements": 0,
            "valid_elements": 0,
            "invalid_elements": 0
        }

        # Check themes count
        if len(unit.themes) != settings.THEMES_PER_UNIT:
            issues["errors"].append(
                f"Unit {unit.unit_number}: Expected {settings.THEMES_PER_UNIT} themes, got {len(unit.themes)}"
            )

        # Validate each theme
        for theme in unit.themes:
            theme_result = self.validate_theme(theme)
            issues["total_elements"] += theme_result["total_elements"]
            issues["valid_elements"] += theme_result["valid_elements"]
            issues["invalid_elements"] += theme_result["invalid_elements"]
            issues["errors"].extend(theme_result["errors"])
            issues["warnings"].extend(theme_result["warnings"])

        # Check additional unit content
        if not unit.synthesis:
            issues["warnings"].append(f"Unit {unit.unit_number}: Missing synthesis (300 words)")
        if not unit.integrated_project:
            issues["warnings"].append(f"Unit {unit.unit_number}: Missing integrated project (800-1000 words)")

        return issues

    def validate_theme(self, theme: Theme) -> Dict[str, any]:
        """Validate a theme

        Args:
            theme: Theme to validate

        Returns:
            Dict: Validation results
        """
        logger.debug(f"Validating Theme {theme.code}: {theme.title}")

        issues = {
            "errors": [],
            "warnings": [],
            "total_elements": 5,
            "valid_elements": 0,
            "invalid_elements": 0
        }

        # Validate narrative
        narrative_result = self.validate_narrative(theme.narrative, theme.code)
        if narrative_result["is_valid"]:
            issues["valid_elements"] += 1
        else:
            issues["invalid_elements"] += 1
            issues["errors"].extend(narrative_result["errors"])

        # Validate concepts
        concepts_result = self.validate_concepts(theme.concepts, theme.code)
        if not concepts_result["is_valid"]:
            issues["errors"].extend(concepts_result["errors"])
            issues["invalid_elements"] += 1
        else:
            issues["valid_elements"] += 1

        # Validate academic text
        academic_result = self.validate_academic_text(theme.academic_text, theme.code)
        if academic_result["is_valid"]:
            issues["valid_elements"] += 1
        else:
            issues["invalid_elements"] += 1
            issues["errors"].extend(academic_result["errors"])

        # Validate infographic
        infographic_result = self.validate_infographic(theme.infographic, theme.code)
        if infographic_result["is_valid"]:
            issues["valid_elements"] += 1
        else:
            issues["invalid_elements"] += 1
            issues["errors"].extend(infographic_result["errors"])

        # Validate video script
        video_result = self.validate_video_script(theme.video_script, theme.code)
        if video_result["is_valid"]:
            issues["valid_elements"] += 1
        else:
            issues["invalid_elements"] += 1
            issues["errors"].extend(video_result["errors"])

        # Validate activity
        activity_result = self.validate_activity(theme.activity, theme.code)
        if activity_result["is_valid"]:
            issues["valid_elements"] += 1
        else:
            issues["invalid_elements"] += 1
            issues["errors"].extend(activity_result["errors"])

        return issues

    def validate_narrative(self, narrative: Narrative, theme_code: str) -> Dict[str, any]:
        """Validate narrative element"""
        logger.debug(f"Validating narrative for {theme_code}")

        errors = []
        warnings = []

        # Check word count
        if not narrative.words:
            narrative.words = len(narrative.content.split())

        word_diff = abs(narrative.words - settings.NARRATIVE_WORDS_TARGET)
        if word_diff > settings.NARRATIVE_TOLERANCE:
            errors.append(
                f"Narrative {theme_code}: Word count {narrative.words} exceeds tolerance. "
                f"Target: {settings.NARRATIVE_WORDS_TARGET} ±{settings.NARRATIVE_TOLERANCE}"
            )

        # Check structure
        if narrative.structure != "3-act":
            warnings.append(f"Narrative {theme_code}: Unexpected structure format")

        # Check character
        if not narrative.character or len(narrative.character) < 3:
            errors.append(f"Narrative {theme_code}: Missing or invalid character name")

        # Check concepts
        if len(narrative.concepts_integrated) < 3:
            errors.append(f"Narrative {theme_code}: Should integrate 3-5 concepts, got {len(narrative.concepts_integrated)}")

        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "metrics": {
                "word_count": narrative.words,
                "word_target": settings.NARRATIVE_WORDS_TARGET,
                "concepts_count": len(narrative.concepts_integrated)
            }
        }

    def validate_concepts(self, concepts: List, theme_code: str) -> Dict[str, any]:
        """Validate key concepts"""
        logger.debug(f"Validating concepts for {theme_code}")

        errors = []

        # Check count
        if len(concepts) != settings.CONCEPTS_PER_THEME:
            errors.append(
                f"Concepts {theme_code}: Expected {settings.CONCEPTS_PER_THEME}, got {len(concepts)}"
            )

        # Check each concept
        for i, concept in enumerate(concepts):
            if not concept.term or len(concept.term) < 3:
                errors.append(f"Concepts {theme_code}: Invalid term at position {i}")
            if not concept.definition or len(concept.definition) < 10:
                errors.append(f"Concepts {theme_code}: Invalid definition for '{concept.term}'")

        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": []
        }

    def validate_academic_text(self, text: AcademicText, theme_code: str) -> Dict[str, any]:
        """Validate academic text element"""
        logger.debug(f"Validating academic text for {theme_code}")

        errors = []
        warnings = []

        # Check word count
        if not text.words:
            text.words = len(text.content.split())

        word_diff = abs(text.words - settings.ACADEMIC_WORDS_TARGET)
        if word_diff > settings.ACADEMIC_TOLERANCE:
            errors.append(
                f"Academic text {theme_code}: Word count {text.words} exceeds tolerance. "
                f"Target: {settings.ACADEMIC_WORDS_TARGET} ±{settings.ACADEMIC_TOLERANCE}"
            )

        # Check concepts count
        if text.concepts_count < 4:
            errors.append(f"Academic text {theme_code}: Should have 4-5 concepts, got {text.concepts_count}")

        # Check references
        if not text.references or len(text.references) < 3:
            warnings.append(f"Academic text {theme_code}: Few references (recommended 3+)")

        # Check headings
        if "##" not in text.content and "#" not in text.content:
            warnings.append(f"Academic text {theme_code}: No markdown headings found")

        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "metrics": {
                "word_count": text.words,
                "word_target": settings.ACADEMIC_WORDS_TARGET,
                "concepts_count": text.concepts_count,
                "references_count": len(text.references) if text.references else 0
            }
        }

    def validate_infographic(self, infographic: Infographic, theme_code: str) -> Dict[str, any]:
        """Validate infographic element"""
        logger.debug(f"Validating infographic for {theme_code}")

        errors = []
        warnings = []

        # Check dimensions
        if infographic.width_px < settings.INFOGRAPHIC_WIDTH:
            errors.append(
                f"Infographic {theme_code}: Width {infographic.width_px}px is less than minimum {settings.INFOGRAPHIC_WIDTH}px"
            )

        if infographic.height_px < settings.INFOGRAPHIC_HEIGHT:
            errors.append(
                f"Infographic {theme_code}: Height {infographic.height_px}px is less than minimum {settings.INFOGRAPHIC_HEIGHT}px"
            )

        # Check sections
        if infographic.sections_count < 4 or infographic.sections_count > 6:
            errors.append(
                f"Infographic {theme_code}: Sections count {infographic.sections_count} out of range (4-6)"
            )

        # Check elements
        if not infographic.elements or len(infographic.elements) < infographic.sections_count:
            warnings.append(f"Infographic {theme_code}: Elements list may be incomplete")

        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "metrics": {
                "width_px": infographic.width_px,
                "height_px": infographic.height_px,
                "sections_count": infographic.sections_count,
                "elements_count": len(infographic.elements) if infographic.elements else 0
            }
        }

    def validate_video_script(self, video: VideoScript, theme_code: str) -> Dict[str, any]:
        """Validate video script element"""
        logger.debug(f"Validating video script for {theme_code}")

        errors = []
        warnings = []

        # Check word count
        if not video.words:
            video.words = len(video.content.split())

        word_diff = abs(video.words - settings.VIDEO_SCRIPT_WORDS_TARGET)
        if word_diff > settings.VIDEO_SCRIPT_TOLERANCE:
            errors.append(
                f"Video script {theme_code}: Word count {video.words} exceeds tolerance. "
                f"Target: {settings.VIDEO_SCRIPT_WORDS_TARGET} ±{settings.VIDEO_SCRIPT_TOLERANCE}"
            )

        # Check duration
        if video.duration_minutes != settings.VIDEO_DURATION_MINUTES:
            warnings.append(f"Video script {theme_code}: Duration {video.duration_minutes}m, expected {settings.VIDEO_DURATION_MINUTES}m")

        # Check concepts count
        if video.concepts_count > 3:
            errors.append(f"Video script {theme_code}: Too many concepts ({video.concepts_count}), max is 3")

        # Check examples
        if video.examples_count < 2:
            warnings.append(f"Video script {theme_code}: Few examples ({video.examples_count}), recommended 2-3")

        # Check visuals
        if video.visuals_count < 2:
            errors.append(f"Video script {theme_code}: Too few visuals ({video.visuals_count}), minimum is 2")

        # Check structure
        if "[NARRACIÓN]" not in video.content or "[VISUAL]" not in video.content:
            errors.append(f"Video script {theme_code}: Missing required [NARRACIÓN] or [VISUAL] markers")

        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "metrics": {
                "word_count": video.words,
                "word_target": settings.VIDEO_SCRIPT_WORDS_TARGET,
                "duration_minutes": video.duration_minutes,
                "concepts_count": video.concepts_count,
                "examples_count": video.examples_count,
                "visuals_count": video.visuals_count
            }
        }

    def validate_activity(self, activity: PracticalActivity, theme_code: str) -> Dict[str, any]:
        """Validate practical activity element"""
        logger.debug(f"Validating activity for {theme_code}")

        errors = []
        warnings = []

        # Check duration
        if activity.duration_minutes != settings.ACTIVITY_DURATION_MINUTES:
            errors.append(f"Activity {theme_code}: Duration {activity.duration_minutes}m, expected {settings.ACTIVITY_DURATION_MINUTES}m")

        # Check components
        if len(activity.components) < 3:
            warnings.append(f"Activity {theme_code}: Few components ({len(activity.components)}), recommended 3-4")

        # Check rubric criteria
        if activity.rubric_criteria < 4:
            errors.append(f"Activity {theme_code}: Rubric has {activity.rubric_criteria} criteria, minimum is 4")

        # Check deliverables
        if len(activity.deliverables) < 1:
            errors.append(f"Activity {theme_code}: No deliverables specified")

        # Check success criteria
        if len(activity.success_criteria) < 3:
            warnings.append(f"Activity {theme_code}: Few success criteria ({len(activity.success_criteria)}), recommended 3+")

        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "metrics": {
                "duration_minutes": activity.duration_minutes,
                "components_count": len(activity.components),
                "rubric_criteria": activity.rubric_criteria,
                "deliverables_count": len(activity.deliverables),
                "success_criteria_count": len(activity.success_criteria)
            }
        }

    def generate_validation_report(self, validation_results: List[Dict]) -> str:
        """Generate human-readable validation report

        Args:
            validation_results: List of validation results

        Returns:
            str: Formatted report
        """
        report = "="*80 + "\n"
        report += "COURSE VALIDATION REPORT\n"
        report += "="*80 + "\n\n"

        total_elements = sum(r.get("total_elements", 0) for r in validation_results)
        valid_elements = sum(r.get("valid_elements", 0) for r in validation_results)
        invalid_elements = sum(r.get("invalid_elements", 0) for r in validation_results)

        report += f"SUMMARY\n"
        report += f"Total Elements: {total_elements}\n"
        report += f"Valid: {valid_elements} ({100*valid_elements/total_elements:.1f}%)\n"
        report += f"Invalid: {invalid_elements} ({100*invalid_elements/total_elements:.1f}%)\n\n"

        all_errors = []
        all_warnings = []

        for result in validation_results:
            all_errors.extend(result.get("errors", []))
            all_warnings.extend(result.get("warnings", []))

        if all_errors:
            report += "ERRORS\n"
            report += "-"*80 + "\n"
            for error in all_errors:
                report += f"❌ {error}\n"
            report += "\n"

        if all_warnings:
            report += "WARNINGS\n"
            report += "-"*80 + "\n"
            for warning in all_warnings:
                report += f"⚠️  {warning}\n"
            report += "\n"

        report += "="*80 + "\n"
        return report
