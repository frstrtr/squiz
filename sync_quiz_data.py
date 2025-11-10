#!/usr/bin/env python3
"""
Sync quiz-data.js from quiz-data-final.json
Generates an import-based JS file with image imports
"""
import json
import re
from pathlib import Path

# Read the canonical JSON
with open('quiz-data-final.json', 'r', encoding='utf-8') as f:
    quiz_data = json.load(f)

# Collect all unique image paths
image_imports = {}
for question in quiz_data:
    for img_path in question.get('images', []):
        if img_path.startswith('assets/'):
            # Create import name: assets/q2_0.png -> img_q2_0
            base_name = Path(img_path).stem  # q2_0
            import_name = f"img_{base_name}"
            image_imports[img_path] = import_name

# Generate the JS file
output_lines = [
    "// Auto-generated quiz data (imports for image assets)",
    "// Generated from quiz-data-final.json",
]

# Add imports
for img_path in sorted(image_imports.keys()):
    import_name = image_imports[img_path]
    output_lines.append(f"import {import_name} from './{img_path}';")

output_lines.append("")
output_lines.append("export const quizData = [")

# Process each question
for i, question in enumerate(quiz_data):
    # Replace image paths with import variables
    question_copy = question.copy()
    if question_copy.get('images'):
        question_copy['images'] = [
            image_imports.get(img, img) 
            for img in question_copy['images']
        ]
    
    # Convert to JSON string and indent
    json_str = json.dumps(question_copy, indent=2, ensure_ascii=False)
    # Add proper indentation for array items
    indented = '\n'.join('  ' + line for line in json_str.split('\n'))
    output_lines.append(indented)
    
    # Add comma except for last item
    if i < len(quiz_data) - 1:
        output_lines[-1] += ","

output_lines.append("];")

# Write output
with open('quiz-data.js', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output_lines))

print(f"✓ Generated quiz-data.js with {len(quiz_data)} questions")
print(f"✓ Added {len(image_imports)} image imports")
