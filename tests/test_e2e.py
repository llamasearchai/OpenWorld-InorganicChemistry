"""End-to-end tests for SciPaper system."""

import json
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from click.testing import CliRunner

from scipaper.main import app
from scipaper.cli import main as cli_main


class TestEndToEnd:
    """End-to-end tests for the complete SciPaper system."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = TestClient(app)
        self.cli_runner = CliRunner()

    def test_api_health_endpoint(self):
        """Test API health endpoint returns correct information."""
        response = self.client.get("/api/v1/health")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "ok"
        assert "version" in data
        assert "openai" in data
        assert "ollama" in data
        assert "downloads_dir" in data

    def test_cli_health_command(self):
        """Test CLI health command output."""
        result = self.cli_runner.invoke(cli_main, ["health"])

        assert result.exit_code == 0
        assert "SciPaper System Health Check" in result.output
        assert "Version:" in result.output

    def test_api_parse_endpoint(self):
        """Test API parse endpoint with various identifier types."""
        test_cases = [
            {
                "text": "Check out this paper: doi:10.1000/xyz123",
                "expected_type": "doi",
                "expected_value": "10.1000/xyz123"
            },
            {
                "text": "See arXiv:2103.01234v1 for details",
                "expected_type": "arxiv",
                "expected_value": "2103.01234v1"
            },
            {
                "text": "ISBN: 978-0123456789 is a great book",
                "expected_type": "isbn",
                "expected_value": "978-0123456789"
            },
            {
                "text": "Visit https://example.com/paper.pdf",
                "expected_type": "url",
                "expected_value": "https://example.com/paper.pdf"
            }
        ]

        for test_case in test_cases:
            payload = {
                "text": test_case["text"],
                "types": [test_case["expected_type"]]
            }

            response = self.client.post("/api/v1/parse", json=payload)

            assert response.status_code == 200
            data = response.json()

            assert len(data) > 0
            assert data[0]["type"] == test_case["expected_type"]
            assert data[0]["value"] == test_case["expected_value"]

    def test_cli_parse_command(self):
        """Test CLI parse command with different formats."""
        result = self.cli_runner.invoke(cli_main, [
            "parse",
            "Check doi:10.1000/xyz123 and arXiv:2103.01234"
        ])

        assert result.exit_code == 0
        assert "doi" in result.output
        assert "10.1000/xyz123" in result.output
        assert "arxiv" in result.output
        assert "2103.01234" in result.output

    def test_cli_parse_with_format_options(self):
        """Test CLI parse command with different output formats."""
        # Test JSON format
        result = self.cli_runner.invoke(cli_main, [
            "parse",
            "doi:10.1000/test",
            "--format", "json"
        ])

        assert result.exit_code == 0
        # Should be valid JSON
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert len(data) > 0
        assert data[0]["type"] == "doi"

    def test_api_search_endpoint_validation(self):
        """Test API search endpoint input validation."""
        # Test missing query
        response = self.client.post("/api/v1/search", json={})
        assert response.status_code == 422  # Validation error

        # Test valid request structure
        payload = {
            "query": "test query",
            "sources": ["crossref"],
            "limit": 5
        }
        response = self.client.post("/api/v1/search", json=payload)
        # May fail due to network/mock issues, but should not be 422
        assert response.status_code != 422

    def test_api_fetch_endpoint_validation(self):
        """Test API fetch endpoint input validation."""
        # Test missing identifier
        response = self.client.post("/api/v1/fetch", json={})
        assert response.status_code == 422  # Validation error

        # Test valid request structure
        payload = {
            "identifier": "10.1000/test",
            "source": "crossref"
        }
        response = self.client.post("/api/v1/fetch", json=payload)
        # May fail due to network/mock issues, but should not be 422
        assert response.status_code != 422

    def test_cli_commands_help(self):
        """Test CLI help commands work correctly."""
        # Test main help
        result = self.cli_runner.invoke(cli_main, ["--help"])
        assert result.exit_code == 0
        assert "SciPaper" in result.output
        assert "comprehensive scientific paper" in result.output

        # Test search help
        result = self.cli_runner.invoke(cli_main, ["search", "--help"])
        assert result.exit_code == 0
        assert "Search for papers" in result.output

        # Test fetch help
        result = self.cli_runner.invoke(cli_main, ["fetch", "--help"])
        assert result.exit_code == 0
        assert "Fetch a specific paper" in result.output

    def test_api_response_formats(self):
        """Test API responses have consistent format."""
        # Test parse endpoint response format
        payload = {"text": "doi:10.1000/test123"}
        response = self.client.post("/api/v1/parse", json=payload)

        assert response.status_code == 200
        data = response.json()

        # Check response structure
        assert isinstance(data, list)
        if data:
            item = data[0]
            assert "type" in item
            assert "value" in item
            assert "position" in item

    def test_cli_error_handling(self):
        """Test CLI error handling for invalid inputs."""
        # Test with invalid command
        result = self.cli_runner.invoke(cli_main, ["invalid_command"])
        assert result.exit_code != 0

        # Test parse with empty text
        result = self.cli_runner.invoke(cli_main, ["parse", ""])
        assert result.exit_code == 0  # Should handle gracefully
        assert "No identifiers found" in result.output

    def test_api_cors_headers(self):
        """Test API includes proper CORS headers."""
        response = self.client.options("/api/v1/health")
        assert response.status_code in [200, 404]  # 404 is also acceptable for OPTIONS

        # Test actual request has CORS headers
        response = self.client.get("/api/v1/health", headers={"Origin": "http://localhost:3000"})
        assert "access-control-allow-origin" in response.headers

    def test_cli_output_consistency(self):
        """Test CLI output is consistent and well-formatted."""
        result = self.cli_runner.invoke(cli_main, ["health"])

        assert result.exit_code == 0
        # Should have structured output with clear sections
        assert "Version:" in result.output
        assert "OpenAI API:" in result.output
        assert "Ollama:" in result.output

    def test_configuration_loading(self):
        """Test that configuration is loaded properly."""
        from scipaper.config import settings

        # Test that settings object exists and has expected attributes
        assert hasattr(settings, 'fastapi_host')
        assert hasattr(settings, 'fastapi_port')
        assert hasattr(settings, 'log_level')

        # Test that settings have reasonable defaults
        assert isinstance(settings.fastapi_port, int)
        assert settings.fastapi_port > 0

    @pytest.mark.asyncio
    async def test_source_registry_functionality(self):
        """Test source registry works correctly."""
        from scipaper.sources.registry import list_sources, get_source

        sources = list_sources()
        assert isinstance(sources, list)
        assert len(sources) > 0

        # Test getting a source instance
        if sources:
            source = get_source(sources[0])
            assert source is not None
            assert hasattr(source, 'name')

    def test_error_response_format(self):
        """Test error responses have consistent format."""
        # Test with invalid endpoint
        response = self.client.get("/api/v1/nonexistent")
        assert response.status_code == 404

        # Test with invalid method
        response = self.client.post("/api/v1/health")
        assert response.status_code == 405  # Method not allowed

    def test_cli_version_option(self):
        """Test CLI version option works."""
        result = self.cli_runner.invoke(cli_main, ["--version"])
        assert result.exit_code == 0
        assert "1.0.0" in result.output
