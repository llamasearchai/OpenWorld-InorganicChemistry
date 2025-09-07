"""Test CLI commands."""

from unittest.mock import patch

from click.testing import CliRunner

from scipaper.cli import main


def test_cli_health():
    """Test CLI health command."""
    runner = CliRunner()
    with patch('scipaper.config.is_openai_available', return_value=True), \
         patch('scipaper.config.is_ollama_available', return_value=False):
        result = runner.invoke(main, ['health'])
        assert result.exit_code == 0
        assert 'SciPaper System Health Check' in result.output
        assert 'Available' in result.output


def test_cli_parse():
    """Test CLI parse command."""
    runner = CliRunner()
    result = runner.invoke(main, ['parse', 'Check doi:10.1000/xyz123'])
    assert result.exit_code == 0
    assert 'doi' in result.output


def test_cli_main_help():
    """Test CLI main help."""
    runner = CliRunner()
    result = runner.invoke(main, ['--help'])
    assert result.exit_code == 0
    assert 'SciPaper' in result.output


def test_cli_invalid_command():
    """Test CLI with invalid command."""
    runner = CliRunner()
    result = runner.invoke(main, ['invalid'])
    assert result.exit_code == 2  # Click uses exit code 2 for command not found
