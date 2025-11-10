#!/usr/bin/env python3
"""
Quiz Parser - Extract questions from HTML files
Handles English, French, and Russian questions with images
"""

import re
import json
from pathlib import Path
from html.parser import HTMLParser
from collections import defaultdict
import hashlib

class QuestionExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.questions = []
        self.current_question = None
        self.current_text = []
        self.in_question = False
        self.in_option = False
        self.current_option_key = None
        self.question_number = None
        self.current_lang = None
        self.images = []
        
    def handle_starttag(self, tag, attrs):
        # Extract images (base64 encoded)
        if tag == 'img':
            for attr_name, attr_value in attrs:
                if attr_name == 'src' and attr_value.startswith('data:image'):
                    self.images.append(attr_value)
    
    def handle_data(self, data):
        text = data.strip()
        if text:
            self.current_text.append(text)
    
    def extract_questions_from_html(self, html_content, lang='en'):
        """Extract questions from HTML content"""
        self.current_lang = lang
        self.feed(html_content)
        return self.parse_text_questions()
    
    def parse_text_questions(self):
        """Parse questions from accumulated text"""
        full_text = ' '.join(self.current_text)
        
        # Split by Question markers
        question_pattern = r'Question\s+(\d+)'
        parts = re.split(question_pattern, full_text, flags=re.IGNORECASE)
        
        questions = []
        for i in range(1, len(parts), 2):
            q_num = parts[i]
            q_text = parts[i+1] if i+1 < len(parts) else ""
            
            # Extract question text and options
            question_data = self.parse_single_question(q_text, q_num)
            if question_data:
                questions.append(question_data)
        
        return questions
    
    def parse_single_question(self, text, q_num):
        """Parse a single question with options"""
        # Match options A, B, C, D
        option_pattern = r'([ABCD])\s+([^ABCD]+?)(?=\s*[ABCD]\s+|$)'
        matches = re.findall(option_pattern, text, re.DOTALL)
        
        if not matches:
            return None
        
        # First part before options is the question
        first_option_pos = text.find(matches[0][0])
        question_text = text[:first_option_pos].strip()
        
        options = {}
        for key, value in matches:
            options[key.strip()] = value.strip()
        
        return {
            'number': int(q_num),
            'question': question_text,
            'options': options,
            'language': self.current_lang
        }


def extract_from_french_html(html_path):
    """Extract French questions"""
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    extractor = QuestionExtractor()
    questions = extractor.extract_questions_from_html(content, 'fr')
    
    return questions, extractor.images


def extract_from_english_html(html_path):
    """Extract English questions"""
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    extractor = QuestionExtractor()
    questions = extractor.extract_questions_from_html(content, 'en')
    
    return questions, extractor.images


def create_question_hash(question_text):
    """Create a hash from question text for deduplication"""
    # Normalize text: lowercase, remove extra spaces, special chars
    normalized = re.sub(r'\s+', ' ', question_text.lower())
    normalized = re.sub(r'[^\w\s]', '', normalized)
    return hashlib.md5(normalized.encode()).hexdigest()


def deduplicate_questions(questions):
    """Remove duplicate questions based on content similarity"""
    seen_hashes = {}
    unique_questions = []
    
    for q in questions:
        q_hash = create_question_hash(q['question'])
        if q_hash not in seen_hashes:
            seen_hashes[q_hash] = q
            unique_questions.append(q)
    
    return unique_questions


def merge_translations(questions_by_lang):
    """Merge questions from different languages into unified structure"""
    merged = []
    
    # Group by question number
    by_number = defaultdict(dict)
    for lang, questions in questions_by_lang.items():
        for q in questions:
            by_number[q['number']][lang] = q
    
    # Create merged structure
    for q_num in sorted(by_number.keys()):
        translations = by_number[q_num]
        
        # Use English as base if available, otherwise first available
        base_lang = 'en' if 'en' in translations else list(translations.keys())[0]
        
        merged_q = {
            'id': q_num,
            'correctOptionKey': 'B',  # Default - needs manual review
            'translations': {}
        }
        
        for lang, q_data in translations.items():
            merged_q['translations'][lang] = {
                'question': q_data['question'],
                'options': q_data['options']
            }
        
        merged.append(merged_q)
    
    return merged


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
        'mock 1 exams answers.html',
        'MOCKEX 4.html',
        'MOCKEX 4 answers.html',
        'SAMPLE QUESTIONS FROM MY UPCOMING   BOOK.html',
        'SAMPLE QUESTIons.html'
    ]
    
    for filename in en_files:
        filepath = source_dir / filename
        if filepath.exists():
            questions, images = extract_from_english_html(filepath)
            questions_by_lang['en'].extend(questions)
            all_images.extend(images)
    
    # Process French files
    fr_files = [
        'model questions -french (1).html',
        'model questions -french rep.html',
        'SKCOMTEST FR - Copy.html'
    ]
    
    for filename in fr_files:
        filepath = source_dir / filename
        if filepath.exists():
            questions, images = extract_from_french_html(filepath)
            questions_by_lang['fr'].extend(questions)
            all_images.extend(images)
    
    # Deduplicate within each language
    for lang in questions_by_lang:
        questions_by_lang[lang] = deduplicate_questions(questions_by_lang[lang])
    
    # Merge translations
    merged_questions = merge_translations(questions_by_lang)
    
    return merged_questions, all_images


def export_to_js(questions, images, output_path='quiz-data.js'):
    """Export questions to JavaScript format"""
    
    # Create image map
    image_map = {}
    for idx, img in enumerate(set(images)):
        image_map[f'img_{idx}'] = img
    
    js_content = f"""// Auto-generated quiz data
// Generated from HTML sources

export const quizData = {json.dumps(questions, indent=2, ensure_ascii=False)};

export const quizImages = {json.dumps(image_map, indent=2)};

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
    
    print(f"Exported {len(questions)} questions to {output_path}")
    print(f"Extracted {len(set(images))} unique images")


if __name__ == '__main__':
    print("Extracting questions from HTML files...")
    questions, images = process_all_html_files()
    
    print(f"\nExtracted {len(questions)} total questions")
    print(f"Extracted {len(images)} total images (including duplicates)")
    
    export_to_js(questions, images)
    print("\nDone!")
