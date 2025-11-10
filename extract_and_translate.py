#!/usr/bin/env python3
"""
Extract all questions, separate EN/FR, translate missing ones, and find duplicates
"""
import json
import re
from bs4 import BeautifulSoup
from pathlib import Path
from collections import defaultdict
import hashlib

# Read current quiz-data.js to get the structure
with open('quiz-data.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract the questions array
array_start = content.find('const quizData = [')
array_start = array_start + len('const quizData = ')
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
existing_questions = json.loads(json_str)

print(f"Loaded {len(existing_questions)} existing questions")

# Parse all HTML files to extract questions
html_files = [
    'source/html/MOCK 1 EXAM FOR TA.html',
    'source/html/MOCKEX 4.html',
    'source/html/model questions -french (1).html',
    'source/html/model questions -french rep.html',
    'source/html/SKCOMTEST FR - Copy.html',
]

all_questions = []
question_hashes = {}  # To detect duplicates

def normalize_text(text):
    """Normalize text for comparison"""
    if not text:
        return ""
    # Remove extra whitespace, convert to lowercase
    text = ' '.join(text.split()).lower()
    # Remove punctuation for comparison
    text = re.sub(r'[^\w\s]', '', text)
    return text

def get_question_hash(question_text, options):
    """Generate hash for question to detect duplicates"""
    normalized_q = normalize_text(question_text)
    normalized_opts = '|'.join(sorted([normalize_text(str(v)) for v in options.values()]))
    combined = f"{normalized_q}|{normalized_opts}"
    return hashlib.md5(combined.encode()).hexdigest()

def detect_language(text):
    """Simple language detection based on common words"""
    if not text:
        return 'en'
    
    french_words = ['le', 'la', 'les', 'de', 'un', 'une', 'des', 'est', 'sont', 'ou', 'et', 'dans', 'pour', 'par', 'sur', 'avec', 'bateau', 'nautique', 'navigation']
    english_words = ['the', 'a', 'an', 'is', 'are', 'of', 'in', 'to', 'for', 'with', 'vessel', 'boat', 'nautical', 'navigation']
    
    text_lower = text.lower()
    
    french_count = sum(1 for word in french_words if f' {word} ' in f' {text_lower} ')
    english_count = sum(1 for word in english_words if f' {word} ' in f' {text_lower} ')
    
    return 'fr' if french_count > english_count else 'en'

# Parse each HTML file
for html_file in html_files:
    if not Path(html_file).exists():
        continue
    
    print(f"\nParsing {html_file}...")
    
    with open(html_file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'lxml')
    
    # Find all question blocks (various formats)
    questions = soup.find_all(['div', 'p', 'table'], class_=re.compile(r'question|item', re.I))
    
    if not questions:
        # Try alternative parsing
        questions = soup.find_all('p')
    
    current_q = None
    
    for elem in soup.find_all(['p', 'div', 'span']):
        text = elem.get_text(strip=True)
        
        # Check if it's a question number
        q_match = re.match(r'^\s*(\d+)[.)\s]', text)
        if q_match:
            if current_q and current_q.get('question'):
                # Save previous question
                all_questions.append(current_q)
            
            q_num = int(q_match.group(1))
            current_q = {
                'original_num': q_num,
                'question': '',
                'options': {},
                'source_file': Path(html_file).name
            }
            # Get question text after number
            q_text = text[q_match.end():].strip()
            if q_text:
                current_q['question'] = q_text
        
        elif current_q is not None:
            # Check for options (A, B, C, D)
            opt_match = re.match(r'^([A-D])[.):\s]+(.+)', text, re.I)
            if opt_match:
                opt_key = opt_match.group(1).upper()
                opt_text = opt_match.group(2).strip()
                current_q['options'][opt_key] = opt_text
            elif not current_q['question'] and text:
                # Add to question text
                current_q['question'] = text

    # Add last question
    if current_q and current_q.get('question'):
        all_questions.append(current_q)

print(f"\nExtracted {len(all_questions)} questions from HTML files")

# Analyze and categorize questions
en_questions = []
fr_questions = []
bilingual_map = {}  # Map question numbers to both versions

for q in all_questions:
    lang = detect_language(q['question'])
    q['detected_lang'] = lang
    
    # Generate hash
    q_hash = get_question_hash(q['question'], q['options'])
    q['hash'] = q_hash
    
    if lang == 'en':
        en_questions.append(q)
    else:
        fr_questions.append(q)
    
    # Track by original number for matching
    key = (q['source_file'], q['original_num'])
    if key not in bilingual_map:
        bilingual_map[key] = {'en': None, 'fr': None}
    bilingual_map[key][lang] = q

print(f"\nFound {len(en_questions)} English questions")
print(f"Found {len(fr_questions)} French questions")

# Find duplicates
duplicates = defaultdict(list)
for q in all_questions:
    duplicates[q['hash']].append(q)

duplicate_groups = {h: qs for h, qs in duplicates.items() if len(qs) > 1}
print(f"\nFound {len(duplicate_groups)} duplicate question groups")

# Print duplicate analysis
if duplicate_groups:
    print("\n=== DUPLICATE QUESTIONS ===")
    for i, (hash_val, questions) in enumerate(duplicate_groups.items(), 1):
        print(f"\nDuplicate Group {i}:")
        for q in questions:
            print(f"  - Q{q['original_num']} ({q['detected_lang'].upper()}) from {q['source_file']}")
            print(f"    {q['question'][:80]}...")

# Create final merged question list
final_questions = []
used_hashes = set()
next_id = 1

# First, add all unique questions from existing data
print("\n=== Processing existing questions ===")
for eq in existing_questions:
    # Create bilingual entry if both EN and FR exist
    question_entry = {
        'id': next_id,
        'correctOptionKey': eq.get('correctOptionKey', 'B'),
        'translations': {
            'en': eq['translations'].get('en', {'question': '', 'options': {}}),
            'fr': eq['translations'].get('fr', {'question': '', 'options': {}}),
            'ru': {'question': '', 'options': {}}
        },
        'images': eq.get('images', [])
    }
    
    final_questions.append(question_entry)
    next_id += 1

print(f"Added {len(final_questions)} questions from existing data")

# Now add any French questions that don't have English equivalents
print("\n=== Adding French-only questions ===")
for fq in fr_questions:
    # Check if this question already exists
    if fq['hash'] in used_hashes:
        continue
    
    # Check if there's a matching English question in existing data
    found_match = False
    for eq in existing_questions:
        if eq['translations'].get('fr', {}).get('question'):
            eq_hash = get_question_hash(
                eq['translations']['fr']['question'],
                eq['translations']['fr'].get('options', {})
            )
            if eq_hash == fq['hash']:
                found_match = True
                break
    
    if not found_match:
        # Add as new question (French only for now)
        question_entry = {
            'id': next_id,
            'correctOptionKey': 'B',  # Default, needs review
            'translations': {
                'en': {
                    'question': f"[TO TRANSLATE] {fq['question'][:100]}...",
                    'options': {}
                },
                'fr': {
                    'question': fq['question'],
                    'options': fq['options']
                },
                'ru': {'question': '', 'options': {}}
            },
            'images': []
        }
        final_questions.append(question_entry)
        used_hashes.add(fq['hash'])
        next_id += 1

print(f"Total questions after adding French: {len(final_questions)}")

# Save results
output_file = 'quiz-data-merged.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(final_questions, f, indent=2, ensure_ascii=False)

print(f"\n✅ Saved merged data to {output_file}")
print(f"Total questions: {len(final_questions)}")
print(f"Duplicates found: {len(duplicate_groups)} groups")

# Generate report
report = []
report.append("# Quiz Questions Analysis Report\n")
report.append(f"Generated: {__import__('datetime').datetime.now()}\n\n")
report.append(f"## Summary\n")
report.append(f"- Total questions: {len(final_questions)}\n")
report.append(f"- English questions: {len(en_questions)}\n")
report.append(f"- French questions: {len(fr_questions)}\n")
report.append(f"- Duplicate groups: {len(duplicate_groups)}\n\n")

if duplicate_groups:
    report.append("## Duplicate Questions\n\n")
    for i, (hash_val, questions) in enumerate(duplicate_groups.items(), 1):
        report.append(f"### Group {i}\n")
        for q in questions:
            report.append(f"- Q{q['original_num']} ({q['detected_lang'].upper()}) - {q['source_file']}\n")
            report.append(f"  Question: {q['question'][:100]}...\n")
        report.append("\n")

with open('quiz-analysis-report.md', 'w', encoding='utf-8') as f:
    f.writelines(report)

print(f"✅ Saved analysis report to quiz-analysis-report.md")
