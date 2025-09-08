from __future__ import annotations

import logging
import subprocess
import sys
from dataclasses import dataclass
from typing import Dict, List, Optional

from .settings import Settings

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of a validation check."""
    name: str
    status: str  # "pass", "warn", "fail"
    message: str
    details: Optional[str] = None


class SystemValidator:
    """Validates system requirements and configuration."""
    
    def __init__(self):
        self.results: List[ValidationResult] = []
    
    def check_python_version(self) -> ValidationResult:
        """Check Python version compatibility."""
        version = sys.version_info
        if version >= (3, 9):
            return ValidationResult(
                "Python Version",
                "pass",
                f"Python {version.major}.{version.minor}.{version.micro} ✓"
            )
        else:
            return ValidationResult(
                "Python Version",
                "fail",
                f"Python {version.major}.{version.minor}.{version.micro} - requires 3.9+"
            )
    
    def check_api_key(self) -> ValidationResult:
        """Check OpenAI API key configuration."""
        settings = Settings.load()
        if settings.openai_api_key:
            return ValidationResult(
                "OpenAI API Key",
                "pass",
                f"API key configured: {settings.openai_api_key_masked}"
            )
        else:
            return ValidationResult(
                "OpenAI API Key",
                "warn",
                "No API key found - set OPENAI_API_KEY environment variable",
                "Some features will not work without an API key"
            )
    
    def check_optional_dependencies(self) -> ValidationResult:
        """Check optional scientific computing dependencies."""
        missing = []
        optional_deps = [
            "ase", "pymatgen", "scikit-learn", 
            "pandas", "matplotlib", "plotly"
        ]
        
        for dep in optional_deps:
            try:
                __import__(dep)
            except ImportError:
                missing.append(dep)
        
        if not missing:
            return ValidationResult(
                "Optional Dependencies",
                "pass",
                "All optional dependencies available ✓"
            )
        else:
            return ValidationResult(
                "Optional Dependencies",
                "warn",
                f"Missing: {', '.join(missing)}",
                "Install with: pip install " + " ".join(missing)
            )
    
    def check_git_status(self) -> ValidationResult:
        """Check git repository status."""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True, text=True, check=True
            )
            if result.stdout.strip():
                return ValidationResult(
                    "Git Status",
                    "warn",
                    "Uncommitted changes detected",
                    "Consider committing changes before running experiments"
                )
            else:
                return ValidationResult(
                    "Git Status",
                    "pass",
                    "Working directory clean ✓"
                )
        except (subprocess.CalledProcessError, FileNotFoundError):
            return ValidationResult(
                "Git Status",
                "warn",
                "Not a git repository or git not available"
            )
    
    def check_disk_space(self) -> ValidationResult:
        """Check available disk space."""
        try:
            import shutil
            total, used, free = shutil.disk_usage(".")
            free_gb = free // (1024**3)
            
            if free_gb > 10:
                return ValidationResult(
                    "Disk Space",
                    "pass",
                    f"{free_gb} GB available ✓"
                )
            elif free_gb > 1:
                return ValidationResult(
                    "Disk Space",
                    "warn",
                    f"{free_gb} GB available - consider cleaning up"
                )
            else:
                return ValidationResult(
                    "Disk Space",
                    "fail",
                    f"{free_gb} GB available - critically low"
                )
        except Exception:
            return ValidationResult(
                "Disk Space",
                "warn",
                "Could not check disk space"
            )
    
    def run_all_checks(self) -> Dict[str, ValidationResult]:
        """Run all validation checks."""
        checks = [
            self.check_python_version,
            self.check_api_key,
            self.check_optional_dependencies,
            self.check_git_status,
            self.check_disk_space
        ]
        
        results = {}
        for check in checks:
            result = check()
            results[result.name] = result
            self.results.append(result)
        
        return results
    
    def print_summary(self) -> None:
        """Print validation summary."""
        print("\n=== System Validation Report ===")
        
        for result in self.results:
            status_icon = {
                "pass": "✅",
                "warn": "⚠️ ",
                "fail": "❌"
            }.get(result.status, "❓")
            
            print(f"{status_icon} {result.name}: {result.message}")
            if result.details:
                print(f"   → {result.details}")
        
        print()
        
        # Summary counts
        counts = {"pass": 0, "warn": 0, "fail": 0}
        for result in self.results:
            counts[result.status] += 1
        
        print(f"Summary: {counts['pass']} passed, {counts['warn']} warnings, {counts['fail']} failed")
        
        if counts["fail"] > 0:
            print("\n❌ Critical issues detected - please resolve before proceeding")
        elif counts["warn"] > 0:
            print("\n⚠️  Some warnings detected - review recommendations")
        else:
            print("\n✅ All checks passed - system ready!")