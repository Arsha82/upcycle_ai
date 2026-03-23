import os

# import try_import_airllm # placeholder removed
try:
    import ollama
except ImportError:
    ollama = None
except ImportError:
    ollama = None

class InferenceEngine:
    def generate_response(self, image_bytes, prompt, use_rag=False, chat_only=False):
        raise NotImplementedError

class OllamaEngine(InferenceEngine):
    def __init__(self, model_name):
        self.model_name = model_name
        self.client = ollama.Client(host='http://127.0.0.1:11434')

    def run_vision(self, image_bytes):
        """Interactive Step 1: Just run vision and return comma-separated objects."""
        if not ollama:
            raise ImportError("Ollama library not found.")
        
        # CRITICAL FIX: The Python Ollama client fails on Windows filepaths 
        # by trying to decode the ASCII path string. However, passing a base64 string causes it 
        # to try os.path.exists(), which throws WinError 206 (path too long).
        # We must explicitly pass `image_bytes` (a Python bytes object) directly.

        import base64
        # CRITICAL FIX: Explicitly encode to a b64 string. Passing raw `bytes` directly
        # into the Ollama Python SDK causes httpx to infinitely hang on Windows during chunked uploads!
        b64_img = base64.b64encode(image_bytes).decode('utf-8')

        try:
            # We revert back to the robust 2-step strategy. Highly quantized legacy VLMs like moondream 
            # will literally infinite loop / hang eternally if forced to adhere to complex JSON Schema logits.
            vision_prompt = "Describe the main objects, items, and material compositions you see in this image in high detail."
            print(f"DEBUG: Running Natural Vision Step with {self.model_name}...")
            vision_res = self.client.generate(
                model=self.model_name,
                prompt=vision_prompt,
                images=[b64_img],
                options={"temperature": 0.0}
            )
            vision_desc = vision_res['response']
            print(f"DEBUG: Vision Original Core Output: {vision_desc}")
            
            # Step 2: Safe structure extraction via Qwen
            reasoning_model = "qwen2.5:1.5b"
            format_prompt = f"Extract a comma-separated list of the 2 to 4 most prominent physical/recyclable objects from this visual description: '{vision_desc}'. Reply ONLY with the comma-separated words. No intro sentences."
            
            print(f"DEBUG: Extracting CSV schema via {reasoning_model}...")
            text_res = self.client.chat(
                model=reasoning_model,
                messages=[{'role': 'user', 'content': format_prompt}],
                options={"temperature": 0.0}
            )
            
            clean_text = text_res['message']['content']
            import re
            clean_text = re.sub(r'[\[\]]', '', clean_text)
            return clean_text.strip()
            
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Ollama. Error: {str(e)}")

    def run_reasoning(self, selected_items, equipment, prompt, use_rag=False):
        """Interactive Step 2: Run reasoning based on explicit user choices and equipment."""
        if not ollama:
            raise ImportError("Ollama library not found.")
            
        # Treat the selected items list as our new "description"
        description = ", ".join(selected_items) if isinstance(selected_items, list) else selected_items
        rag_context = ""
        
        if use_rag:
            try:
                from rag_utils import get_rag_manager
                print("DEBUG: Querying Vector DB for user-selected items...")
                rag_manager = get_rag_manager()
                
                # Cache check
                cached_text = rag_manager.find_exact_match(description, threshold=0.15)
                if cached_text:
                    yield f"⚡ **[CACHE HIT]** ⚡\n\nWe instantly recognized this exact combination!\n\n{cached_text}"
                    return

                snippets = rag_manager.query(description, n_results=3)
                if snippets:
                    rag_context = "\n--- RELEVANT KNOWLEDGE BASE SNIPPETS ---\n"
                    for idx, snip in enumerate(snippets):
                        rag_context += f"Snippet {idx+1}:\n{snip}\n\n"
                    rag_context += "------------------------------------------\n"
            except Exception:
                pass

        reasoning_model = "qwen2.5:1.5b"
        
        equipment_text = ""
        if equipment and equipment.strip():
            equipment_text = f"The user explicitly stated they only have the following equipment available: {equipment.strip()}"
        else:
            equipment_text = "The user has not specified any equipment, so assume basic household tools."

        base_prompt = f"""
CONTEXT:
The user wants to upcycle: "{description}"
{equipment_text}

{rag_context}
YOUR STRICT TASK:
You are a highly creative upcycling expert. Read the RELEVANT KNOWLEDGE BASE SNIPPETS above (if any).
"""
        
        print(f"DEBUG: Running Interactive Reasoning Step with {reasoning_model}...")
        
        previous_ideas = []
        try:
            for i in range(1, 4):
                if i > 1:
                    yield "|||IDEA_SEPARATOR|||"
                
                req_prompt = base_prompt + f"\nInvent ONE highly creative DIY upcycling project (Idea #{i}).\n"
                
                if previous_ideas:
                    req_prompt += f"DO NOT completely duplicate these ideas you already created: {', '.join(previous_ideas)}\n"
                    
                req_prompt += "Format explicitly with a clear Markdown Heading (## Title), Required Tools, Materials, and step-by-step Instructions.\n"
                req_prompt += "DO NOT output any random asterisks (**) or separators outside of your core idea text."

                stream = self.client.chat(
                    model=reasoning_model,
                    messages=[{'role': 'user', 'content': req_prompt}],
                    stream=True,
                    options={"temperature": 0.7}
                )
                
                full_idea = ""
                for chunk in stream:
                    content = chunk['message']['content']
                    full_idea += content
                    yield content
                    
                # Extract a title explicitly for the exclusion list safely
                idea_title = full_idea.split('\n')[0].replace('#', '').replace('*', '').strip()
                if idea_title:
                    previous_ideas.append(idea_title)
                    
        except Exception as e:
            yield f"Error generating ideas: {str(e)}"

    def generate_response(self, image_bytes, prompt, use_rag=False, chat_only=False):
        if not ollama:
            raise ImportError("Ollama library not found. Please install it.")
        
        if chat_only:
            reasoning_model = "qwen2.5:1.5b"
            text_res = self.client.chat(
                model=reasoning_model,
                messages=[{'role': 'user', 'content': prompt}],
                keep_alive="1h",
                stream=True
            )
            def generate_chat():
                for chunk in text_res:
                    yield chunk['message']['content']
            return generate_chat()
        
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

                # STEP 2: REASONING (Qwen 2.5 1.5B)
                # We use an ultra-fast small model to format the output.
                reasoning_model = "qwen2.5:1.5b" 
                
                full_text_prompt = f"""
                CONTEXT:
                The user has an image containing: "{description}"
                
                {rag_context}
                
                YOUR STRICT TASK:
                You are a formatter. Do NOT invent new projects. 
                Read the RELEVANT KNOWLEDGE BASE SNIPPETS above. 
                Pick the ONE best project from those snippets.
                Format that project nicely into a markdown step-by-step guide with tools, materials, and steps.
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

    def generate_response(self, image_bytes, prompt, use_rag=False, chat_only=False):
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
