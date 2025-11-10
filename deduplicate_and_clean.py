#!/usr/bin/env python3
"""
Deduplicate questions and prepare for translation.
Removes duplicate questions based on analysis report and creates a clean dataset.
"""
import json
import hashlib
import re
from collections import defaultdict

def normalize_text(text):
    """Normalize text for comparison."""
    if not text:
        return ""
    # Convert to lowercase
    text = text.lower()
    # Remove extra whitespace
    text = ' '.join(text.split())
    # Remove punctuation but keep numbers
    text = re.sub(r'[^\w\s]', '', text)
    return text

def get_question_hash(question_text, options):
    """Generate hash for question to identify duplicates."""
    normalized_q = normalize_text(question_text)
    
    # For options, handle both dict and string formats
    if isinstance(options, dict):
        normalized_opts = ' '.join([normalize_text(str(v)) for v in sorted(options.values())])
    else:
        normalized_opts = normalize_text(str(options))
    
    combined = normalized_q + normalized_opts
    return hashlib.md5(combined.encode('utf-8')).hexdigest()

def load_merged_data():
    """Load the merged quiz data."""
    with open('quiz-data-merged.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def detect_language(text):
    """Simple language detection based on common words."""
    if not text or not isinstance(text, str):
        return 'unknown'
    
    text_lower = text.lower()
    
    # French indicators
    french_words = ['le', 'la', 'les', 'de', 'des', 'un', 'une', 'est', 'sont', 'du', 
                    'nautiques', 'nœuds', 'degrés', 'navire', 'bateau', 'vitesse']
    # English indicators
    english_words = ['the', 'a', 'an', 'is', 'are', 'of', 'to', 'in', 'on', 'at',
                     'nautical', 'knots', 'degrees', 'vessel', 'boat', 'speed']
    
    french_count = sum(1 for word in french_words if word in text_lower)
    english_count = sum(1 for word in english_words if word in text_lower)
    
    if french_count > english_count:
        return 'fr'
    elif english_count > french_count:
        return 'en'
    return 'unknown'

def deduplicate_questions(questions):
    """
    Remove duplicate questions, keeping the best version.
    Priority: keep questions with both EN and FR translations.
    """
    # Group questions by hash
    hash_groups = defaultdict(list)
    
    for q in questions:
        # Try both EN and FR to find duplicates
        for lang in ['en', 'fr']:
            if q['translations'].get(lang) and q['translations'][lang].get('question'):
                q_text = q['translations'][lang]['question']
                q_opts = q['translations'][lang]['options']
                q_hash = get_question_hash(q_text, q_opts)
                hash_groups[q_hash].append(q)
                break
    
    # Keep unique questions
    unique_questions = []
    seen_hashes = set()
    
    for q in questions:
        # Get hash for this question
        q_hash = None
        for lang in ['en', 'fr']:
            if q['translations'].get(lang) and q['translations'][lang].get('question'):
                q_text = q['translations'][lang]['question']
                q_opts = q['translations'][lang]['options']
                q_hash = get_question_hash(q_text, q_opts)
                break
        
        if not q_hash:
            continue
            
        if q_hash in seen_hashes:
            continue
            
        # Check if this is part of a duplicate group
        duplicates = hash_groups[q_hash]
        if len(duplicates) > 1:
            # Pick the best one (with most translations or images)
            best = max(duplicates, key=lambda x: (
                bool(x['translations'].get('en', {}).get('question')),
                bool(x['translations'].get('fr', {}).get('question')),
                len(x.get('images', []))
            ))
            if q == best:
                unique_questions.append(q)
                seen_hashes.add(q_hash)
        else:
            unique_questions.append(q)
            seen_hashes.add(q_hash)
    
    return unique_questions

def prepare_for_translation(questions):
    """
    Identify questions that need translation and mark them clearly.
    Returns questions with translation status.
    """
    translation_stats = {
        'needs_en_translation': [],
        'needs_fr_translation': [],
        'complete': []
    }
    
    for i, q in enumerate(questions):
        has_en = bool(q['translations'].get('en', {}).get('question'))
        has_fr = bool(q['translations'].get('fr', {}).get('question'))
        
        # Check if EN/FR are actually different questions (not translations)
        if has_en and has_fr:
            en_q = q['translations']['en']['question']
            fr_q = q['translations']['fr']['question']
            
            # If they're very different, they might be different questions
            en_lang = detect_language(en_q)
            fr_lang = detect_language(fr_q)
            
            if en_lang == fr_lang:
                # Both detected as same language - might be mislabeled
                if en_lang == 'fr':
                    # Both are French
                    has_en = False
                elif en_lang == 'en':
                    # Both are English  
                    has_fr = False
        
        if has_en and not has_fr:
            translation_stats['needs_fr_translation'].append(i + 1)
        elif has_fr and not has_en:
            translation_stats['needs_en_translation'].append(i + 1)
        elif has_en and has_fr:
            translation_stats['complete'].append(i + 1)
    
    return translation_stats

def main():
    print("Loading merged quiz data...")
    questions = load_merged_data()
    print(f"Loaded {len(questions)} questions")
    
    print("\n" + "="*60)
    print("DEDUPLICATION")
    print("="*60)
    
    unique_questions = deduplicate_questions(questions)
    removed_count = len(questions) - len(unique_questions)
    print(f"Removed {removed_count} duplicate questions")
    print(f"Unique questions remaining: {len(unique_questions)}")
    
    print("\n" + "="*60)
    print("TRANSLATION ANALYSIS")
    print("="*60)
    
    stats = prepare_for_translation(unique_questions)
    
    print(f"\nComplete (both EN and FR): {len(stats['complete'])} questions")
    print(f"Need English translation: {len(stats['needs_en_translation'])} questions")
    if stats['needs_en_translation']:
        print(f"  Question IDs: {stats['needs_en_translation'][:10]}" + 
              (" ..." if len(stats['needs_en_translation']) > 10 else ""))
    
    print(f"Need French translation: {len(stats['needs_fr_translation'])} questions")
    if stats['needs_fr_translation']:
        print(f"  Question IDs: {stats['needs_fr_translation'][:10]}" + 
              (" ..." if len(stats['needs_fr_translation']) > 10 else ""))
    
    # Renumber questions
    for i, q in enumerate(unique_questions, 1):
        q['id'] = i
    
    # Save cleaned data
    output_file = 'quiz-data-clean.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(unique_questions, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Saved {len(unique_questions)} unique questions to {output_file}")
    
    # Create translation TODO file
    with open('translation-todo.txt', 'w', encoding='utf-8') as f:
        f.write("TRANSLATION TODO LIST\n")
        f.write("=" * 60 + "\n\n")
        
        if stats['needs_en_translation']:
            f.write(f"NEED ENGLISH TRANSLATION ({len(stats['needs_en_translation'])} questions):\n")
            f.write("-" * 60 + "\n")
            for q_id in stats['needs_en_translation']:
                q = unique_questions[q_id - 1]
                fr_q = q['translations']['fr']['question']
                f.write(f"\nQuestion {q_id}:\n")
                f.write(f"FR: {fr_q}\n")
                f.write(f"EN: [NEEDS TRANSLATION]\n")
        
        if stats['needs_fr_translation']:
            f.write(f"\n\nNEED FRENCH TRANSLATION ({len(stats['needs_fr_translation'])} questions):\n")
            f.write("-" * 60 + "\n")
            for q_id in stats['needs_fr_translation']:
                q = unique_questions[q_id - 1]
                en_q = q['translations']['en']['question']
                f.write(f"\nQuestion {q_id}:\n")
                f.write(f"EN: {en_q}\n")
                f.write(f"FR: [NEEDS TRANSLATION]\n")
    
    print(f"✓ Created translation-todo.txt with items needing translation")
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Original questions: {len(questions)}")
    print(f"Duplicates removed: {removed_count}")
    print(f"Unique questions: {len(unique_questions)}")
    print(f"Fully bilingual: {len(stats['complete'])}")
    print(f"Need translation: {len(stats['needs_en_translation']) + len(stats['needs_fr_translation'])}")

if __name__ == '__main__':
    main()
