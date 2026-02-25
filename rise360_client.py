"""Rise 360 API Client for Course Creation Automation"""
import requests
import time
from typing import Optional, Dict, Any
from loguru import logger
from config import settings
from models import BlockType


class Rise360Client:
    """Client for interacting with Rise 360 API"""

    def __init__(self, email: str, password: str, base_url: str = None, mode: str = "simulation"):
        """Initialize Rise 360 client

        Args:
            email: Rise 360 account email
            password: Rise 360 account password
            base_url: Base URL for Rise 360 API
            mode: 'simulation' or 'production'
        """
        self.email = email
        self.password = password
        self.base_url = base_url or settings.RISE_API_URL
        self.mode = mode
        self.session = requests.Session()
        self.auth_token: Optional[str] = None
        self.course_id: Optional[str] = None
        self.request_count = 0
        self.rate_limit_reset = 0

    def authenticate(self) -> bool:
        """Authenticate with Rise 360

        Returns:
            bool: True if authentication successful
        """
        if self.mode == "simulation":
            logger.info("SIMULATION MODE: Skipping authentication")
            self.auth_token = "mock_token_simulation"
            return True

        try:
            logger.info(f"Authenticating with Rise 360 as {self.email}")
            response = self.session.post(
                f"{self.base_url}/v1/auth/login",
                json={"email": self.email, "password": self.password},
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            self.auth_token = data.get("token")
            logger.info("Authentication successful")
            return True
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return False

    def _check_rate_limit(self) -> None:
        """Check and enforce rate limiting"""
        current_time = time.time()
        if self.request_count >= settings.RATE_LIMIT_REQUESTS_PER_MINUTE:
            sleep_time = max(0, 60 - (current_time - self.rate_limit_reset))
            if sleep_time > 0:
                logger.warning(f"Rate limit approaching. Sleeping {sleep_time}s")
                time.sleep(sleep_time)
            self.request_count = 0
            self.rate_limit_reset = current_time

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication"""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "MCU-ALTEA-Automation/1.0"
        }
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        return headers

    def create_course(self, course_name: str, course_code: str, duration_hours: float) -> Optional[str]:
        """Create a new course in Rise 360

        Args:
            course_name: Name of the course
            course_code: Course code
            duration_hours: Duration in hours

        Returns:
            str: Course ID if successful, None otherwise
        """
        if self.mode == "simulation":
            self.course_id = f"course_sim_{int(time.time())}"
            logger.info(f"SIMULATION: Created course {self.course_id}")
            return self.course_id

        try:
            self._check_rate_limit()
            payload = {
                "title": course_name,
                "description": f"Código: {course_code}",
                "duration": duration_hours,
                "language": settings.COURSE_LANGUAGE
            }
            response = self.session.post(
                f"{self.base_url}/v1/courses",
                json=payload,
                headers=self._get_headers(),
                timeout=30
            )
            response.raise_for_status()
            self.course_id = response.json().get("id")
            logger.info(f"Course created: {self.course_id}")
            self.request_count += 1
            return self.course_id
        except Exception as e:
            logger.error(f"Failed to create course: {e}")
            return None

    def create_unit(self, course_id: str, unit_number: int, unit_title: str) -> Optional[str]:
        """Create a unit within a course

        Args:
            course_id: ID of the parent course
            unit_number: Unit number (1-5)
            unit_title: Title of the unit

        Returns:
            str: Unit ID if successful
        """
        if self.mode == "simulation":
            unit_id = f"unit_sim_{course_id}_{unit_number}"
            logger.debug(f"SIMULATION: Created unit {unit_id}")
            return unit_id

        try:
            self._check_rate_limit()
            payload = {
                "title": unit_title,
                "order": unit_number,
                "description": f"Unit {unit_number}"
            }
            response = self.session.post(
                f"{self.base_url}/v1/courses/{course_id}/units",
                json=payload,
                headers=self._get_headers(),
                timeout=30
            )
            response.raise_for_status()
            unit_id = response.json().get("id")
            logger.info(f"Unit created: {unit_id}")
            self.request_count += 1
            return unit_id
        except Exception as e:
            logger.error(f"Failed to create unit: {e}")
            return None

    def create_lesson(self, course_id: str, unit_id: str, theme_number: int,
                     theme_title: str) -> Optional[str]:
        """Create a lesson (theme) within a unit

        Args:
            course_id: ID of the parent course
            unit_id: ID of the parent unit
            theme_number: Theme number within unit
            theme_title: Title of the theme

        Returns:
            str: Lesson ID if successful
        """
        if self.mode == "simulation":
            lesson_id = f"lesson_sim_{unit_id}_{theme_number}"
            logger.debug(f"SIMULATION: Created lesson {lesson_id}")
            return lesson_id

        try:
            self._check_rate_limit()
            payload = {
                "title": theme_title,
                "order": theme_number,
                "description": f"Theme {theme_number}"
            }
            response = self.session.post(
                f"{self.base_url}/v1/courses/{course_id}/units/{unit_id}/lessons",
                json=payload,
                headers=self._get_headers(),
                timeout=30
            )
            response.raise_for_status()
            lesson_id = response.json().get("id")
            logger.info(f"Lesson created: {lesson_id}")
            self.request_count += 1
            return lesson_id
        except Exception as e:
            logger.error(f"Failed to create lesson: {e}")
            return None

    def insert_text_block(self, course_id: str, unit_id: str, lesson_id: str,
                         title: str, content: str, order: int = 1) -> Optional[str]:
        """Insert a text block into a lesson

        Args:
            course_id: ID of the course
            unit_id: ID of the unit
            lesson_id: ID of the lesson
            title: Block title
            content: HTML content
            order: Order within lesson

        Returns:
            str: Block ID if successful
        """
        if self.mode == "simulation":
            block_id = f"block_sim_text_{lesson_id}_{order}"
            logger.debug(f"SIMULATION: Inserted text block {block_id}")
            return block_id

        try:
            self._check_rate_limit()
            payload = {
                "type": "text",
                "title": title,
                "content": content,
                "order": order
            }
            response = self.session.post(
                f"{self.base_url}/v1/courses/{course_id}/units/{unit_id}/lessons/{lesson_id}/blocks",
                json=payload,
                headers=self._get_headers(),
                timeout=30
            )
            response.raise_for_status()
            block_id = response.json().get("id")
            logger.info(f"Text block inserted: {block_id}")
            self.request_count += 1
            return block_id
        except Exception as e:
            logger.error(f"Failed to insert text block: {e}")
            return None

    def insert_image_block(self, course_id: str, unit_id: str, lesson_id: str,
                          title: str, image_url: str, description: str,
                          order: int = 2) -> Optional[str]:
        """Insert an image block into a lesson

        Args:
            course_id: ID of the course
            unit_id: ID of the unit
            lesson_id: ID of the lesson
            title: Block title
            image_url: URL of the image
            description: Alt text / description
            order: Order within lesson

        Returns:
            str: Block ID if successful
        """
        if self.mode == "simulation":
            block_id = f"block_sim_image_{lesson_id}_{order}"
            logger.debug(f"SIMULATION: Inserted image block {block_id}")
            return block_id

        try:
            self._check_rate_limit()
            payload = {
                "type": "image",
                "title": title,
                "url": image_url,
                "description": description,
                "order": order
            }
            response = self.session.post(
                f"{self.base_url}/v1/courses/{course_id}/units/{unit_id}/lessons/{lesson_id}/blocks",
                json=payload,
                headers=self._get_headers(),
                timeout=30
            )
            response.raise_for_status()
            block_id = response.json().get("id")
            logger.info(f"Image block inserted: {block_id}")
            self.request_count += 1
            return block_id
        except Exception as e:
            logger.error(f"Failed to insert image block: {e}")
            return None

    def insert_video_block(self, course_id: str, unit_id: str, lesson_id: str,
                          title: str, video_url: str, order: int = 3) -> Optional[str]:
        """Insert a video block into a lesson

        Args:
            course_id: ID of the course
            unit_id: ID of the unit
            lesson_id: ID of the lesson
            title: Block title
            video_url: URL of the video
            order: Order within lesson

        Returns:
            str: Block ID if successful
        """
        if self.mode == "simulation":
            block_id = f"block_sim_video_{lesson_id}_{order}"
            logger.debug(f"SIMULATION: Inserted video block {block_id}")
            return block_id

        try:
            self._check_rate_limit()
            payload = {
                "type": "video",
                "title": title,
                "url": video_url,
                "order": order
            }
            response = self.session.post(
                f"{self.base_url}/v1/courses/{course_id}/units/{unit_id}/lessons/{lesson_id}/blocks",
                json=payload,
                headers=self._get_headers(),
                timeout=30
            )
            response.raise_for_status()
            block_id = response.json().get("id")
            logger.info(f"Video block inserted: {block_id}")
            self.request_count += 1
            return block_id
        except Exception as e:
            logger.error(f"Failed to insert video block: {e}")
            return None

    def insert_interaction_block(self, course_id: str, unit_id: str, lesson_id: str,
                                title: str, interaction_html: str, order: int = 5) -> Optional[str]:
        """Insert an interaction block into a lesson

        Args:
            course_id: ID of the course
            unit_id: ID of the unit
            lesson_id: ID of the lesson
            title: Block title
            interaction_html: HTML for the interaction
            order: Order within lesson

        Returns:
            str: Block ID if successful
        """
        if self.mode == "simulation":
            block_id = f"block_sim_interaction_{lesson_id}_{order}"
            logger.debug(f"SIMULATION: Inserted interaction block {block_id}")
            return block_id

        try:
            self._check_rate_limit()
            payload = {
                "type": "interaction",
                "title": title,
                "html": interaction_html,
                "order": order
            }
            response = self.session.post(
                f"{self.base_url}/v1/courses/{course_id}/units/{unit_id}/lessons/{lesson_id}/blocks",
                json=payload,
                headers=self._get_headers(),
                timeout=30
            )
            response.raise_for_status()
            block_id = response.json().get("id")
            logger.info(f"Interaction block inserted: {block_id}")
            self.request_count += 1
            return block_id
        except Exception as e:
            logger.error(f"Failed to insert interaction block: {e}")
            return None

    def publish_course(self) -> bool:
        """Publish the course

        Returns:
            bool: True if successful
        """
        if self.mode == "simulation":
            logger.info(f"SIMULATION: Course {self.course_id} marked as published")
            return True

        if not self.course_id:
            logger.error("No course ID set. Create course first.")
            return False

        try:
            self._check_rate_limit()
            response = self.session.patch(
                f"{self.base_url}/v1/courses/{self.course_id}",
                json={"status": "published"},
                headers=self._get_headers(),
                timeout=30
            )
            response.raise_for_status()
            logger.info(f"Course {self.course_id} published successfully")
            self.request_count += 1
            return True
        except Exception as e:
            logger.error(f"Failed to publish course: {e}")
            return False

    def get_course_url(self) -> Optional[str]:
        """Get the shareable URL for the course

        Returns:
            str: Course URL if available
        """
        if self.mode == "simulation":
            return f"{settings.RISE_BASE_URL}/share/sim_{self.course_id}"

        if not self.course_id:
            return None

        return f"{settings.RISE_BASE_URL}/share/{self.course_id}"
