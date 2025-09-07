from openinorganicchemistry.core.settings import Settings

# Example usage
s = Settings.load()
print(f"Model: {s.model_general}")
print(f"API Key masked: {s.openai_api_key_masked}")