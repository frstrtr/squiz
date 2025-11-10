#!/usr/bin/env python3
"""
Enhanced Quiz Parser - Extract questions from HTML files with better accuracy
Handles English, French, and Russian questions with images
"""

import re
import json
from pathlib import Path
from bs4 import BeautifulSoup
from collections import defaultdict
import hashlib

def clean_text(text):
    """Clean and normalize text"""
    if not text:
        return ""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special formatting characters
    text = text.strip()
    return text

def extract_images_from_html(soup):
    """Extract all base64 encoded images"""
    images = []
    for img in soup.find_all('img'):
        src = img.get('src', '')
        if src.startswith('data:image'):
            images.append(src)
    return images

def parse_english_questions(html_content):
    """Parse English questions from HTML"""
    soup = BeautifulSoup(html_content, 'html.parser')
    questions = []
    images = extract_images_from_html(soup)
    
    # Find all h1 tags that contain questions
    h1_tags = soup.find_all('h1')
    
    current_question = None
    for h1 in h1_tags:
        text = clean_text(h1.get_text())
        
        # Check if this is a question header
        question_match = re.search(r'Question\s+(\d+)', text, re.IGNORECASE)
        if question_match:
            if current_question:
                questions.append(current_question)
            
            q_num = int(question_match.group(1))
            # Extract question text after the number
            question_text = text[question_match.end():].strip()
            
            # Extract options
            options = {}
            option_pattern = r'\b([ABCD])\s+(.+?)(?=\s+[ABCD]\s+|$)'
            for match in re.finditer(option_pattern, question_text, re.DOTALL):
                key = match.group(1)
                value = clean_text(match.group(2))
                if value:
                    options[key] = value
            
            # Clean question text (remove options)
            if options:
                first_option_match = re.search(r'\b[ABCD]\s+', question_text)
                if first_option_match:
                    question_text = question_text[:first_option_match.start()].strip()
            
            current_question = {
                'number': q_num,
                'question': question_text,
                'options': options,
                'language': 'en',
                'images': []  # Will be populated later
            }
    
    if current_question:
        questions.append(current_question)
    
    return questions, images

def parse_french_questions(html_content):
    """Parse French questions from HTML"""
    soup = BeautifulSoup(html_content, 'html.parser')
    questions = []
    images = extract_images_from_html(soup)
    
    # Find all paragraphs with class containing question markers
    all_p_tags = soup.find_all('p')
    
    current_question = None
    current_question_num = None
    current_question_text = []
    current_options = {}
    
    for p in all_p_tags:
        text = clean_text(p.get_text())
        
        # Check if this is a question number
        question_match = re.match(r'Question\s+(\d+)', text, re.IGNORECASE)
        if question_match:
            # Save previous question
            if current_question_num and current_question_text:
                questions.append({
                    'number': current_question_num,
                    'question': ' '.join(current_question_text),
                    'options': current_options,
                    'language': 'fr'
                })
            
            # Start new question
            current_question_num = int(question_match.group(1))
            current_question_text = []
            current_options = {}
            continue
        
        # Check if this is an option
        option_match = re.match(r'^([ABCD])\s+(.+)', text)
        if option_match and current_question_num:
            key = option_match.group(1)
            value = clean_text(option_match.group(2))
            current_options[key] = value
        elif text and current_question_num and not current_options:
            # This is question text
            current_question_text.append(text)
    
    # Save last question
    if current_question_num and current_question_text:
        questions.append({
            'number': current_question_num,
            'question': ' '.join(current_question_text),
            'options': current_options,
            'language': 'fr'
        })
    
    return questions, images

def create_question_hash(question_text):
    """Create a hash from question text for deduplication"""
    # Normalize text: lowercase, remove extra spaces, special chars
    normalized = re.sub(r'\s+', ' ', question_text.lower())
    normalized = re.sub(r'[^\w\s]', '', normalized)
    return hashlib.md5(normalized.encode()).hexdigest()[:16]

def find_correct_answer(question_text, options):
    """Try to determine the correct answer from context clues"""
    # This is a heuristic - needs manual review
    # For now, just return 'B' as default
    return 'B'

def merge_translations(questions_by_lang):
    """Merge questions from different languages into unified structure"""
    merged = []
    
    # Group by question number
    by_number = defaultdict(dict)
    max_q_num = 0
    
    for lang, questions in questions_by_lang.items():
        for q in questions:
            q_num = q['number']
            by_number[q_num][lang] = q
            max_q_num = max(max_q_num, q_num)
    
    # Create merged structure
    for q_num in range(1, max_q_num + 1):
        if q_num not in by_number:
            continue
        
        translations = by_number[q_num]
        
        merged_q = {
            'id': q_num,
            'correctOptionKey': 'B',  # Default - needs manual review
            'translations': {},
            'images': []
        }
        
        for lang, q_data in translations.items():
            if q_data['options']:  # Only include if has options
                merged_q['translations'][lang] = {
                    'question': q_data['question'],
                    'options': q_data['options']
                }
        
        # Only add if we have at least one translation with options
        if merged_q['translations']:
            merged.append(merged_q)
    
    return merged

def associate_images_with_questions(questions, images):
    """Associate images with appropriate questions"""
    # Simple approach: distribute images evenly among questions that might need them
    # Questions with navigation, boats, buoys, etc. are likely to have images
    
    image_keywords = ['buoy', 'bouée', 'vessel', 'bateau', 'lighthouse', 'phare', 
                     'craft', 'navire', 'compass', 'compas']
    
    image_idx = 0
    for q in questions:
        for lang, trans in q['translations'].items():
            question_lower = trans['question'].lower()
            if any(keyword in question_lower for keyword in image_keywords):
                if image_idx < len(images):
                    q['images'].append(images[image_idx])
                    image_idx += 1
                break
    
    return questions

def process_all_html_files():
    """Process all HTML files in the source directory"""
    source_dir = Path('source/html')
    
    questions_by_lang = {
        'en': [],
        'fr': [],
        'ru': []
    }
    
    all_images = []
    
    # Process English files
    en_files = [
        'MOCK 1 EXAM FOR TA.html',
        'MOCKEX 4.html',
        'SAMPLE QUESTIONS FROM MY UPCOMING   BOOK.html',
    ]
    
    for filename in en_files:
        filepath = source_dir / filename
        if filepath.exists():
            print(f"Processing {filename}...")
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            questions, images = parse_english_questions(content)
            print(f"  Found {len(questions)} questions, {len(images)} images")
            questions_by_lang['en'].extend(questions)
            all_images.extend(images)
    
    # Process French files
    fr_files = [
        'model questions -french (1).html',
        'SKCOMTEST FR - Copy.html'
    ]
    
    for filename in fr_files:
        filepath = source_dir / filename
        if filepath.exists():
            print(f"Processing {filename}...")
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            questions, images = parse_french_questions(content)
            print(f"  Found {len(questions)} questions, {len(images)} images")
            questions_by_lang['fr'].extend(questions)
            all_images.extend(images)
    
    # Merge translations
    print("\nMerging translations...")
    merged_questions = merge_translations(questions_by_lang)
    
    # Associate images
    print("Associating images with questions...")
    unique_images = list(set(all_images))
    merged_questions = associate_images_with_questions(merged_questions, unique_images)
    
    return merged_questions, unique_images

def export_to_js(questions, images, output_path='quiz-data.js'):
    """Export questions to JavaScript format"""
    
    js_content = f"""// Auto-generated quiz data
// Generated from HTML sources
// Total questions: {len(questions)}
// Total images: {len(images)}

export const quizData = {json.dumps(questions, indent=2, ensure_ascii=False)};

export const appTexts = {{
  en: {{
    title: "Trilingual Skipper Quiz",
    question: "Question",
    summary: "Quiz Summary",
    score: "Your Score",
    correct: "Correct",
    incorrect: "Incorrect",
    reset: "Start Over",
    next: "Next Question",
    finish: "Finish Quiz",
    correctAnswer: "Correct Answer:",
    selectedAnswer: "Your Selection:",
  }},
  fr: {{
    title: "Quiz Trilingue de Skipper",
    question: "Question",
    summary: "Résumé du Quiz",
    score: "Votre Score",
    correct: "Correct",
    incorrect: "Incorrect",
    reset: "Recommencer",
    next: "Question Suivante",
    finish: "Terminer le Quiz",
    correctAnswer: "Bonne Réponse:",
    selectedAnswer: "Votre Sélection:",
  }},
  ru: {{
    title: "Трехъязычный Тест Шкипера",
    question: "Вопрос",
    summary: "Сводка Теста",
    score: "Ваш Счет",
    correct: "Правильно",
    incorrect: "Неправильно",
    reset: "Начать Сначала",
    next: "Следующий Вопрос",
    finish: "Завершить Тест",
    correctAnswer: "Правильный Ответ:",
    selectedAnswer: "Ваш Выбор:",
  }}
}};

export const languages = ['en', 'fr', 'ru'];
export const stackedLanguages = ['fr', 'en', 'ru'];
"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(js_content)
    
    print(f"\nExported {len(questions)} questions to {output_path}")
    print(f"Included {len(images)} unique images")

if __name__ == '__main__':
    print("=" * 60)
    print("Enhanced Quiz Parser")
    print("=" * 60)
    print("\nExtracting questions from HTML files...\n")
    
    questions, images = process_all_html_files()
    
    print(f"\n{'=' * 60}")
    print(f"SUMMARY")
    print(f"{'=' * 60}")
    print(f"Total questions extracted: {len(questions)}")
    print(f"Total unique images: {len(images)}")
    print(f"Questions with images: {sum(1 for q in questions if q.get('images'))}")
    
    export_to_js(questions, images)
    print("\nDone!")
