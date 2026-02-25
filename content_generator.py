"""Content Generation for MCU-ALTEA 150 Course"""
import json
import re
from typing import Dict, List, Optional, Any
from loguru import logger
from anthropic import Anthropic
from config import settings
from models import (
    Narrative, AcademicText, VideoScript, Infographic,
    PracticalActivity, Concept, Theme, Unit
)


class ContentGenerator:
    """Generate course content using Claude API"""

    def __init__(self):
        """Initialize content generator"""
        if settings.ANTHROPIC_API_KEY:
            self.client = Anthropic()
        else:
            logger.warning("ANTHROPIC_API_KEY not set. Content generation will use templates.")
            self.client = None

    def count_words(self, text: str) -> int:
        """Count words in text (excluding HTML tags)

        Args:
            text: Text to count

        Returns:
            int: Word count
        """
        # Remove HTML tags
        clean = re.sub(r'<[^>]+>', '', text)
        # Count words
        return len(clean.split())

    def validate_word_count(self, text: str, target: int, tolerance: int) -> tuple[bool, int]:
        """Validate word count against target

        Args:
            text: Text to validate
            target: Target word count
            tolerance: Tolerance in words

        Returns:
            tuple: (is_valid, actual_count)
        """
        count = self.count_words(text)
        is_valid = abs(count - target) <= tolerance
        return is_valid, count

    def generate_narrative(self, unit_num: int, theme_num: int,
                          theme_title: str, concepts: List[str]) -> Narrative:
        """Generate a narrative pedagógica

        Args:
            unit_num: Unit number
            theme_num: Theme number
            theme_title: Theme title
            concepts: List of concepts to integrate

        Returns:
            Narrative: Generated narrative
        """
        logger.info(f"Generating narrative for U{unit_num}.{theme_num}: {theme_title}")

        if self.client:
            prompt = f"""Genera una narrativa pedagógica siguiendo EXACTAMENTE estas especificaciones:

TEMA: Unidad {unit_num}, Tema {theme_num}: {theme_title}

REQUISITOS EXACTOS:
- Palabras: EXACTAMENTE {settings.NARRATIVE_WORDS_TARGET} palabras (tolerancia ±{settings.NARRATIVE_TOLERANCE})
- Estructura: 3 actos (Introducción → Desarrollo/Conflicto → Resolución)
- Personaje principal: Un profesional enfrentando problema real relacionado al tema
- Conceptos a integrar: {', '.join(concepts)}
- Tono: Personal, histórico, con tensión narrativa y emocional
- Párrafos: Máximo 4 oraciones seguidas
- Conclusión: Conexión explícita entre historia y aplicaciones profesionales

ESTRUCTURA REQUERIDA:
1. Introducción (Presenta personaje y contexto): ~150 palabras
2. Desarrollo (Conflicto/dilema, integra conceptos gradualmente): ~1,500 palabras
3. Resolución (Superación, aprendizajes): ~150 palabras

Genera SOLO el contenido de la narrativa sin explicaciones adicionales.

FORMATO DE RESPUESTA: Devuelve un JSON con:
{{
  "title": "Título de la narrativa",
  "character": "Nombre del personaje",
  "content": "Contenido completo de la narrativa...",
  "concepts_integrated": {concepts},
  "word_count": número de palabras
}}"""

            try:
                response = self.client.messages.create(
                    model="claude-opus-4-6",
                    max_tokens=3000,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                result_text = response.content[0].text
                # Parse JSON from response
                json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group())
                    narrative = Narrative(
                        title=data.get("title", f"Narrativa U{unit_num}.{theme_num}"),
                        character=data.get("character", "Profesional"),
                        content=data.get("content", ""),
                        concepts_integrated=data.get("concepts_integrated", concepts),
                        words=self.count_words(data.get("content", ""))
                    )
                    logger.info(f"Generated narrative with {narrative.words} words")
                    return narrative
            except Exception as e:
                logger.error(f"Error generating narrative with API: {e}")

        # Fallback template-based generation
        return self._generate_narrative_template(unit_num, theme_num, theme_title, concepts)

    def _generate_narrative_template(self, unit_num: int, theme_num: int,
                                    theme_title: str, concepts: List[str]) -> Narrative:
        """Generate narrative using template (fallback)"""
        template = f"""# Narrativa Pedagógica: {theme_title}

## {theme_title}

El último día en el aula 302, la Profesora Elena Martínez se encontraba de pie frente a sus treinta estudiantes,
observando sus rostros con la mezcla de nostalgia y esperanza que solo genera una transición importante.
Durante quince años, estas aulas habían sido su hogar profesional, el espacio donde sus palabras cobraban vida,
donde podía leer en tiempo real la comprensión en los ojos de sus alumnos.

Pero hoy era diferente. La pandemia había acelerado lo inevitable: la transformación digital de la educación.
Mientras revisaba sus notas de clase manuscritas, Elena se enfrentaba a una pregunta que la había mantenido
despierta varias noches: ¿Cómo podría mantener la calidez del aula física en un ecosistema digital?
¿Podría la distancia transaccional ser realmente compensada por la tecnología?

Los conceptos que había aprendido en la capacitación obligatoria —{concepts[0]}, {concepts[1]}, {concepts[2]}—
resonaban en su mente, pero parecían abstractos, lejanos de la realidad de sus estudiantes.

Sin embargo, conforme los días avanzaban y Elena comenzaba a diseñar su primer curso virtual,
descubrió algo inesperado. No era la tecnología la que transformaba la educación, sino la intención pedagógica.
La {concepts[3]} no buscaba reemplazar al profesor, sino amplificar su capacidad de conexión.
El {concepts[4]} no era una limitación, sino una oportunidad para diseñar interacciones más reflexivas.

Elena comprendió que la enseñanza virtual no significaba abandonar lo que había construido en el aula 302.
Significaba evolucionar, adaptarse, mantener la esencia del aprendizaje mientras navegaba nuevas aguas.
Y así, con determinación renovada, Elena comenzó su viaje hacia la transformación digital de su práctica docente."""

        narrative = Narrative(
            title=f"Narrativa: {theme_title}",
            character="Elena Martínez",
            content=template,
            concepts_integrated=concepts,
            words=self.count_words(template)
        )
        logger.info(f"Generated template narrative with {narrative.words} words")
        return narrative

    def generate_academic_text(self, unit_num: int, theme_num: int,
                              theme_title: str, concepts: List[str]) -> AcademicText:
        """Generate academic text

        Args:
            unit_num: Unit number
            theme_num: Theme number
            theme_title: Theme title
            concepts: List of concepts

        Returns:
            AcademicText: Generated academic text
        """
        logger.info(f"Generating academic text for U{unit_num}.{theme_num}")

        if self.client:
            prompt = f"""Genera un texto académico riguroso siguiendo EXACTAMENTE estas especificaciones:

TEMA: {theme_title}

REQUISITOS EXACTOS:
- Palabras: EXACTAMENTE {settings.ACADEMIC_WORDS_TARGET} palabras (tolerancia ±{settings.ACADEMIC_TOLERANCE})
- Conceptos a desarrollar: {', '.join(concepts)}
- Estructura: Introducción (200 pal) + Desarrollo (1,400 pal) + Conclusión (300 pal)
- Tono: Formal, académico, apropiado para nivel Maestría
- Párrafos: Máximo 3 oraciones seguidas
- Headings: Usa ## para secciones principales, ### para subsecciones
- Referencias: Incluir citas a autores reconocidos (Moore, Piaget, Vygotsky, Siemens, etc.)
- Aplicación: Vínculos explícitos a educación virtual

FORMATO DE RESPUESTA:
Devuelve un JSON con:
{{
  "title": "Título del texto",
  "content": "Contenido completo con markdown heading...",
  "word_count": número,
  "references": ["Autor1", "Autor2", ...]
}}"""

            try:
                response = self.client.messages.create(
                    model="claude-opus-4-6",
                    max_tokens=4000,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                result_text = response.content[0].text
                json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group())
                    academic = AcademicText(
                        title=data.get("title", f"Texto Académico U{unit_num}.{theme_num}"),
                        content=data.get("content", ""),
                        concepts_count=len(concepts),
                        references=data.get("references", []),
                        words=self.count_words(data.get("content", "")),
                        headings={"h2": 5, "h3": 10}
                    )
                    logger.info(f"Generated academic text with {academic.words} words")
                    return academic
            except Exception as e:
                logger.error(f"Error generating academic text with API: {e}")

        # Fallback
        return self._generate_academic_text_template(unit_num, theme_num, theme_title, concepts)

    def _generate_academic_text_template(self, unit_num: int, theme_num: int,
                                        theme_title: str, concepts: List[str]) -> AcademicText:
        """Generate academic text using template"""
        template = f"""## {theme_title}

### Introducción

La educación en el siglo XXI enfrenta transformaciones sin precedentes. Los conceptos de {concepts[0]},
{concepts[1]}, y {concepts[2]} representan marcos teóricos fundamentales para comprender la complejidad
de los entornos educativos contemporáneos. Esta sección examina cómo estos constructos se entrelazan
con los desafíos y oportunidades de la educación virtual.

### {concepts[0]}

{concepts[0]} representa un aspecto central de la teoría educativa moderna. La investigación de Moore (1991)
estableció que la distancia educativa no es meramente física, sino psicológica y comunicativa. En contextos
virtuales, esta dimensión adquiere relevancia particular, ya que requiere diseño intencional de interacciones
que cierren la brecha entre docente y estudiante.

### {concepts[1]}

{concepts[1]} proporciona un marco para entender cómo los estudiantes construyen significado en ambientes
de aprendizaje. Según Piaget (1954), el aprendizaje activo implica interacción constante entre el individuo
y su entorno. En educación virtual, esto significa crear experiencias donde el estudiante es protagonista
de su construcción de conocimiento.

### {concepts[2]}

{concepts[2]} enfatiza la importancia de las interacciones sociales en el aprendizaje. Vygotsky (1978)
propuso que el aprendizaje es fundamentalmente un proceso social, mediado por la cultura y el lenguaje.
Las plataformas virtuales ofrecen nuevas posibilidades para estas interacciones, aunque requieren
diseño cuidadoso para ser efectivas.

### Síntesis y Aplicación

La integración de estos conceptos en diseño instruccional virtual demanda un equilibrio entre pedagogía
fundamentada y pragmatismo tecnológico. Profesionales educativos deben considerar cómo {concepts[3]}
y {concepts[4]} se manifiestan en sus contextos específicos, adaptando principios generales a realidades
particulares.

### Conclusión

La comprensión profunda de estos marcos teóricos permite a diseñadores instruccionales crear experiencias
educativas más efectivas, accesibles y transformadoras en contextos virtuales."""

        academic = AcademicText(
            title=f"Texto Académico: {theme_title}",
            content=template,
            concepts_count=len(concepts),
            references=["Moore, M. G. (1991)", "Piaget, J. (1954)", "Vygotsky, L. S. (1978)"],
            words=self.count_words(template),
            headings={"h2": 1, "h3": 5}
        )
        logger.info(f"Generated template academic text with {academic.words} words")
        return academic

    def generate_video_script(self, unit_num: int, theme_num: int,
                             theme_title: str, concepts: List[str]) -> VideoScript:
        """Generate video script

        Args:
            unit_num: Unit number
            theme_num: Theme number
            theme_title: Theme title
            concepts: List of concepts

        Returns:
            VideoScript: Generated video script
        """
        logger.info(f"Generating video script for U{unit_num}.{theme_num}")

        if self.client:
            prompt = f"""Genera un guion de video educativo siguiendo EXACTAMENTE estas especificaciones:

TEMA: {theme_title}
CONCEPTOS: {', '.join(concepts[:3])}

REQUISITOS EXACTOS:
- Palabras: EXACTAMENTE {settings.VIDEO_SCRIPT_WORDS_TARGET} palabras (tolerancia ±{settings.VIDEO_SCRIPT_TOLERANCE})
- Duración: 5 minutos (conversacional ≈ 190 palabras/minuto)
- Estructura: INTRO (30s) + DESARROLLO (3.5 min, 2-3 conceptos) + CIERRE (30s)
- Tono: Conversacional, directo, amigable
- Ejemplos: Mínimo 2-3 ejemplos concretos
- Visuals: Mencionar específicamente [VISUAL]: descripción de animación/gráfico

FORMATO:
[NARRACIÓN]: texto conversacional
[VISUAL]: descripción de lo que se ve en pantalla
[NARRACIÓN]: continúa...

RESPUESTA JSON:
{{
  "title": "Título del video",
  "script": "Contenido con [NARRACIÓN] y [VISUAL]...",
  "word_count": número,
  "visual_count": número de visuals,
  "sections": ["INTRO", "DESARROLLO", "CIERRE"]
}}"""

            try:
                response = self.client.messages.create(
                    model="claude-opus-4-6",
                    max_tokens=2500,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                result_text = response.content[0].text
                json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group())
                    video = VideoScript(
                        title=data.get("title", f"Video U{unit_num}.{theme_num}"),
                        content=data.get("script", ""),
                        words=self.count_words(data.get("script", "")),
                        duration_minutes=5.0,
                        concepts_count=min(3, len(concepts)),
                        examples_count=2,
                        visuals_count=data.get("visual_count", 3),
                        sections=data.get("sections", [])
                    )
                    logger.info(f"Generated video script with {video.words} words")
                    return video
            except Exception as e:
                logger.error(f"Error generating video script with API: {e}")

        # Fallback
        return self._generate_video_script_template(unit_num, theme_num, theme_title, concepts)

    def _generate_video_script_template(self, unit_num: int, theme_num: int,
                                       theme_title: str, concepts: List[str]) -> VideoScript:
        """Generate video script using template"""
        template = f"""[NARRACIÓN]: Hola, soy tu guía en este viaje de transformación educativa.
Hoy exploraremos cómo {concepts[0].lower()} puede revolucionar tu práctica docente.
[VISUAL]: Pantalla con título: "{theme_title}" y animación de transformación

[NARRACIÓN]: En los últimos años, los educadores enfrentamos un dilema cada vez más común:
¿cómo mantenemos la calidad y autenticidad de nuestro enseñanza mientras navegamos
espacios cada vez más virtuales? La respuesta radica en comprender algunos conceptos clave.

[VISUAL]: Animación mostrando 3 conceptos clave con iconos representativos

[NARRACIÓN]: Primero, consideremos {concepts[0]}. Este concepto, fundamental en educación,
reconoce que la mera distancia física no define la brecha educativa. Lo que realmente importa
es cómo diseñamos las interacciones para cerrar esa brecha psicológica y comunicativa.

[VISUAL]: Gráfico mostrando "distancia física" vs "distancia transaccional" con ejemplos

[NARRACIÓN]: Segundo, {concepts[1]} nos propone que el aprendizaje verdadero es activo.
No es el docente transmitiendo información al estudiante, sino el estudiante construyendo
significado a través de la interacción, la reflexión y la experiencia.

[VISUAL]: Video de ejemplo mostrando estudiantes interactuando en plataforma virtual

[NARRACIÓN]: Tercero, {concepts[2]} enfatiza la importancia de las redes y conexiones.
En educación virtual, estas conexiones no son solo entre personas, sino también entre
recursos, ideas y comunidades de práctica global.

[VISUAL]: Mapa de red expandiendo con conexiones entre nodos

[NARRACIÓN]: Lo crucial es integrar estos conceptos en tu diseño instruccional.
No es tecnología por tecnología, sino pedagogía fundamentada, mediada estratégicamente
por herramientas digitales que amplifican nuestra capacidad educativa.

[VISUAL]: Ciclo de diseño instruccional mostrando integración de conceptos

[NARRACIÓN]: Ahora que entiendes la base teórica, ¿estás listo para transformar tu curso?
En el siguiente módulo aplicaremos estos principios a la creación de contenido real.
[VISUAL]: Fade to black con texto: "Próximo: Aplicación práctica"
"""

        video = VideoScript(
            title=f"Video: {theme_title}",
            content=template,
            words=self.count_words(template),
            duration_minutes=5.0,
            concepts_count=min(3, len(concepts)),
            examples_count=3,
            visuals_count=8,
            sections=["INTRO", "DESARROLLO", "CIERRE"]
        )
        logger.info(f"Generated template video script with {video.words} words")
        return video

    def generate_key_concepts(self, theme_title: str, concepts: List[str]) -> List[Concept]:
        """Generate concept definitions

        Args:
            theme_title: Theme title
            concepts: List of concept terms

        Returns:
            List[Concept]: Generated concepts with definitions
        """
        logger.info(f"Generating key concepts for: {theme_title}")

        concept_list = []
        for term in concepts:
            definition = self._get_concept_definition(term)
            concept_list.append(Concept(term=term, definition=definition))

        return concept_list

    def _get_concept_definition(self, term: str) -> str:
        """Get concept definition"""
        definitions = {
            "Distancia transaccional": "Brecha psicológica y comunicativa entre docente y estudiante en educación a distancia",
            "Constructivismo digital": "Construcción activa de conocimiento en entornos virtuales mediante interacción reflexiva",
            "Conectivismo": "Aprendizaje como construcción de redes de conexiones entre personas, recursos e ideas",
            "Aprendizaje asincrónico": "Diseño flexible de experiencias educativas con puntos de sincronización estratégicamente ubicados",
            "Ecosistema de aprendizaje": "Sistema integrado e interdependiente de elementos educativos que trabajan sinérgicamente",
            "Zona de Desarrollo Próximo": "Espacio entre lo que un estudiante puede hacer solo y lo que puede hacer con apoyo",
            "IA Generativa": "Sistemas que crean contenido nuevo basados en patrones de datos masivos mediante redes neuronales",
            "Curación Crítica": "Evaluación, verificación, corrección y enriquecimiento sistemático de contenido generado por IA",
        }
        return definitions.get(term, f"Concepto pedagógico fundamental en educación virtual: {term}")

    def generate_practical_activity(self, unit_num: int, theme_num: int,
                                   theme_title: str) -> PracticalActivity:
        """Generate practical activity

        Args:
            unit_num: Unit number
            theme_num: Theme number
            theme_title: Theme title

        Returns:
            PracticalActivity: Generated activity
        """
        logger.info(f"Generating practical activity for U{unit_num}.{theme_num}")

        template = f"""## Auditoría Pedagógica Interactiva

### Objetivo
Aplicar los conceptos clave de este tema analizando críticamente un curso virtual existente
e identificando oportunidades de mejora basadas en principios pedagógicos rigurosos.

### Instrucciones

#### Parte 1: Selección de Curso (10 minutos)
Selecciona un curso virtual de tu institución o del repositorio recomendado.
Completa la siguiente tabla de identificación básica del curso.

#### Parte 2: Análisis Estructurado (25 minutos)
Completa la tabla de análisis evaluando cada dimensión:
- Alineamiento pedagógico
- Diseño de interacciones
- Accesibilidad y claridad
- Evidencia de constructo teórico
- Oportunidades de mejora

#### Parte 3: Reflexión Crítica (15 minutos)
Escribe una reflexión de 150-200 palabras respondiendo:
1. ¿Qué fortalezas pedagógicas identificaste?
2. ¿Qué limitaciones observaste?
3. ¿Cómo aplicarías conceptos de este tema para mejorar el curso?

#### Parte 4: Propuesta de Mejora (10 minutos)
Diseña 2-3 intervenciones específicas basadas en los conceptos del tema.

### Rúbrica de Evaluación

| Criterio | Excepcional (5) | Competente (4) | Desarrollando (3) | Inicial (1) |
|----------|-----------------|----------------|------------------|------------|
| **Análisis completo** | 5+ elementos analizados con profundidad | 4 elementos analizados | 2-3 elementos | 1 o menos |
| **Fundamentación teórica** | Vincula explícitamente a 3+ conceptos | Vincula a 2 conceptos | Vincula a 1 concepto | Sin fundamentación |
| **Propuestas de mejora** | 3+ propuestas concretas y fundamentadas | 2 propuestas concretas | 1 propuesta general | Sin propuestas |
| **Reflexión crítica** | Análisis profundo y balanced | Análisis razonado | Observaciones superficiales | Reflexión mínima |
| **Claridad y presentación** | Excelente | Buena | Aceptable | Necesita mejora |

### Entregables Esperados
1. Tabla de análisis completa
2. Reflexión de 150-200 palabras
3. 2-3 propuestas de mejora fundamentadas
4. Evidencia de auto-evaluación

### Tiempo Total Estimado: 60 minutos
"""

        activity = PracticalActivity(
            title=f"Actividad Práctica: {theme_title}",
            content=template,
            duration_minutes=60,
            components=[
                "Selección y análisis de curso existente",
                "Evaluación estructurada contra criterios pedagógicos",
                "Reflexión crítica comparativa",
                "Diseño de propuestas de mejora"
            ],
            rubric_criteria=5,
            deliverables=[
                "Tabla de análisis completada",
                "Reflexión de 150-200 palabras",
                "Propuestas de mejora específicas"
            ],
            success_criteria=[
                "Identifica evidencia de conceptos en curso analizado",
                "Propone mejoras concretas y fundamentadas",
                "Reflexión demuestra comprensión profunda",
                "Análisis es equilibrado (fortalezas y limitaciones)",
                "Vinculación explícita a teoría educativa"
            ],
            words=self.count_words(template)
        )
        logger.info(f"Generated practical activity: {activity.title}")
        return activity
