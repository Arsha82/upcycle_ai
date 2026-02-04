import os
# import try_import_airllm # placeholder removed
try:
    import ollama
except ImportError:
    ollama = None
except ImportError:
    ollama = None

class InferenceEngine:
    def generate_response(self, image_bytes, prompt):
        raise NotImplementedError

class OllamaEngine(InferenceEngine):
    def __init__(self, model_name):
        self.model_name = model_name
        self.client = ollama.Client(host='http://127.0.0.1:11434')

    def generate_response(self, image_bytes, prompt):
        if not ollama:
            raise ImportError("Ollama library not found. Please install it.")
        
        # Check if we need to use the Chain Strategy (Vision -> Text)
        # This is required for small models like moondream that are good at seeing but bad at instructing.
        chain_strategy = "moondream" in self.model_name
        
        import tempfile
        import os
        
        # Save bytes to temp file
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_img:
            temp_img.write(image_bytes)
            temp_img_path = temp_img.name

        try:
            if chain_strategy:
                # STEP 1: VISION (Moondream)
                # Simple prompt for the vision model
                vision_prompt = "Describe this object and its material in detail."
                print(f"DEBUG: Running Vision Step with {self.model_name}...")
                vision_res = self.client.generate(
                    model=self.model_name,
                    prompt=vision_prompt,
                    images=[temp_img_path]
                )
                description = vision_res['response']
                print(f"DEBUG: Vision Output: {description}")
                
                # STEP 2: REASONING (Llama3)
                # We use a capable text model for the logic. 
                # We assume user has llama3 or llama3.1 from previous logs.
                reasoning_model = "llama3.1" # Default to 3.1 as seen in logs
                
                # Construct a new text-only prompt combining the system instructions and the vision description
                full_text_prompt = f"""
                CONTEXT:
                The user has uploaded an image of a waste item.
                A vision model has described it as: "{description}"
                
                YOUR TASK:
                {prompt}
                """
                
                print(f"DEBUG: Running Reasoning Step with {reasoning_model}...")
                text_res = self.client.chat(
                    model=reasoning_model,
                    messages=[{'role': 'user', 'content': full_text_prompt}]
                )
                return text_res['message']['content']

            else:
                # Standard One-Shot (for Llama 3.2 Vision or LLaVA if it works)
                response = self.client.generate(
                    model=self.model_name,
                    prompt=prompt,
                    images=[temp_img_path]
                )
                return response['response']
                
        except Exception as e:
            raise ConnectionError(f"Failed to communicate with Ollama. Error: {str(e)}")
        finally:
            if os.path.exists(temp_img_path):
                os.remove(temp_img_path)

class AirLLMEngine(InferenceEngine):
    def __init__(self, model_name):
        self.model_name = model_name
        # AirLLM usually loads the model on init
        # We might want to delay this to avoid heavy load on startup
        self.model = None

    def load_model(self):
        # Heavy import inside method
        try:
            from airllm import AutoModel
        except ImportError:
            raise ImportError("AirLLM not installed.")
        
        if not self.model:
            # Note: AirLLM is primarily for text. Vision support is limited/non-existent in core AirLLM
            # unless we use a separate vision encoder. 
            # For now, we will assume this is a TEXT-ONLY fallback or user provides description?
            # actually, user wants AirLLM for this. 
            # If the model is a Vision model (like Llama 3.2 Vision), AirLLM might support it if it's architectures align.
            # But standard AirLLM is for LLMs. 
            # We will implement a warning or text-only mode if image is passed.
            # OR we just pass text prompts. 
            
            # For this MVP, let's implement basic loading.
            self.model = AutoModel.from_pretrained(self.model_name)

    def generate_response(self, image_bytes, prompt):
        self.load_model()
        
        # TODO: AirLLM vision support. 
        # For now, we return a mock or text-only logic because AirLLM doesn't natively handle image bytes easily 
        # without custom vision tower integration.
        return "AirLLM currently supports text-only inference in this implementation. Please describe the item." 

def get_inference_engine(provider, model_name):
    if provider == "Ollama":
        return OllamaEngine(model_name)
    elif provider == "AirLLM":
        return AirLLMEngine(model_name)
    else:
        raise ValueError(f"Unknown provider: {provider}")
