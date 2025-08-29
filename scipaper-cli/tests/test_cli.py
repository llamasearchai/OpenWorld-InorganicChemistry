import pytest
from click.testing import CliRunner
from scipaper.cli import main
from unittest.mock import patch

@pytest.fixture
def runner():
    return CliRunner()

def test_cli_help(runner):
    """Test CLI help command"""
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "SciPaper CLI - Master Interface" in result.output

def test_cli_master_help(runner):
    """Test master command help"""
    result = runner.invoke(main, ["master", "--help"])
    assert result.exit_code == 0
    assert "Master command interface with Ollama integration" in result.output

@patch("scipaper.cli.run_async")
def test_cli_master_search(mock_run, runner):
    """Test master search command"""
    mock_run.return_value = "Mocked search results"
    result = runner.invoke(main, ["master", "search test"])
    assert result.exit_code == 0
    assert "Mocked search results" in result.output

@patch("scipaper.cli.run_async")
def test_cli_master_fetch(mock_run, runner):
    """Test master fetch command"""
    mock_run.return_value = "Mocked fetch results"
    result = runner.invoke(main, ["master", "fetch test"])
    assert result.exit_code == 0
    assert "Mocked fetch results" in result.output

@patch("scipaper.cli.run_async")
def test_cli_master_agent(mock_run, runner):
    """Test master agent command"""
    mock_run.return_value = "Mocked agent response"
    result = runner.invoke(main, ["master", "agent test"])
    assert result.exit_code == 0
    assert "Mocked agent response" in result.output

def test_cli_master_unknown_command(runner):
    """Test master with unknown command"""
    result = runner.invoke(main, ["master", "unknown"])
    assert result.exit_code == 0
    assert "Unknown command" in result.output

def test_cli_direct_commands(runner):
    """Test direct CLI commands"""
    with patch("scipaper.cli.run_async") as mock_run:
        mock_run.return_value = "Mocked response"
        
        # Test health command
        result = runner.invoke(main, ["health"])
        assert result.exit_code == 0
        
        # Test search command
        result = runner.invoke(main, ["search", "test"])
        assert result.exit_code == 0
        
        # Test fetch command
        result = runner.invoke(main, ["fetch", "test"])
        assert result.exit_code == 0
        
        # Test agent command
        result = runner.invoke(main, ["agent", "test"])
        assert result.exit_code == 0


def test_cli_parse_text(runner):
    result = runner.invoke(main, ["parse", "--text", "doi 10.1/xyz", "--match", "doi", "--format", "csv"])
    assert result.exit_code == 0
    assert "10.1/xyz,doi" in result.output