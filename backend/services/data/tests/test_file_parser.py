"""
Tests for FileParser (Resume Document Parser).

Tests basic functionality for PDF/DOCX parsing and data extraction.
Full integration tests with real resumes deferred to integration test suite.
"""

import tempfile
from pathlib import Path

import pytest

from backend.services.data.file_parser import FileParser


class TestFileParser:
    """Test FileParser initialization."""
    
    def test_parser_initialization(self):
        """Test that FileParser initializes correctly."""
        parser = FileParser()
        assert parser is not None
        assert parser.email_pattern is not None
        assert parser.phone_pattern is not None
        assert len(parser.tech_keywords) > 100  # Should have 100+ tech keywords


class TestPersonalInfoExtraction:
    """Test personal information extraction."""
    
    def test_extract_email(self):
        """Test email extraction from text."""
        parser = FileParser()
        text = """
        John Doe
        john.doe@example.com
        +1234567890
        """
        
        personal_info, confidence, warnings = parser.extract_personal_info(text)
        
        assert personal_info is not None
        assert personal_info['email'] == 'john.doe@example.com'
        assert confidence > 0.5
    
    def test_extract_phone(self):
        """Test phone extraction from text."""
        parser = FileParser()
        text = """
        Jane Smith
        jane@example.com
        +12025551234
        """
        
        personal_info, confidence, warnings = parser.extract_personal_info(text)
        
        assert personal_info is not None
        assert personal_info.get('phone') == '+12025551234'
    
    def test_extract_linkedin(self):
        """Test LinkedIn URL extraction."""
        parser = FileParser()
        text = """
        Bob Johnson
        bob@example.com
        linkedin.com/in/bobjohnson
        """
        
        personal_info, confidence, warnings = parser.extract_personal_info(text)
        
        assert personal_info is not None
        assert str(personal_info.get('linkedin_url')) == 'https://linkedin.com/in/bobjohnson'
    
    def test_extract_github(self):
        """Test GitHub URL extraction."""
        parser = FileParser()
        text = """
        Alice Developer
        alice@example.com
        github.com/alicedev
        """
        
        personal_info, confidence, warnings = parser.extract_personal_info(text)
        
        assert personal_info is not None
        assert str(personal_info.get('github_url')) == 'https://github.com/alicedev'
    
    def test_extract_name(self):
        """Test name extraction from text."""
        parser = FileParser()
        text = """
        Sarah Williams
        sarah.williams@example.com
        Software Engineer
        """
        
        personal_info, confidence, warnings = parser.extract_personal_info(text)
        
        assert personal_info is not None
        assert personal_info['first_name'] == 'Sarah'
        assert personal_info['last_name'] == 'Williams'
    
    def test_missing_email_warning(self):
        """Test warning when email not found."""
        parser = FileParser()
        text = """
        John Doe
        No email here
        """
        
        personal_info, confidence, warnings = parser.extract_personal_info(text)
        
        assert "Email not found" in " ".join(warnings)
        assert confidence < 0.5


class TestSkillsExtraction:
    """Test skills extraction."""
    
    def test_extract_skills_from_section(self):
        """Test skills extraction from dedicated section."""
        parser = FileParser()
        text = """
        Skills:
        Python, JavaScript, React, Django, AWS, Docker, Kubernetes, Git
        """
        
        skills, confidence = parser.extract_skills(text)
        
        assert 'Python' in skills
        assert 'JavaScript' in skills
        assert 'React' in skills
        assert 'Django' in skills
        assert confidence > 0.8
    
    def test_extract_skills_from_full_text(self):
        """Test skills extraction when no dedicated section."""
        parser = FileParser()
        text = """
        Software Engineer with 5 years of experience in Python and JavaScript.
        Built scalable web applications using React and Django.
        Deployed on AWS using Docker and Kubernetes.
        """
        
        skills, confidence = parser.extract_skills(text)
        
        assert 'Python' in skills
        assert 'JavaScript' in skills
        assert 'React' in skills
        # Confidence lower when no dedicated section
        assert confidence > 0.0
    
    def test_no_skills_found(self):
        """Test when no skills detected."""
        parser = FileParser()
        text = """
        I am a person with experience in things.
        """
        
        skills, confidence = parser.extract_skills(text)
        
        assert skills == []
        assert confidence == 0.0


class TestSectionFinding:
    """Test section detection helper."""
    
    def test_find_section(self):
        """Test finding section by keywords."""
        parser = FileParser()
        text = """
        Personal Info
        John Doe
        
        Experience:
        Software Engineer at TechCorp
        2020 - Present
        
        Education:
        BS Computer Science
        """
        
        section = parser._find_section(text, ["Experience", "Work History"])
        
        assert section is not None
        assert "Software Engineer" in section
        assert "TechCorp" in section
    
    def test_section_not_found(self):
        """Test when section doesn't exist."""
        parser = FileParser()
        text = """
        John Doe
        john@example.com
        """
        
        section = parser._find_section(text, ["Projects"])
        
        assert section is None


class TestErrorHandling:
    """Test error handling for invalid files."""
    
    def test_unsupported_file_format(self):
        """Test error for unsupported file format."""
        parser = FileParser()
        
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            file_path = Path(f.name)
            f.write(b"Some text content")
        
        try:
            with pytest.raises(ValueError, match="File format not supported"):
                parser.parse_resume(file_path)
        finally:
            file_path.unlink()
    
    def test_nonexistent_pdf(self):
        """Test error for nonexistent PDF file."""
        parser = FileParser()
        file_path = Path("nonexistent_resume.pdf")
        
        with pytest.raises(FileNotFoundError):
            parser.parse_pdf(file_path)
    
    def test_nonexistent_docx(self):
        """Test error for nonexistent DOCX file."""
        parser = FileParser()
        file_path = Path("nonexistent_resume.docx")
        
        with pytest.raises(FileNotFoundError):
            parser.parse_docx(file_path)


class TestIntegration:
    """Integration tests (minimal - full tests require real resume files)."""
    
    def test_parse_resume_with_text_file_creates_sample_docx(self, tmp_path):
        """Test basic parsing workflow (using mock DOCX would require python-docx in tests)."""
        parser = FileParser()
        
        # This test is a placeholder - real integration tests would use sample resume files
        # For now, just verify parser can be instantiated and has required methods
        assert hasattr(parser, 'parse_resume')
        assert hasattr(parser, 'extract_personal_info')
        assert hasattr(parser, 'extract_skills')
        assert callable(parser.parse_resume)
