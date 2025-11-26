#!/bin/bash

# =============================================================================
# Spacing Token Pipeline Test Runner
# =============================================================================
#
# REFERENCE IMPLEMENTATION - This is planning/documentation code showing how the
# test runner script should be structured when implemented. This script is not
# meant to be run directly but serves as a complete reference for implementing
# the actual test execution process.
#
# This script:
# 1. Runs all spacing-related tests
# 2. Generates coverage reports
# 3. Provides detailed test output
# =============================================================================

set -e  # Exit on any error (can be disabled for test failures)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# =============================================================================
# Configuration
# =============================================================================

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../../../../../.." && pwd)"
REFERENCE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
TESTS_DIR="$REFERENCE_DIR/tests"

# Test configuration
COVERAGE_DIR="$PROJECT_ROOT/htmlcov"
COVERAGE_FILE="$PROJECT_ROOT/.coverage"
COVERAGE_THRESHOLD=80

# Default settings
RUN_UNIT=true
RUN_INTEGRATION=true
RUN_E2E=false
GENERATE_COVERAGE=true
VERBOSE=false
FAIL_FAST=false
PARALLEL=false
MARKERS=""

# =============================================================================
# Helper Functions
# =============================================================================

print_header() {
    echo ""
    echo -e "${BLUE}==============================================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}==============================================================================${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${CYAN}ℹ $1${NC}"
}

# =============================================================================
# Parse Arguments
# =============================================================================

show_help() {
    echo "Spacing Token Pipeline Test Runner"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Test Selection:"
    echo "  --unit-only         Run only unit tests"
    echo "  --integration-only  Run only integration tests"
    echo "  --e2e               Include end-to-end tests (slow)"
    echo "  --all               Run all tests including e2e"
    echo ""
    echo "Coverage:"
    echo "  --no-coverage       Skip coverage report generation"
    echo "  --coverage-html     Generate HTML coverage report"
    echo "  --min-coverage N    Set minimum coverage threshold (default: $COVERAGE_THRESHOLD)"
    echo ""
    echo "Output:"
    echo "  -v, --verbose       Verbose test output"
    echo "  -q, --quiet         Minimal output"
    echo "  --fail-fast         Stop on first failure"
    echo ""
    echo "Advanced:"
    echo "  -k EXPRESSION       Run tests matching expression"
    echo "  -m MARKERS          Run tests with specific markers"
    echo "  --parallel          Run tests in parallel"
    echo "  --last-failed       Run only tests that failed last time"
    echo ""
    echo "Examples:"
    echo "  $0                          # Run unit + integration tests"
    echo "  $0 --unit-only -v           # Run only unit tests with verbose output"
    echo "  $0 --all --coverage-html    # Run all tests with HTML coverage"
    echo "  $0 -k 'test_extract'        # Run tests matching 'test_extract'"
    echo ""
}

while [[ $# -gt 0 ]]; do
    case $1 in
        --unit-only)
            RUN_UNIT=true
            RUN_INTEGRATION=false
            RUN_E2E=false
            shift
            ;;
        --integration-only)
            RUN_UNIT=false
            RUN_INTEGRATION=true
            RUN_E2E=false
            shift
            ;;
        --e2e)
            RUN_E2E=true
            shift
            ;;
        --all)
            RUN_UNIT=true
            RUN_INTEGRATION=true
            RUN_E2E=true
            shift
            ;;
        --no-coverage)
            GENERATE_COVERAGE=false
            shift
            ;;
        --coverage-html)
            GENERATE_COVERAGE=true
            COVERAGE_HTML=true
            shift
            ;;
        --min-coverage)
            COVERAGE_THRESHOLD="$2"
            shift 2
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -q|--quiet)
            VERBOSE=false
            QUIET=true
            shift
            ;;
        --fail-fast)
            FAIL_FAST=true
            shift
            ;;
        -k)
            TEST_EXPRESSION="$2"
            shift 2
            ;;
        -m)
            MARKERS="$2"
            shift 2
            ;;
        --parallel)
            PARALLEL=true
            shift
            ;;
        --last-failed)
            LAST_FAILED=true
            shift
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# =============================================================================
# Pre-flight Checks
# =============================================================================

print_header "Pre-flight Checks"

# Check pytest is installed
if ! command -v pytest &> /dev/null; then
    print_error "pytest is not installed"
    print_info "Install with: pip install pytest pytest-asyncio pytest-cov"
    exit 1
fi
print_success "pytest is installed"

# Check pytest-cov for coverage
if [ "$GENERATE_COVERAGE" = true ]; then
    if ! python -c "import pytest_cov" &> /dev/null; then
        print_warning "pytest-cov not installed, disabling coverage"
        GENERATE_COVERAGE=false
    else
        print_success "pytest-cov is installed"
    fi
fi

# Check test directory exists
if [ ! -d "$TESTS_DIR" ]; then
    print_error "Tests directory not found: $TESTS_DIR"
    exit 1
fi
print_success "Tests directory found"

# Count test files
UNIT_TESTS=$(find "$TESTS_DIR/unit" -name "test_*.py" 2>/dev/null | wc -l)
INTEGRATION_TESTS=$(find "$TESTS_DIR/integration" -name "test_*.py" 2>/dev/null | wc -l)

print_info "Unit test files: $UNIT_TESTS"
print_info "Integration test files: $INTEGRATION_TESTS"

# =============================================================================
# Build Pytest Command
# =============================================================================

print_header "Building Test Command"

# Base command
PYTEST_CMD="pytest"

# Add paths based on what to run
PYTEST_PATHS=""
if [ "$RUN_UNIT" = true ] && [ $UNIT_TESTS -gt 0 ]; then
    PYTEST_PATHS="$PYTEST_PATHS $TESTS_DIR/unit"
fi
if [ "$RUN_INTEGRATION" = true ] && [ $INTEGRATION_TESTS -gt 0 ]; then
    PYTEST_PATHS="$PYTEST_PATHS $TESTS_DIR/integration"
fi
if [ "$RUN_E2E" = true ]; then
    E2E_DIR="$TESTS_DIR/e2e"
    if [ -d "$E2E_DIR" ]; then
        PYTEST_PATHS="$PYTEST_PATHS $E2E_DIR"
    fi
fi

# Add pytest options
PYTEST_OPTS=""

# Verbose output
if [ "$VERBOSE" = true ]; then
    PYTEST_OPTS="$PYTEST_OPTS -v"
fi

# Quiet output
if [ "$QUIET" = true ]; then
    PYTEST_OPTS="$PYTEST_OPTS -q"
fi

# Fail fast
if [ "$FAIL_FAST" = true ]; then
    PYTEST_OPTS="$PYTEST_OPTS -x"
fi

# Test expression filter
if [ -n "$TEST_EXPRESSION" ]; then
    PYTEST_OPTS="$PYTEST_OPTS -k '$TEST_EXPRESSION'"
fi

# Marker filter
if [ -n "$MARKERS" ]; then
    PYTEST_OPTS="$PYTEST_OPTS -m '$MARKERS'"
fi

# Last failed
if [ "$LAST_FAILED" = true ]; then
    PYTEST_OPTS="$PYTEST_OPTS --lf"
fi

# Parallel execution
if [ "$PARALLEL" = true ]; then
    if python -c "import pytest_xdist" &> /dev/null; then
        PYTEST_OPTS="$PYTEST_OPTS -n auto"
    else
        print_warning "pytest-xdist not installed, running sequentially"
    fi
fi

# Coverage options
if [ "$GENERATE_COVERAGE" = true ]; then
    # Source directories to measure coverage for
    COVERAGE_SOURCE="--cov=src/copy_that/application"

    # Coverage report options
    COVERAGE_OPTS="--cov-report=term-missing --cov-report=xml"

    # HTML report if requested
    if [ "$COVERAGE_HTML" = true ]; then
        COVERAGE_OPTS="$COVERAGE_OPTS --cov-report=html:$COVERAGE_DIR"
    fi

    # Fail if coverage below threshold
    COVERAGE_OPTS="$COVERAGE_OPTS --cov-fail-under=$COVERAGE_THRESHOLD"

    PYTEST_OPTS="$PYTEST_OPTS $COVERAGE_SOURCE $COVERAGE_OPTS"
fi

# Print command
FULL_CMD="$PYTEST_CMD $PYTEST_PATHS $PYTEST_OPTS"
print_info "Command: $FULL_CMD"

# =============================================================================
# Run Tests
# =============================================================================

print_header "Running Tests"

cd "$PROJECT_ROOT"

# Set PYTHONPATH to include src
export PYTHONPATH="$PROJECT_ROOT/src:$PYTHONPATH"

# Record start time
START_TIME=$(date +%s)

# Run tests
set +e  # Don't exit on test failures
eval $FULL_CMD
TEST_EXIT_CODE=$?
set -e

# Record end time
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

# =============================================================================
# Results Summary
# =============================================================================

print_header "Test Results Summary"

# Print duration
MINUTES=$((DURATION / 60))
SECONDS=$((DURATION % 60))
print_info "Total time: ${MINUTES}m ${SECONDS}s"

# Print result
if [ $TEST_EXIT_CODE -eq 0 ]; then
    print_success "All tests passed!"
elif [ $TEST_EXIT_CODE -eq 1 ]; then
    print_error "Some tests failed"
elif [ $TEST_EXIT_CODE -eq 2 ]; then
    print_error "Test execution was interrupted"
elif [ $TEST_EXIT_CODE -eq 3 ]; then
    print_error "Internal error during test execution"
elif [ $TEST_EXIT_CODE -eq 4 ]; then
    print_error "pytest command line usage error"
elif [ $TEST_EXIT_CODE -eq 5 ]; then
    print_warning "No tests were collected"
else
    print_error "Unknown error (exit code: $TEST_EXIT_CODE)"
fi

# Coverage report location
if [ "$GENERATE_COVERAGE" = true ]; then
    echo ""
    print_info "Coverage report: coverage.xml"
    if [ "$COVERAGE_HTML" = true ]; then
        print_info "HTML coverage: $COVERAGE_DIR/index.html"
    fi
fi

# =============================================================================
# Spacing-Specific Test Summary
# =============================================================================

echo ""
print_header "Spacing Pipeline Test Categories"

echo "Tests covered:"
echo ""
echo "Unit Tests:"
echo "  - test_spacing_extractor.py: AI extraction logic"
echo "  - test_spacing_utils.py: Utility functions (px_to_rem, scale detection)"
echo "  - test_spacing_aggregator.py: Batch deduplication and statistics"
echo ""
echo "Integration Tests:"
echo "  - test_spacing_pipeline.py: End-to-end pipeline, API endpoints, streaming"
echo ""

# =============================================================================
# Exit
# =============================================================================

exit $TEST_EXIT_CODE
