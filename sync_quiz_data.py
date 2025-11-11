#!/usr/bin/env python3
"""
Sync quiz-data.js from quiz-data-final.json
Generates a browser-compatible JS file without image imports
"""
import json

# Read the canonical JSON
with open('quiz-data-final.json', 'r', encoding='utf-8') as f:
    quiz_data = json.load(f)

# Generate the JS file - browser compatible version (no imports)
output_lines = [
    "// Auto-generated quiz data - Browser compatible version",
    "// Generated from quiz-data-final.json",
    "",
    "export const quizData = ["
]

# Process each question
for i, question in enumerate(quiz_data):
    # Keep images as-is (paths, not imports)
    question_copy = question.copy()
    
    # Convert to JSON string and indent
    json_str = json.dumps(question_copy, indent=2, ensure_ascii=False)
    # Add proper indentation for array items
    indented = '\n'.join('  ' + line for line in json_str.split('\n'))
    output_lines.append(indented)
    
    # Add comma except for last item
    if i < len(quiz_data) - 1:
        output_lines[-1] += ","

output_lines.append("];")
output_lines.append("")

# Add appTexts with Russian support
app_texts = """
export const appTexts = {
  en: {
    title: "Skipper Quiz",
    startQuiz: "Start Quiz",
    nextQuestion: "Next Question",
    previousQuestion: "Previous",
    submitQuiz: "Submit Quiz",
    score: "Score",
    correctAnswers: "Correct Answers",
    reviewAnswers: "Review Answers",
    restartQuiz: "Restart Quiz"
  },
  fr: {
    title: "Quiz Skipper",
    startQuiz: "Commencer le Quiz",
    nextQuestion: "Question Suivante",
    previousQuestion: "Précédent",
    submitQuiz: "Soumettre le Quiz",
    score: "Score",
    correctAnswers: "Réponses Correctes",
    reviewAnswers: "Revoir les Réponses",
    restartQuiz: "Recommencer le Quiz"
  },
  ru: {
    title: "Тест Шкипера",
    startQuiz: "Начать Тест",
    nextQuestion: "Следующий Вопрос",
    previousQuestion: "Назад",
    submitQuiz: "Завершить Тест",
    score: "Результат",
    correctAnswers: "Правильные Ответы",
    reviewAnswers: "Просмотр Ответов",
    restartQuiz: "Начать Заново"
  }
};
"""
output_lines.append(app_texts.strip())

# Write output
with open('quiz-data.js', 'w', encoding='utf-8') as f:
    f.write('\n'.join(output_lines))

print(f"✓ Generated quiz-data.js with {len(quiz_data)} questions")
print(f"✓ Added Russian language support (EN/FR/RU)")
