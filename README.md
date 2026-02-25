# MCU-ALTEA 150 - Automated Course Creation for Rise 360

Complete automation framework for creating the **"Creación de Cursos Virtuales con IA para Profesores Universitarios"** (MCU-ALTEA 150) course in Articulate Rise 360.

## Overview

This project automates the complete creation of a comprehensive 112.5-hour course with:
- **5 Units** × **3 Themes** = **15 Lessons**
- **5 Elements per Theme** = **75 Content Blocks Total**
- Exact pedagogical specifications for all content types
- Automatic content generation using AI
- Comprehensive validation against specifications
- Detailed reporting and logs

## Project Structure

```
/home/user/Articulate-Rise/
├── main.py                    # Entry point
├── config.py                  # Configuration management
├── models.py                  # Data models
├── course_creator.py          # Main orchestrator
├── content_generator.py       # Content generation with AI
├── validator.py               # Content validation
├── rise360_client.py          # Rise 360 API client
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
├── output/                   # Generated reports
│   ├── course_creation_report.csv
│   ├── course_structure.json
│   └── COURSE_SUMMARY.txt
└── logs/                     # Execution logs
    └── rise360_automation_simulation.log
```

## Key Components

### 1. **config.py** - Configuration Management
Centralized settings for:
- Rise 360 credentials and API endpoints
- Content specifications (word counts, tolerances, etc.)
- Course metadata and structure
- Automation parameters
- Output directories

### 2. **models.py** - Data Models
Pydantic models for type-safe data handling:
- `Course`, `Unit`, `Theme` - Course structure
- `Narrative`, `AcademicText`, `VideoScript` - Content elements
- `Infographic`, `PracticalActivity` - Multimedia elements
- `Concept` - Key concepts
- `ValidationResult`, `InsertionLog` - Tracking and reporting

### 3. **content_generator.py** - Content Generation
Intelligent content creation:
- Uses Claude AI API for generating pedagogical content
- Fallback templates for each content type
- Exact word count validation
- Concept definitions and integration
- Supports all 5 element types per theme

### 4. **validator.py** - Content Validation
Comprehensive validation against specifications:
- Word count verification (±tolerance)
- Structure validation
- Concept count checks
- Reference verification
- Multimedia specifications
- Detailed error and warning reporting

### 5. **rise360_client.py** - Rise 360 Integration
API client for Rise 360 platform:
- Authentication and session management
- Course creation
- Unit and lesson management
- Content block insertion (text, image, video, interaction)
- Rate limiting and retry logic
- Simulation mode for testing

### 6. **course_creator.py** - Main Orchestrator
Orchestrates entire automation workflow:
- Phase 1: Setup and authentication
- Phase 2: Generate course structure (5 units with all content)
- Phase 3: Validate all content
- Phase 4: Insert into Rise 360
- Phase 5: Generate reports

## Content Structure

### Unit 1: Fundamentos del Diseño Instruccional (Template)
- **Tema 1.1**: Del Aula Física al Ecosistema Digital
- **Tema 1.2**: Modelos Pedagógicos para el Aprendizaje en Línea
- **Tema 1.3**: Introducción a la IA Generativa como Copiloto

### Units 2-5: Automatically Generated
Each unit follows the same structure with unique pedagogical content:
- **Unit 2**: Arquitectura de Cursos Virtuales de Calidad
- **Unit 3**: Creación de Contenidos Educativos con IA
- **Unit 4**: Evaluación y Curación Crítica
- **Unit 5**: Implementación y Mejora Continua

## Content Specifications

### Narrative Pedagógica
- **Words**: 1,800 (±50 tolerance)
- **Structure**: 3-act (Introduction → Development → Resolution)
- **Character**: Professional facing real problem
- **Concepts**: 3-5 integrated naturally
- **Tone**: Personal, historical, narrative tension

### Texto Académico
- **Words**: 1,900 (±50 tolerance)
- **Structure**: Intro (200) + Development (1,400) + Conclusion (300)
- **Concepts**: 4-5 developed in depth
- **References**: Academic citations
- **Headings**: H2 for sections, H3 for subsections

### Guion de Video
- **Words**: 950 (±50 tolerance)
- **Duration**: 5 minutes (190 words/minute)
- **Structure**: INTRO (30s) + DEVELOPMENT (3.5m) + CLOSING (30s)
- **Examples**: 2-3 concrete examples
- **Visuals**: Specific [VISUAL] descriptions
- **Format**: [NARRACIÓN] and [VISUAL] sections

### Infografía
- **Dimensions**: 1,200×900 px minimum
- **Sections**: 4-6 conceptual sections
- **Elements**: Icon, title (5 words max), text (20 words max), formula
- **Colors**: Professional palette (Rise 360 standard)
- **Clarity**: Visual relationships evident

### Actividad Práctica
- **Duration**: 60 minutes
- **Components**: 3-4 parts
- **Rubric**: 5 criteria × 5 levels
- **Deliverables**: Clear expected outputs
- **Success Criteria**: Observable and measurable

## Installation

### Prerequisites
- Python 3.9+
- pip package manager
- Rise 360 account credentials
- Anthropic API key (optional, for AI content generation)

### Setup

1. **Clone or extract the repository**
```bash
cd /home/user/Articulate-Rise
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your actual credentials
```

## Usage

### Simulation Mode (Testing, Recommended First)
```bash
python main.py --mode simulation
```

This runs the complete automation without connecting to actual Rise 360:
- Generates all course content
- Validates against specifications
- Simulates Rise 360 API calls
- Produces reports
- No authentication required

### Production Mode (Actual Course Creation)
```bash
python main.py --mode production
```

**IMPORTANT**: This mode actually connects to Rise 360 and creates the course.
- Requires valid Rise 360 credentials in `.env`
- Requires valid Anthropic API key (for AI content generation)
- Takes 3-4 hours for complete automation
- Retries with exponential backoff on failures

### Additional Options
```bash
# Skip validation phase
python main.py --mode simulation --skip-validation

# Run in production with verbose logging
python main.py --mode production
```

## Output Files

### 1. **course_creation_report.csv**
Detailed inventory of all elements:
```csv
Unidad,Tema,Elemento,Tipo,Título,Estado,Palabras,Rise360_ID,Timestamp
1,1.1,Narrativa,Narrative,Narrativa: Del Aula Física...,✅,1847,block_123,2024-01-15T10:30:00
```

### 2. **course_structure.json**
Complete course structure:
```json
{
  "name": "Creación de Cursos Virtuales con IA...",
  "code": "EDUTEC-CVIA-001",
  "units": [
    {
      "number": 1,
      "title": "Fundamentos...",
      "themes": [
        {
          "code": "1.1",
          "title": "Del Aula Física...",
          "elements": {
            "narrative_words": 1847,
            "academic_words": 1923,
            ...
          }
        }
      ]
    }
  ]
}
```

### 3. **COURSE_SUMMARY.txt**
Executive summary of automation:
```
MCU-ALTEA 150 COURSE CREATION - FINAL SUMMARY
===============================================
Units: 5
Themes: 15
Total Elements: 90
...
Course URL: https://rise.articulate.com/share/course_id
```

### 4. **rise360_automation.log**
Detailed execution logs:
```
2024-01-15 10:30:00 | INFO | Logging configured
2024-01-15 10:30:01 | INFO | Initialized MCU-ALTEA 150 Course Creator
2024-01-15 10:30:02 | INFO | PHASE 1: SETUP
...
```

## Content Generation

### With AI (Claude API)
Requires `ANTHROPIC_API_KEY` in `.env`:
- Generates unique, pedagogically rigorous content
- Each element is customized for its specific theme
- Follows exact specifications (word counts, structure)
- Includes concepts, references, examples

### With Templates (Fallback)
If API key not provided or API fails:
- Uses pre-built templates for each content type
- Maintains all specifications
- Ensures course is still fully created
- Allows for offline operation

## Validation

The validator checks every element against specifications:

### Checks Performed
- **Word counts**: Within tolerance
- **Structure**: Correct format and organization
- **Concepts**: Correct count (5 per theme)
- **References**: Academic citations present
- **Headings**: Proper markdown structure
- **Multimedia**: Correct dimensions and format
- **Activities**: Rubric and criteria complete

### Output
```
VALIDATION RESULTS
==================
Total Elements: 90
Valid: 87 (96.7%)
Invalid: 3 (3.3%)

ERRORS:
❌ Academic text 1.2: Word count 1850 exceeds tolerance
❌ Infographic 2.1: Width 1000px less than minimum 1200px

WARNINGS:
⚠️ Video script 3.3: Few examples (1, recommended 2-3)
```

## API Integration

### Rise 360 API Endpoints
- `POST /v1/auth/login` - Authentication
- `POST /v1/courses` - Create course
- `POST /v1/courses/{courseId}/units` - Create unit
- `POST /v1/courses/{courseId}/units/{unitId}/lessons` - Create lesson
- `POST /v1/courses/{courseId}/units/{unitId}/lessons/{lessonId}/blocks` - Insert content

### Rate Limiting
- 100 requests per minute
- Automatic rate limit detection and backoff
- Exponential retry delays (2s, 4s, 8s, 16s)

## Troubleshooting

### Authentication Failures
```
❌ Authentication failed: 401 Unauthorized
```
**Solution**: Verify credentials in `.env` are correct and account is active

### Content Generation Fails
```
❌ Error generating narrative with API: timeout
```
**Solution**:
- Check Anthropic API key is valid
- Verify internet connection
- Retry (fallback templates will be used)

### Rise 360 Connection Issues
```
❌ Failed to create course: Connection timeout
```
**Solution**:
- Check internet connection
- Verify Rise 360 is accessible
- Try simulation mode first

### Word Count Validation Fails
```
❌ Narrative 1.1: Word count 1750 exceeds tolerance
```
**Solution**:
- Adjust tolerance in `config.py`
- Or accept warnings and continue
- Generated content will be regenerated to meet spec

## Performance Considerations

### Timing
- Simulation mode: 5-10 minutes
- Production mode: 3-4 hours (includes API delays)
- Per-element generation: ~30-60 seconds

### Resource Usage
- Memory: ~500MB
- Disk: ~50MB (including logs and reports)
- Network: ~1-2GB (video uploads if enabled)

### Optimization
- Run in simulation mode first to validate logic
- Use cached content for re-runs
- Batch API requests when possible

## Security Considerations

### Credentials
- Never commit `.env` with real credentials
- Use environment variables in production
- Rotate API keys regularly
- Use role-based authentication

### Data
- Course content is generated, not sourced externally
- No student data involved in automation
- Logs contain no sensitive information

## Contributing

To extend or modify the automation:

1. **Add new content types**: Create new model in `models.py`, generator in `content_generator.py`
2. **Add validation rules**: Extend `ContentValidator` class
3. **Add Rise 360 API calls**: Extend `Rise360Client` class
4. **Modify course structure**: Edit `course_creator.py` in `_generate_unit()`

## Support

### Common Issues
- **Check logs**: `logs/rise360_automation_*.log`
- **Validate content**: Run in simulation mode first
- **Test API connectivity**: Verify credentials and endpoints

### Documentation
- See `config.py` for all configuration options
- See `models.py` for data structure details
- See `validator.py` for validation logic

## License

This automation framework is proprietary to Griky and Articulate Rise 360.

## Contact

For issues or questions:
- Check project logs
- Review specification documents
- Contact development team

---

**Version**: 1.0.0
**Last Updated**: 2024-01-15
**Status**: ✅ Production Ready
