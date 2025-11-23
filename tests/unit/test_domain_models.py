"""Tests for domain models"""

from datetime import UTC, datetime

from copy_that.domain.models import (
    ColorToken,
    ExtractionJob,
    ExtractionSession,
    Project,
    TokenExport,
    TokenLibrary,
    utc_now,
)


class TestUtcNow:
    """Test utc_now helper function"""

    def test_utc_now_returns_datetime(self):
        """Test utc_now returns a datetime object"""
        result = utc_now()
        assert isinstance(result, datetime)

    def test_utc_now_is_naive_datetime(self):
        """Test utc_now returns naive datetime (for asyncpg compatibility)"""
        result = utc_now()
        # utc_now returns naive datetime for TIMESTAMP WITHOUT TIME ZONE compatibility
        assert result.tzinfo is None

    def test_utc_now_is_current_time(self):
        """Test utc_now returns approximately current time"""
        before = datetime.now(UTC).replace(tzinfo=None)
        result = utc_now()
        after = datetime.now(UTC).replace(tzinfo=None)
        assert before <= result <= after


class TestProjectModel:
    """Test Project model"""

    def test_project_creation(self):
        """Test basic project creation"""
        project = Project(name="Test Project", description="Test description")
        assert project.name == "Test Project"
        assert project.description == "Test description"

    def test_project_minimal(self):
        """Test project with only required fields"""
        project = Project(name="Minimal Project")
        assert project.name == "Minimal Project"
        assert project.description is None

    def test_project_repr(self):
        """Test project __repr__"""
        project = Project(id=1, name="Test Project")
        repr_str = repr(project)
        assert "Project" in repr_str
        assert "id=1" in repr_str
        assert "Test Project" in repr_str

    def test_project_tablename(self):
        """Test project table name"""
        assert Project.__tablename__ == "projects"


class TestExtractionJobModel:
    """Test ExtractionJob model"""

    def test_extraction_job_creation(self):
        """Test basic extraction job creation"""
        job = ExtractionJob(
            project_id=1,
            source_url="http://example.com/image.jpg",
            extraction_type="color",
        )
        assert job.project_id == 1
        assert job.source_url == "http://example.com/image.jpg"
        assert job.extraction_type == "color"

    def test_extraction_job_default_status(self):
        """Test extraction job default status"""
        job = ExtractionJob(
            project_id=1,
            source_url="http://example.com/image.jpg",
            extraction_type="color",
        )
        # Default status is set via SQLAlchemy default
        assert job.status is None or job.status == "pending"

    def test_extraction_job_with_status(self):
        """Test extraction job with explicit status"""
        job = ExtractionJob(
            project_id=1,
            source_url="http://example.com/image.jpg",
            extraction_type="color",
            status="processing",
        )
        assert job.status == "processing"

    def test_extraction_job_with_result_data(self):
        """Test extraction job with result data"""
        job = ExtractionJob(
            project_id=1,
            source_url="http://example.com/image.jpg",
            extraction_type="all",
            status="completed",
            result_data='{"colors": []}',
        )
        assert job.result_data == '{"colors": []}'

    def test_extraction_job_with_error(self):
        """Test extraction job with error message"""
        job = ExtractionJob(
            project_id=1,
            source_url="http://example.com/image.jpg",
            extraction_type="color",
            status="failed",
            error_message="Connection timeout",
        )
        assert job.error_message == "Connection timeout"

    def test_extraction_job_repr(self):
        """Test extraction job __repr__"""
        job = ExtractionJob(
            id=1,
            project_id=1,
            source_url="http://example.com/image.jpg",
            extraction_type="color",
            status="pending",
        )
        repr_str = repr(job)
        assert "ExtractionJob" in repr_str
        assert "id=1" in repr_str
        assert "color" in repr_str
        assert "pending" in repr_str

    def test_extraction_job_tablename(self):
        """Test extraction job table name"""
        assert ExtractionJob.__tablename__ == "extraction_jobs"


class TestColorTokenModel:
    """Test ColorToken model"""

    def test_color_token_creation(self):
        """Test basic color token creation"""
        token = ColorToken(
            project_id=1,
            hex="#FF5733",
            rgb="rgb(255, 87, 51)",
            name="Coral Red",
            confidence=0.95,
        )
        assert token.project_id == 1
        assert token.hex == "#FF5733"
        assert token.rgb == "rgb(255, 87, 51)"
        assert token.name == "Coral Red"
        assert token.confidence == 0.95

    def test_color_token_with_optional_fields(self):
        """Test color token with optional fields"""
        token = ColorToken(
            project_id=1,
            hex="#FF5733",
            rgb="rgb(255, 87, 51)",
            name="Coral Red",
            confidence=0.95,
            hsl="hsl(11, 100%, 60%)",
            hsv="hsv(11, 80%, 100%)",
            design_intent="error",
            category="primary",
            harmony="complementary",
            temperature="warm",
        )
        assert token.hsl == "hsl(11, 100%, 60%)"
        assert token.hsv == "hsv(11, 80%, 100%)"
        assert token.design_intent == "error"
        assert token.category == "primary"
        assert token.harmony == "complementary"
        assert token.temperature == "warm"

    def test_color_token_accessibility_fields(self):
        """Test color token accessibility fields"""
        token = ColorToken(
            project_id=1,
            hex="#FF5733",
            rgb="rgb(255, 87, 51)",
            name="Coral Red",
            confidence=0.95,
            wcag_contrast_on_white=3.5,
            wcag_contrast_on_black=8.2,
            wcag_aa_compliant_text=True,
            wcag_aaa_compliant_text=False,
            colorblind_safe=True,
        )
        assert token.wcag_contrast_on_white == 3.5
        assert token.wcag_contrast_on_black == 8.2
        assert token.wcag_aa_compliant_text is True
        assert token.wcag_aaa_compliant_text is False
        assert token.colorblind_safe is True

    def test_color_token_variants(self):
        """Test color token variant fields"""
        token = ColorToken(
            project_id=1,
            hex="#FF5733",
            rgb="rgb(255, 87, 51)",
            name="Coral Red",
            confidence=0.95,
            tint_color="#FF8A6C",
            shade_color="#CC4529",
            tone_color="#D96B52",
        )
        assert token.tint_color == "#FF8A6C"
        assert token.shade_color == "#CC4529"
        assert token.tone_color == "#D96B52"

    def test_color_token_advanced_properties(self):
        """Test color token advanced properties"""
        token = ColorToken(
            project_id=1,
            hex="#FF5733",
            rgb="rgb(255, 87, 51)",
            name="Coral Red",
            confidence=0.95,
            closest_web_safe="#FF6633",
            closest_css_named="tomato",
            delta_e_to_dominant=5.2,
            is_neutral=False,
        )
        assert token.closest_web_safe == "#FF6633"
        assert token.closest_css_named == "tomato"
        assert token.delta_e_to_dominant == 5.2
        assert token.is_neutral is False

    def test_color_token_ml_properties(self):
        """Test color token ML/CV properties"""
        token = ColorToken(
            project_id=1,
            hex="#FF5733",
            rgb="rgb(255, 87, 51)",
            name="Coral Red",
            confidence=0.95,
            kmeans_cluster_id=3,
            histogram_significance=0.85,
        )
        assert token.kmeans_cluster_id == 3
        assert token.histogram_significance == 0.85

    def test_color_token_library_fields(self):
        """Test color token library and curation fields"""
        token = ColorToken(
            project_id=1,
            hex="#FF5733",
            rgb="rgb(255, 87, 51)",
            name="Coral Red",
            confidence=0.95,
            library_id=1,
            role="primary",
            provenance='{"image_1": 0.95}',
        )
        assert token.library_id == 1
        assert token.role == "primary"
        assert token.provenance == '{"image_1": 0.95}'

    def test_color_token_count_and_prominence(self):
        """Test color token count and prominence"""
        token = ColorToken(
            project_id=1,
            hex="#FF5733",
            rgb="rgb(255, 87, 51)",
            name="Coral Red",
            confidence=0.95,
            count=5,
            prominence_percentage=25.5,
        )
        assert token.count == 5
        assert token.prominence_percentage == 25.5

    def test_color_token_repr(self):
        """Test color token __repr__"""
        token = ColorToken(
            id=1,
            project_id=1,
            hex="#FF5733",
            rgb="rgb(255, 87, 51)",
            name="Coral Red",
            confidence=0.95,
            design_intent="error",
        )
        repr_str = repr(token)
        assert "ColorToken" in repr_str
        assert "id=1" in repr_str
        assert "#FF5733" in repr_str
        assert "Coral Red" in repr_str
        assert "error" in repr_str

    def test_color_token_tablename(self):
        """Test color token table name"""
        assert ColorToken.__tablename__ == "color_tokens"


class TestExtractionSessionModel:
    """Test ExtractionSession model"""

    def test_extraction_session_creation(self):
        """Test basic extraction session creation"""
        session = ExtractionSession(
            project_id=1,
            name="Brand Guidelines - Acme Corp",
            description="Extract colors from brand assets",
        )
        assert session.project_id == 1
        assert session.name == "Brand Guidelines - Acme Corp"
        assert session.description == "Extract colors from brand assets"

    def test_extraction_session_minimal(self):
        """Test extraction session with minimal fields"""
        session = ExtractionSession(
            project_id=1,
            name="Quick Session",
        )
        assert session.name == "Quick Session"
        assert session.description is None

    def test_extraction_session_with_images(self):
        """Test extraction session with image metadata"""
        session = ExtractionSession(
            project_id=1,
            name="Multi-image Session",
            image_count=5,
            source_images='["img1.jpg", "img2.jpg", "img3.jpg", "img4.jpg", "img5.jpg"]',
        )
        assert session.image_count == 5
        assert "img1.jpg" in session.source_images

    def test_extraction_session_repr(self):
        """Test extraction session __repr__"""
        session = ExtractionSession(
            id=1,
            project_id=1,
            name="Test Session",
            image_count=3,
        )
        repr_str = repr(session)
        assert "ExtractionSession" in repr_str
        assert "id=1" in repr_str
        assert "Test Session" in repr_str
        assert "images=3" in repr_str

    def test_extraction_session_tablename(self):
        """Test extraction session table name"""
        assert ExtractionSession.__tablename__ == "extraction_sessions"


class TestTokenLibraryModel:
    """Test TokenLibrary model"""

    def test_token_library_creation(self):
        """Test basic token library creation"""
        library = TokenLibrary(
            session_id=1,
            token_type="color",
            name="Primary Colors",
        )
        assert library.session_id == 1
        assert library.token_type == "color"
        assert library.name == "Primary Colors"

    def test_token_library_with_statistics(self):
        """Test token library with statistics"""
        library = TokenLibrary(
            session_id=1,
            token_type="color",
            statistics='{"dominant_hue": "red", "color_count": 10}',
        )
        assert "dominant_hue" in library.statistics

    def test_token_library_curation(self):
        """Test token library curation fields"""
        library = TokenLibrary(
            session_id=1,
            token_type="color",
            is_curated=True,
            curation_notes="Removed duplicate grays",
        )
        assert library.is_curated is True
        assert library.curation_notes == "Removed duplicate grays"

    def test_token_library_repr(self):
        """Test token library __repr__"""
        library = TokenLibrary(
            id=1,
            session_id=2,
            token_type="color",
        )
        repr_str = repr(library)
        assert "TokenLibrary" in repr_str
        assert "id=1" in repr_str
        assert "session_id=2" in repr_str
        assert "color" in repr_str

    def test_token_library_tablename(self):
        """Test token library table name"""
        assert TokenLibrary.__tablename__ == "token_libraries"


class TestTokenExportModel:
    """Test TokenExport model"""

    def test_token_export_creation(self):
        """Test basic token export creation"""
        export = TokenExport(
            library_id=1,
            format="css",
        )
        assert export.library_id == 1
        assert export.format == "css"

    def test_token_export_with_file_info(self):
        """Test token export with file information"""
        export = TokenExport(
            library_id=1,
            format="w3c",
            file_path="/exports/tokens.json",
            file_size=1024,
        )
        assert export.file_path == "/exports/tokens.json"
        assert export.file_size == 1024

    def test_token_export_formats(self):
        """Test various export formats"""
        formats = ["w3c", "css", "react", "html", "scss", "tailwind"]
        for fmt in formats:
            export = TokenExport(library_id=1, format=fmt)
            assert export.format == fmt

    def test_token_export_repr(self):
        """Test token export __repr__"""
        export = TokenExport(
            id=1,
            library_id=2,
            format="css",
        )
        repr_str = repr(export)
        assert "TokenExport" in repr_str
        assert "id=1" in repr_str
        assert "library_id=2" in repr_str
        assert "css" in repr_str

    def test_token_export_tablename(self):
        """Test token export table name"""
        assert TokenExport.__tablename__ == "token_exports"


class TestModelRelationships:
    """Test logical relationships between models"""

    def test_project_to_extraction_job(self):
        """Test project and extraction job relationship"""
        project = Project(id=1, name="Test Project")
        job = ExtractionJob(
            project_id=project.id,
            source_url="http://example.com/image.jpg",
            extraction_type="color",
        )
        assert job.project_id == project.id

    def test_project_to_color_token(self):
        """Test project and color token relationship"""
        project = Project(id=1, name="Test Project")
        token = ColorToken(
            project_id=project.id,
            hex="#FF5733",
            rgb="rgb(255, 87, 51)",
            name="Red",
            confidence=0.9,
        )
        assert token.project_id == project.id

    def test_session_to_library(self):
        """Test session and library relationship"""
        session = ExtractionSession(id=1, project_id=1, name="Test Session")
        library = TokenLibrary(session_id=session.id, token_type="color")
        assert library.session_id == session.id

    def test_library_to_export(self):
        """Test library and export relationship"""
        library = TokenLibrary(id=1, session_id=1, token_type="color")
        export = TokenExport(library_id=library.id, format="css")
        assert export.library_id == library.id

    def test_token_to_library(self):
        """Test token to library relationship"""
        library = TokenLibrary(id=1, session_id=1, token_type="color")
        token = ColorToken(
            project_id=1,
            hex="#FF5733",
            rgb="rgb(255, 87, 51)",
            name="Red",
            confidence=0.9,
            library_id=library.id,
        )
        assert token.library_id == library.id
