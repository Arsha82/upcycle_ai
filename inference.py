import os
# import try_import_airllm # placeholder removed
try:
    import ollama
except ImportError:
    ollama = None
except ImportError:
    ollama = None

class InferenceEngine:
    def generate_response(self, image_bytes, prompt, use_rag=False):
        raise NotImplementedError

class OllamaEngine(InferenceEngine):
    def __init__(self, model_name):
        self.model_name = model_name
        self.client = ollama.Client(host='http://127.0.0.1:11434')

    def run_vision(self, image_bytes):
        """Interactive Step 1: Just run vision and return comma-separated objects."""
        if not ollama:
            raise ImportError("Ollama library not found.")
        
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_img:
            temp_img.write(image_bytes)
            temp_img_path = temp_img.name

        try:
            # Prompt specifically asks for a COMMA SEPARATED list of items
            vision_prompt = "Identify all distinct objects, loose items, and materials visible in this image. Return the result STRICTLY as a simple comma-separated list. Do not include sentences."
            print(f"DEBUG: Running Interactive Vision Step with {self.model_name}...")
            vision_res = self.client.generate(
                model=self.model_name,
                prompt=vision_prompt,
                images=[temp_img_path]
            )
            return vision_res['response']
        finally:
            if os.path.exists(temp_img_path):
                os.remove(temp_img_path)

    def run_reasoning(self, selected_items, equipment, prompt, use_rag=False):
        """Interactive Step 2: Run reasoning based on explicit user choices and equipment."""
        if not ollama:
            raise ImportError("Ollama library not found.")
            
        # Treat the selected items list as our new "description"
        description = ", ".join(selected_items) if isinstance(selected_items, list) else selected_items
        rag_context = ""
        
        if use_rag:
            from rag_utils import get_rag_manager
            print("DEBUG: Querying Vector DB for user-selected items...")
            rag_manager = get_rag_manager()
            
            # Cache check
            cached_text = rag_manager.find_exact_match(description, threshold=0.15)
            if cached_text:
                return f"⚡ **[CACHE HIT]** ⚡\n\nWe instantly recognized this exact combination!\n\n{cached_text}"

            snippets = rag_manager.query(description, n_results=3)
            if snippets:
                rag_context = "\n--- RELEVANT KNOWLEDGE BASE SNIPPETS ---\n"
                for idx, snip in enumerate(snippets):
                    rag_context += f"Snippet {idx+1}:\n{snip}\n\n"
                rag_context += "------------------------------------------\n"

        reasoning_model = "llama3.1"
        
        equipment_text = ""
        if equipment and equipment.strip():
            equipment_text = f"The user explicitly stated they only have the following equipment available: {equipment.strip()}"
        else:
            equipment_text = "The user has not specified any equipment, so assume basic household tools."

        full_text_prompt = f"""
        CONTEXT:
        The user wants to upcycle the following specific items: "{description}"
        {equipment_text}
        
        {rag_context}
        
        YOUR TASK:
        {prompt}
        
        IMPORTANT: 
        1. Only suggest projects requiring the equipment listed, or very basic tools.
        2. If there are RELEVANT KNOWLEDGE BASE SNIPPETS provided above, highly prioritize using ideas, instructions, and information from those snippets in your response!
        """
        
        print(f"DEBUG: Running Interactive Reasoning Step with {reasoning_model}...")
        text_res = self.client.chat(
            model=reasoning_model,
            messages=[{'role': 'user', 'content': full_text_prompt}]
        )
        
        final_output = text_res['message']['content']
        
        if use_rag:
            from rag_utils import get_rag_manager
            rag_manager = get_rag_manager()
            rag_manager.add_generated_idea(description, final_output)
            
        return final_output

    def generate_response(self, image_bytes, prompt, use_rag=False):
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
                
                # OPTIONAL RAG STEP & CACHING:
                rag_context = ""
                if use_rag:
                    from rag_utils import get_rag_manager
                    
                    print("DEBUG: Querying Vector DB for related upcycling ideas...")
                    rag_manager = get_rag_manager()
                    
                    # 1. CACHE CHECK: Did we already generate ideas for this exact same object type?
                    # E.g., if vision description is highly similar to a past scan.
                    cached_text = rag_manager.find_exact_match(description, threshold=0.15)
                    if cached_text:
                        print("DEBUG: ⚡ CACHE HIT! Found highly similar past scan. Skipping Llama generation.")
                        return f"⚡ **[CACHE HIT]** ⚡\n\nWe instantly recognized this item from our Knowledge Base!\n\n{cached_text}"

                    # 2. RAG CONTEXT: If no exact match, grab general knowledge for context
                    snippets = rag_manager.query(description, n_results=3)
                    
                    if snippets:
                        rag_context = "\n--- RELEVANT KNOWLEDGE BASE SNIPPETS ---\n"
                        for idx, snip in enumerate(snippets):
                            rag_context += f"Snippet {idx+1}:\n{snip}\n\n"
                        rag_context += "------------------------------------------\n"
                        print("DEBUG: Context found and injected into prompt.")
                    else:
                        print("DEBUG: Vector DB returned no results.")

                # STEP 2: REASONING (Llama3)
                # We use a capable text model for the logic. 
                # We assume user has llama3 or llama3.1 from previous logs.
                reasoning_model = "llama3.1" # Default to 3.1 as seen in logs
                
                # Construct a new text-only prompt combining the system instructions and the vision description
                full_text_prompt = f"""
                CONTEXT:
                The user has uploaded an image of a waste item.
                A vision model has described it as: "{description}"
                
                {rag_context}
                
                YOUR TASK:
                {prompt}
                
                IMPORTANT INSTRUCTION: If there are RELEVANT KNOWLEDGE BASE SNIPPETS provided above, highly prioritize using ideas, instructions, and information from those snippets in your response!
                """
                
                print(f"DEBUG: Running Reasoning Step with {reasoning_model}...")
                text_res = self.client.chat(
                    model=reasoning_model,
                    messages=[{'role': 'user', 'content': full_text_prompt}]
                )
                
                final_output = text_res['message']['content']
                
                # FEEDBACK LOOP: Save this high-quality idea back into the DB for future cache hits
                if use_rag:
                    # We save the generated text, keyed by the vision description
                    rag_manager.add_generated_idea(description, final_output)
                    print("DEBUG: Feedback loop complete. Saved generated instructions to Knowledge Base.")
                    
                return final_output

            else:
                # Standard One-Shot (for Llama 3.2 Vision or LLaVA if it works)
                
                # To support RAG here, we would need to run vision FIRST or do two passes.
                # For MVP, one-shot with RAG without knowing what's in the image is hard.
                # We will just pass the standard prompt.
                 
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

    def generate_response(self, image_bytes, prompt, use_rag=False):
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
