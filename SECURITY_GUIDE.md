# Security Guide

## Overview

This document outlines security measures implemented in OpenWorld-InorganicChemistry and best practices for secure usage.

## Security Features Implemented

### ✅ API Key Security
- **Environment-based Configuration**: API keys loaded from environment variables
- **Keychain Integration**: macOS Keychain fallback for secure local storage
- **No Hardcoded Secrets**: Zero hardcoded API keys or credentials in source code
- **Masked Logging**: API keys automatically masked in logs and output

### ✅ Comprehensive .gitignore
- Blocks all common secret file patterns (.env*, secrets/, etc.)
- Prevents accidental commit of API keys, tokens, and credentials
- Includes patterns for certificates, private keys, and authentication files
- Protects temporary files and backups that might contain sensitive data

### ✅ Secure Configuration Management
- Template-based configuration with `.env.example`
- Environment variable precedence system
- Built-in validation with security checks
- Clear separation between development and production configs

## Setup Instructions

### 1. Initial Setup
```bash
# Clone repository (no secrets included)
git clone <repository-url>
cd OpenWorld-InorganicChemistry

# Copy configuration template
cp .env.example .env

# Edit with your actual API keys (NEVER commit .env)
# OPENAI_API_KEY=your_actual_key_here
```

### 2. Verify Security Setup
```bash
# Run comprehensive security validation
python -m openinorganicchemistry.cli doctor

# Check for any exposed secrets (should be clean)
grep -r "sk-\|ghp_" . --exclude-dir=.git --exclude-dir=.tox --exclude-dir=.venv
```

### 3. Production Deployment
- Use environment variables instead of `.env` files
- Implement key rotation policies (30-90 days)
- Monitor API usage for anomalies
- Use minimal permissions for service accounts

## Security Validations

The enhanced `doctor` command performs comprehensive security checks:

- ✅ Python version compatibility
- ✅ API key presence and format validation
- ✅ Dependency availability and versions
- ✅ Git repository status and uncommitted changes
- ✅ Disk space and system resources
- ✅ File permissions and access controls

## Threat Model

### Protected Against:
- ✅ Accidental secret commits
- ✅ API key exposure in logs
- ✅ Configuration file leakage
- ✅ Dependency vulnerabilities
- ✅ Local privilege escalation

### Additional Protections Needed:
- 🔄 Network transport security (HTTPS enforced)
- 🔄 Input validation and sanitization
- 🔄 Rate limiting for API calls
- 🔄 Audit logging for sensitive operations

## Best Practices

### For Users
- Keep API keys confidential and rotate regularly
- Never share `.env` files or commit them to version control
- Use the doctor command before important operations
- Monitor API usage in your provider dashboards

### For Developers
- Always use the provided template files
- Test with mock/test API keys during development
- Use environment variables in all deployment scenarios
- Implement proper error handling to avoid information leakage

## Incident Response

If you suspect a security incident:

1. **Immediate Actions**:
   - Rotate all API keys immediately
   - Check API provider usage logs for unauthorized activity
   - Review git commit history for accidental exposures

2. **Investigation**:
   - Run security validation: `python -m openinorganicchemistry.cli doctor`
   - Check for unauthorized changes to configuration files
   - Review recent system access logs

3. **Recovery**:
   - Update all affected credentials
   - Patch any identified vulnerabilities
   - Document lessons learned and update security procedures

## Compliance

This implementation follows security best practices including:

- **OWASP Guidelines**: Secure configuration management
- **NIST Framework**: Secure software development lifecycle
- **Industry Standards**: Secret management and access control

## Regular Maintenance

Security is maintained through:

- 🔄 Weekly dependency security scans
- 🔄 Monthly API key rotation reminders
- 🔄 Quarterly security architecture reviews
- 🔄 Annual threat model updates

## Contact

For security questions or concerns:
- Review this guide and run the doctor command first
- Check existing issues for similar problems
- Create private security advisory for sensitive issues

---

**Remember**: Security is a shared responsibility. Follow these guidelines to keep your installation secure.