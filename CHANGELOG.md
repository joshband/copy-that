# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project setup as full-stack web application
- Git repository initialization at ~/Documents/3_Development/Repos/copy-that
- CHANGELOG.md for tracking project changes
- Python-based backend structure (src/ directory)
- **Frontend application (React + TypeScript + Vite)**:
  - Drag & drop image upload component (up to 10 images)
  - Image preview grid with hover actions
  - File validation (type, size, count)
  - Error handling and user feedback
  - Responsive design with Tailwind CSS
  - React Dropzone integration
  - Heroicons for UI icons
  - Individual image removal and clear all functionality
- Project documentation:
  - DESIGN.md - Architecture and technical approach
  - QUICK_START.md - Quick start guide
  - IMPLEMENTATION.md - Implementation details
  - OPENAI_VISION.md - OpenAI Vision API integration guide
  - DESIGN_SYSTEM_STRUCTURE.md - Industry-standard design system structure
  - BRAND_GUIDE.md - Visual identity and design principles
  - frontend/README.md - Frontend setup and usage guide
- Claude Code project configuration (.claude/CLAUDE.md)
- requirements.txt with computer vision and ML dependencies:
  - OpenCV, scikit-image, Pillow for image processing
  - PyTorch, Transformers for ML
  - OpenAI SDK (>= 1.12.0) for AI-powered analysis
  - python-dotenv for environment configuration
  - SVG, Cairo for graphics generation
- setup.py for package installation
- .env configuration support for OpenAI API key

### Changed

### Deprecated

### Removed

### Fixed

### Security

---

## [0.1.0] - 2025-10-30

### Added
- Project "Copy That" initialized
- Repository structure created
