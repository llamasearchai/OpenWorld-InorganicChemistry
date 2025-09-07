#!/usr/bin/env bash
set -euo pipefail
KEY_NAME="OPENAI_API_KEY"
if ! command -v security >/dev/null 2>&1; then
  echo "macOS 'security' tool not found. Are you on macOS?"
  exit 1
fi
read -rsp "Enter your OpenAI API key (sk-...): " KEY
echo
security add-generic-password -a "$USER" -s "$KEY_NAME" -w "$KEY" -U
echo "Stored $KEY_NAME in macOS Keychain (service=$KEY_NAME, account=$USER)."
echo "You can retrieve it programmatically via the 'keyring' Python package."


