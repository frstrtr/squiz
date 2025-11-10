#!/usr/bin/env python3
import json
import re

# Read the file
with open('quiz-data.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract just the questions array
# Find start of array
array_start = content.find('const quizData = [')
if array_start == -1:
    print("Could not find quiz data start")
    exit(1)

array_start = array_start + len('const quizData = ')

# Find the matching closing bracket for the array
bracket_count = 0
in_array = False
array_end = array_start

for i in range(array_start, len(content)):
    char = content[i]
    if char == '[':
        bracket_count += 1
        in_array = True
    elif char == ']' and in_array:
        bracket_count -= 1
        if bracket_count == 0:
            array_end = i + 1
            break

json_str = content[array_start:array_end]
questions = json.loads(json_str)

# Find and fix Question 2
for i, q in enumerate(questions):
    if q['id'] == 2:
        # Fix Question 2 - English compass question only
        questions[i] = {
            "id": 2,
            "correctOptionKey": "A",  # 345 C is the correct answer
            "translations": {
                "en": {
                    "question": "When reporting the position of your craft at sea by the use of this magnetic compass, you need to mention the correct direction with respect to the lighthouse as",
                    "options": {
                        "A": "345 C",
                        "B": "185 C",
                        "C": "350 C",
                        "D": "165 C"
                    }
                },
                "ru": {
                    "question": "",
                    "options": {}
                }
            },
            "images": q.get('images', [])
        }
        print("✓ Fixed Question 2:")
        print("  - Set English compass question with all 4 options")
        print("  - Changed correctOptionKey to 'A' (345 C)")
        print("  - Removed French boat registration question (different question)")
        break

# Keep the rest of the file after the questions array
rest_of_file = content[array_end:]

# Write back
output = f"// Auto-generated quiz data\nconst quizData = {json.dumps(questions, indent=2, ensure_ascii=False)};\n{rest_of_file[1:]}"  # Skip the semicolon
with open('quiz-data.js', 'w', encoding='utf-8') as f:
    f.write(output)

print(f"\nTotal questions: {len(questions)}")
print("File updated successfully!")
