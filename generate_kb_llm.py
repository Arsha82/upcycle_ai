import ollama
import json
import csv
import os
import random
import time

MATERIALS = [
    {"material": "Plastic Bottle", "vision_target": "clear, plastic, empty, water bottle, crushed bottle, transparent plastic"},
    {"material": "Glass Jar", "vision_target": "glass jar, mason jar, clear glass container, empty jam jar, transparent cylinder"},
    {"material": "Cardboard Box", "vision_target": "cardboard, brown box, corrugated cardboard, shipping box, folded carton"},
    {"material": "Tin Can", "vision_target": "metal can, tin can, aluminum can, soup can, ridged metal cylinder"},
    {"material": "Old T-Shirt", "vision_target": "fabric, t-shirt, cotton shirt, old clothing, cloth, textile fabric"},
    {"material": "Wood Pallet", "vision_target": "wood, pallet, wooden planks, timber, slatted wood, rustic boards"},
    {"material": "Newspaper", "vision_target": "paper, newspaper, newsprint, crumpled paper, torn pages, text printed paper"},
    {"material": "Wine Cork", "vision_target": "cork, wine cork, wooden stopper, cylinder corks, pile of corks"},
    {"material": "Egg Carton", "vision_target": "egg carton, cardboard egg tray, molded pulp, empty egg box"},
    {"material": "Pencil Shavings", "vision_target": "wood shavings, pencil shavings, colored pencil tips, thin wood curves"},
    {"material": "CDs/DVDs", "vision_target": "cd, dvd, compact disc, shiny disc, optical disc, reflective circle"},
    {"material": "Coffee Grounds", "vision_target": "coffee grounds, wet brown powder, dirt-like powder, used espresso"},
    {"material": "Denim Jeans", "vision_target": "denim, blue jeans, torn jeans, fabric, blue cloth, heavy textile"}
]

PROMPT_TEMPLATE = """You are an expert DIY Crafting and Upcycling Assistant.
Generate a highly detailed, uniquely creative 500-word upcycling project guide for a person who wants to upcycle a {material}.

You MUST return your response as a strictly valid JSON object. Do not include any nested objects or arrays. All values MUST be flat strings.

The JSON MUST exactly match this format:
{{
  "Project Idea": "A creative, catchy title string for the project.",
  "Difficulty": "Easy, Intermediate, or Advanced",
  "Time to Complete": "45 minutes",
  "Instructions": "A highly detailed, verbose step-by-step masterclass guide (around 500 words) as a single long string."
}}

Make sure the project is significantly different from typical ideas for this material. Be extremely creative.
"""

def main():
    csv_file = "upcycle_knowledge_llm.csv"
    target_rows = 767
    
    start_id = 1
    if os.path.exists(csv_file):
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
            if len(rows) > 0:
                start_id = len(rows) # If 1 header row, next ID is 1. If 1 header + 5 rows, len is 6, next ID is 6.
    
    if start_id == 1:
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['ID', 'Material', 'Vision Description Target', 'Project Idea', 'Difficulty', 'Time to Complete', 'Instructions'])
    
    print(f"Starting generation at ID {start_id}...")
    
    client = ollama.Client()
    model_name = "llama3.1:8b" # Adjust if your local model is named differently (like llama3 or llama3.1)
    
    # Verify model connection first
    try:
        client.list()
    except Exception as e:
        print(f"Failed to connect to Ollama. Make sure Ollama is running. Error: {e}")
        return

    i = start_id
    while i <= target_rows:
        item = random.choice(MATERIALS)
        prompt = PROMPT_TEMPLATE.format(material=item["material"])
        
        success = False
        attempts = 0
        while not success and attempts < 3:
            print(f"Generating row {i}/{target_rows} for {item['material']} (Attempt {attempts+1}/3)...")
            try:
                res = client.chat(model=model_name, messages=[{'role': 'user', 'content': prompt}], format='json')
                
                content = res['message']['content']
                data = json.loads(content)
                
                if "Project Idea" in data and "Difficulty" in data and "Time to Complete" in data and "Instructions" in data:
                    with open(csv_file, 'a', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerow([
                            i,
                            item['material'],
                            item['vision_target'],
                            data['Project Idea'],
                            data['Difficulty'],
                            data['Time to Complete'],
                            data['Instructions']
                        ])
                    print(f"  ✓ Saved: {data['Project Idea']}")
                    success = True
                else:
                    print(f"  ✗ Invalid JSON keys. Retrying...")
                    attempts += 1
            except Exception as e:
                print(f"  ✗ Error generating/parsing JSON: {e}")
                attempts += 1
                time.sleep(2)
                
        if success:
            i += 1
        else:
            print(f"Failed to cleanly generate row {i}. Trying a different material.")
            time.sleep(2)

if __name__ == "__main__":
    main()
