import ollama
import sys

print("Testing Ollama connection...")

try:
    # Test listing models
    print("Attempting to list models...")
    models = ollama.list()
    print("Success! Models found:")
    for m in models['models']:
        print(f" - {m['name']}")
        
    # Test connection to specific model check
    target_model = "llama3.2-vision"
    found = any(m['name'].startswith(target_model) for m in models['models'])
    if found:
        print(f"\nModel '{target_model}' is present.")
    else:
        print(f"\nWARNING: Model '{target_model}' NOT found in list.")
        print("Please run: ollama pull llama3.2-vision")

    # Simple generation test (if model exists)
    if found:
        print(f"\nTesting generation with {target_model}...")
        res = ollama.chat(model=target_model, messages=[{'role': 'user', 'content': 'hello'}])
        print("Response:", res['message']['content'])

except Exception as e:
    print(f"\nERROR: Failed to connect or interact with Ollama.")
    print(f"Exception Type: {type(e).__name__}")
    print(f"Exception Message: {e}")
    print("\nTroubleshooting:")
    print("1. Ensure 'ollama serve' is running in a separate terminal.")
    print("2. Check if http://localhost:11434/ is accessible.")
