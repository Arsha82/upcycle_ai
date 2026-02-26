import random
import csv
import os

materials = ["Plastic Bottle", "Glass Jar", "Cardboard Box", "Tin Can", "Old T-Shirt", "Wood Pallet", "Newspaper", "CDs/DVDs", "Egg Carton", "Wine Cork"]
difficulties = ["Easy", "Intermediate", "Advanced"]

def generate_instructions():
    # Simple template-based instruction generation for synthetic data
    verbs = ["Cut", "Clean", "Paint", "Glue", "Attach", "Fold", "Assemble"]
    parts = ["the base", "the top", "the sides", "the decorative pieces", "the main body"]
    
    steps = []
    num_steps = random.randint(3, 6)
    for i in range(1, num_steps + 1):
        step = f"Step {i}: {random.choice(verbs)} {random.choice(parts)} carefully."
        steps.append(step)
    
    return "\n".join(steps)

def generate_entry(index):
    material = random.choice(materials)
    
    # Generate a dummy project name
    adjectives = ["Rustic", "Modern", "Minimalist", "Colorful", "Hanging", "Decorative", "Functional"]
    items = ["Planter", "Organizer", "Lamp", "Bird Feeder", "Storage Box", "Wall Art", "Coaster"]
    project_idea = f"{random.choice(adjectives)} {material} {random.choice(items)}"
    
    difficulty = random.choice(difficulties)
    time_to_complete = f"{random.randint(10, 120)} minutes"
    instructions = generate_instructions()
    
    return {
        "ID": index,
        "Material": material,
        "Project Idea": project_idea,
        "Difficulty": difficulty,
        "Time to Complete": time_to_complete,
        "Instructions": instructions
    }

def main():
    output_file = "upcycle_knowledge.csv"
    num_rows = 150
    
    # Generate data
    data = [generate_entry(i) for i in range(1, num_rows + 1)]
    
    # Write to CSV
    keys = data[0].keys()
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        dict_writer = csv.DictWriter(f, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)
        
    print(f"Generated {num_rows} rows of Knowledge Base data to {output_file}")

if __name__ == "__main__":
    main()
