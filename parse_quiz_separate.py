#!/usr/bin/env python3
"""
Enhanced Quiz Parser - Separate Questions Version
Treats English and French questions as completely separate entities
"""

from bs4 import BeautifulSoup
from pathlib import Path
import re
import json
import hashlib

def extract_images_from_html(html_content):
    """Extract base64 encoded images from HTML"""
    images = []
    # Look for data:image base64 encoded images
    image_pattern = r'data:image/[^;]+;base64,[A-Za-z0-9+/=]+'
    matches = re.findall(image_pattern, html_content)
    
    for match in matches:
        if match not in images:
            images.append(match)
    
    return images

def parse_english_questions(soup, filename):
    """Parse English questions from HTML (h1 tags)"""
    questions = []
    h1_tags = soup.find_all('h1')
    
    for h1 in h1_tags:
        text = h1.get_text(strip=True)
        
        # Check if this looks like a question (has question number)
        if re.match(r'^\d+[.\)]\s*', text):
            # Extract question number and text
            match = re.match(r'^(\d+)[.\)]\s*(.*)', text)
            if match:
                q_num = int(match.group(1))
                q_text = match.group(2).strip()
                
                # Look for options in following elements
                options = {}
                current = h1.find_next_sibling()
                option_pattern = r'^([A-D])[.\)]\s*(.*)'
                
                while current and len(options) < 4:
                    if current.name in ['p', 'div', 'span']:
                        opt_text = current.get_text(strip=True)
                        opt_match = re.match(option_pattern, opt_text)
                        if opt_match:
                            opt_key = opt_match.group(1)
                            opt_value = opt_match.group(2).strip()
                            if opt_value:
                                options[opt_key] = opt_value
                    current = current.find_next_sibling()
                
                if q_text and options:
                    questions.append({
                        'number': q_num,
                        'question': q_text,
                        'options': options,
                        'source': filename,
                        'lang': 'en'
                    })
    
    return questions

def parse_french_questions(soup, filename):
    """Parse French questions from HTML (p tags)"""
    questions = []
    p_tags = soup.find_all('p')
    
    current_question = None
    options = {}
    
    for p in p_tags:
        text = p.get_text(strip=True)
        
        # Check if this is a question
        q_match = re.match(r'^(\d+)[.\)]\s*(.*)', text)
        if q_match:
            # Save previous question if exists
            if current_question and options:
                questions.append({
                    'number': current_question['number'],
                    'question': current_question['text'],
                    'options': options,
                    'source': filename,
                    'lang': 'fr'
                })
            
            # Start new question
            current_question = {
                'number': int(q_match.group(1)),
                'text': q_match.group(2).strip()
            }
            options = {}
        else:
            # Check if this is an option
            opt_match = re.match(r'^([A-D])[.\)]\s*(.*)', text)
            if opt_match and current_question:
                opt_key = opt_match.group(1)
                opt_value = opt_match.group(2).strip()
                if opt_value:
                    options[opt_key] = opt_value
    
    # Don't forget the last question
    if current_question and options:
        questions.append({
            'number': current_question['number'],
            'question': current_question['text'],
            'options': options,
            'source': filename,
            'lang': 'fr'
        })
    
    return questions

def create_question_hash(question_text):
    """Create a hash of the question for deduplication"""
    normalized = re.sub(r'\s+', ' ', question_text.lower().strip())
    return hashlib.md5(normalized.encode()).hexdigest()

def deduplicate_questions(questions):
    """Remove duplicate questions based on content"""
    seen_hashes = set()
    unique_questions = []
    
    for q in questions:
        q_hash = create_question_hash(q['question'])
        if q_hash not in seen_hashes:
            seen_hashes.add(q_hash)
            unique_questions.append(q)
    
    return unique_questions

def associate_images_with_questions(questions, all_images):
    """Associate images with questions based on keywords"""
    # Keywords that might indicate an image is needed
    image_keywords = [
        'compass', 'buoy', 'vessel', 'craft', 'lighthouse', 'navigation',
        'chart', 'map', 'diagram', 'picture', 'image', 'shown', 'following',
        'this magnetic', 'immatriculation', 'bateau', 'navire'
    ]
    
    for q in questions:
        q['images'] = []
        q_text_lower = q['question'].lower()
        
        # Check if question text suggests an image
        if any(keyword in q_text_lower for keyword in image_keywords):
            # Assign images (for now, assign all available images to such questions)
            # In a real scenario, you'd need more sophisticated matching
            if all_images:
                q['images'] = all_images.copy()
    
    return questions

def export_to_js(questions, output_file='quiz-data.js'):
    """Export questions to JavaScript module format"""
    
    # Create question objects
    quiz_data = []
    for idx, q in enumerate(questions, 1):
        question_obj = {
            'id': idx,
            'correctOptionKey': 'B',  # Default, needs manual review
            'translations': {
                q['lang']: {
                    'question': q['question'],
                    'options': q['options']
                }
            },
            'images': q.get('images', [])
        }
        quiz_data.append(question_obj)
    
    # App texts
    app_texts = {
        "en": {
            "title": "Trilingual Skipper Quiz",
            "question": "Question",
            "summary": "Quiz Summary",
            "score": "Your Score",
            "correct": "Correct",
            "incorrect": "Incorrect",
            "reset": "Start Over",
            "next": "Next Question",
            "finish": "Finish Quiz",
            "correctAnswer": "Correct Answer:",
            "selectedAnswer": "Your Selection:",
        },
        "fr": {
            "title": "Quiz Trilingue de Skipper",
            "question": "Question",
            "summary": "Résumé du Quiz",
            "score": "Votre Score",
            "correct": "Correct",
            "incorrect": "Incorrect",
            "reset": "Recommencer",
            "next": "Question Suivante",
            "finish": "Terminer le Quiz",
            "correctAnswer": "Bonne Réponse:",
            "selectedAnswer": "Votre Sélection:",
        },
        "ru": {
            "title": "Трехъязычный Тест Шкипера",
            "question": "Вопрос",
            "summary": "Сводка Теста",
            "score": "Ваш Счет",
            "correct": "Правильно",
            "incorrect": "Неправильно",
            "reset": "Начать Сначала",
            "next": "Следующий Вопрос",
            "finish": "Завершить Тест",
            "correctAnswer": "Правильный Ответ:",
            "selectedAnswer": "Ваш Выбор:",
        }
    }
    
    # Write to JS file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('// Auto-generated quiz data - Separate Questions Version\n')
        f.write(f'// Generated from HTML sources\n')
        f.write(f'// Total questions: {len(quiz_data)}\n')
        f.write(f'// English and French questions are kept separate\n\n')
        
        f.write('export const quizData = ')
        f.write(json.dumps(quiz_data, ensure_ascii=False, indent=2))
        f.write(';\n\n')
        
        f.write('export const appTexts = ')
        f.write(json.dumps(app_texts, ensure_ascii=False, indent=2))
        f.write(';\n\n')
        
        f.write("export const languages = ['en', 'fr', 'ru'];\n")
        f.write("export const stackedLanguages = ['fr', 'en', 'ru'];\n")
    
    print(f'Exported to {output_file}')

def main():
    html_dir = Path('source/html')
    all_questions = []
    all_images = []
    
    # Process all HTML files
    for html_file in html_dir.glob('*.html'):
        if 'answer' in html_file.name.lower():
            print(f'Skipping answer file: {html_file.name}')
            continue
        
        print(f'Processing {html_file.name}...')
        
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        soup = BeautifulSoup(html_content, 'lxml')
        
        # Extract images
        images = extract_images_from_html(html_content)
        all_images.extend(images)
        
        # Try parsing as English
        en_questions = parse_english_questions(soup, html_file.name)
        if en_questions:
            print(f'  Found {len(en_questions)} English questions')
            all_questions.extend(en_questions)
        
        # Try parsing as French
        fr_questions = parse_french_questions(soup, html_file.name)
        if fr_questions:
            print(f'  Found {len(fr_questions)} French questions')
            all_questions.extend(fr_questions)
        
        if images:
            print(f'  Found {len(images)} images')
    
    # Remove duplicate images
    all_images = list(set(all_images))
    print(f'\nTotal unique images: {len(all_images)}')
    
    # Deduplicate questions
    print(f'Total questions before deduplication: {len(all_questions)}')
    all_questions = deduplicate_questions(all_questions)
    print(f'Total questions after deduplication: {len(all_questions)}')
    
    # Associate images with questions
    all_questions = associate_images_with_questions(all_questions, all_images)
    
    # Count questions with images
    questions_with_images = sum(1 for q in all_questions if q.get('images'))
    print(f'Questions with images: {questions_with_images}')
    
    # Export to JavaScript
    export_to_js(all_questions)

if __name__ == '__main__':
    main()
