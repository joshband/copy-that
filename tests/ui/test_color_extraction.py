"""
UI tests for color extraction demo using Playwright
"""

import pytest
from playwright.sync_api import Page, expect


class TestColorExtractionUI:
    """Test the color extraction demo UI"""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """Navigate to the demo page before each test"""
        # Assumes the app is running at localhost:8000
        page.goto("http://localhost:8000/")
        self.page = page

    def test_page_loads_with_title(self):
        """Test that the page loads with the correct title"""
        expect(self.page).to_have_title("Copy That - AI Color Extraction Demo")

    def test_upload_area_exists(self):
        """Test that the upload area is present"""
        upload_area = self.page.locator("#uploadArea")
        expect(upload_area).to_be_visible()

    def test_extract_button_hidden_initially(self):
        """Test that extract button is hidden before image upload"""
        extract_btn = self.page.locator("#extractBtn")
        expect(extract_btn).to_be_hidden()

    def test_results_section_hidden_initially(self):
        """Test that results section shows empty state initially"""
        empty_state = self.page.locator("#emptyState")
        expect(empty_state).to_be_visible()

    def test_api_docs_link_exists(self):
        """Test that API docs link is present"""
        docs_link = self.page.locator('a[href="/docs"]')
        expect(docs_link).to_be_visible()


class TestColorDisplay:
    """Test color display attributes"""

    @pytest.fixture
    def mock_colors_response(self):
        """Mock color extraction response"""
        return {
            "colors": [
                {
                    "hex": "#FF5733",
                    "rgb": "rgb(255, 87, 51)",
                    "name": "Sunset Orange",
                    "semantic_name": "primary",
                    "confidence": 0.95,
                    "design_intent": "accent color",
                    "harmony": "complementary",
                    "usage": ["buttons", "highlights"],
                    "prominence_percentage": 25.5,
                    "wcag_aa_compliant_text": True,
                },
                {
                    "hex": "#4ECDC4",
                    "rgb": "rgb(78, 205, 196)",
                    "name": "Turquoise",
                    "semantic_name": "secondary",
                    "confidence": 0.88,
                    "design_intent": "background",
                    "harmony": "analogous",
                    "usage": ["backgrounds", "cards"],
                    "prominence_percentage": 18.2,
                    "wcag_aa_compliant_text": False,
                },
            ],
            "dominant_colors": ["#FF5733", "#4ECDC4", "#2C3E50"],
            "color_palette": "Vibrant and modern palette",
            "extraction_confidence": 0.91,
            "extractor_used": "gpt-4o",
        }

    def test_color_card_displays_all_attributes(self, page: Page, mock_colors_response):
        """Test that color cards display all required attributes"""
        # Inject test data via JavaScript
        page.goto("http://localhost:8000/")
        page.evaluate(f"""
            showResults({mock_colors_response});
        """)

        # Check that color cards are created
        color_cards = page.locator(".color-card")
        expect(color_cards).to_have_count(2)

        # Check first color card has all attributes
        first_card = color_cards.first

        # Hex code should be displayed
        hex_element = first_card.locator(".color-hex")
        expect(hex_element).to_contain_text("#FF5733")

        # RGB should be displayed
        rgb_element = first_card.locator(".color-rgb")
        expect(rgb_element).to_contain_text("rgb(255, 87, 51)")

        # Name should be displayed
        name_element = first_card.locator(".color-name")
        expect(name_element).to_contain_text("Sunset Orange")

        # Semantic name should be displayed
        semantic_element = first_card.locator(".color-semantic")
        expect(semantic_element).to_contain_text("primary")

        # Design intent should be displayed
        intent_element = first_card.locator(".color-intent")
        expect(intent_element).to_be_visible()

        # Harmony should be displayed
        harmony_element = first_card.locator(".color-harmony")
        expect(harmony_element).to_be_visible()

        # Usage should be displayed
        usage_element = first_card.locator(".color-usage")
        expect(usage_element).to_be_visible()

        # WCAG compliance should be displayed
        wcag_element = first_card.locator(".color-wcag")
        expect(wcag_element).to_be_visible()

    def test_extractor_used_displayed_in_stats(self, page: Page, mock_colors_response):
        """Test that the AI model used is displayed in stats"""
        page.goto("http://localhost:8000/")
        page.evaluate(f"""
            showResults({mock_colors_response});
        """)

        stats = page.locator("#stats")
        expect(stats).to_contain_text("gpt-4o")
        expect(stats).to_contain_text("AI Model")

    def test_color_count_displayed(self, page: Page, mock_colors_response):
        """Test that color count is displayed correctly"""
        page.goto("http://localhost:8000/")
        page.evaluate(f"""
            showResults({mock_colors_response});
        """)

        stats = page.locator("#stats")
        expect(stats).to_contain_text("2")
        expect(stats).to_contain_text("Colors Extracted")


class TestCopyFunctionality:
    """Test copy-to-clipboard functionality"""

    def test_color_swatch_has_copy_hint(self, page: Page):
        """Test that color swatch shows copy hint on hover"""
        page.goto("http://localhost:8000/")

        # Inject a test color
        page.evaluate("""
            showResults({
                colors: [{
                    hex: "#FF5733",
                    rgb: "rgb(255, 87, 51)",
                    name: "Test",
                    confidence: 0.9
                }],
                dominant_colors: ["#FF5733"],
                color_palette: "Test",
                extraction_confidence: 0.9,
                extractor_used: "test"
            });
        """)

        # Check copy hint exists
        copy_hint = page.locator(".copy-hint")
        expect(copy_hint).to_be_attached()

    def test_hex_code_is_clickable(self, page: Page):
        """Test that hex code element has click handler"""
        page.goto("http://localhost:8000/")

        # Inject a test color
        page.evaluate("""
            showResults({
                colors: [{
                    hex: "#FF5733",
                    rgb: "rgb(255, 87, 51)",
                    name: "Test",
                    confidence: 0.9
                }],
                dominant_colors: ["#FF5733"],
                color_palette: "Test",
                extraction_confidence: 0.9,
                extractor_used: "test"
            });
        """)

        # Check hex element has cursor pointer (indicates clickable)
        hex_element = page.locator(".color-hex")
        expect(hex_element).to_have_css("cursor", "pointer")


class TestAccessibility:
    """Test accessibility features"""

    def test_upload_area_has_description(self, page: Page):
        """Test that upload area has descriptive text"""
        page.goto("http://localhost:8000/")
        upload_area = page.locator("#uploadArea")
        expect(upload_area).to_contain_text("Drag & drop")
        expect(upload_area).to_contain_text("click to browse")

    def test_buttons_have_visible_text(self, page: Page):
        """Test that buttons have visible text labels"""
        page.goto("http://localhost:8000/")
        # The button should have text when visible
        page.evaluate("""
            document.getElementById('extractBtn').style.display = 'block';
        """)
        extract_btn = page.locator("#extractBtn")
        expect(extract_btn).to_contain_text("Extract Colors")
