"""Test CLI commands."""

from click.testing import CliRunner

from scipaper.cli import main


def test_cli_health():
    """Test CLI health command."""
    runner = CliRunner()
    result = runner.invoke(main, ['health'])
    assert result.exit_code == 0
    assert 'SciPaper System Health Check' in result.output


def test_cli_parse():
    """Test CLI parse command."""
    runner = CliRunner()
    result = runner.invoke(main, ['parse', 'Check doi:10.1000/xyz123'])
    assert result.exit_code == 0
    assert 'doi' in result.output
    assert '10.1000/xyz123' in result.output


def test_cli_main_help():
    """Test CLI main help."""
    runner = CliRunner()
    result = runner.invoke(main, ['--help'])
    assert result.exit_code == 0
    assert 'SciPaper' in result.output
    assert 'comprehensive scientific paper' in result.output
