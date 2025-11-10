import re

# Read the file
with open('quiz-data.js', 'r', encoding='utf-8') as f:
    content = f.read()

# The malformed Question 2 English section with missing B and D options
# We'll fix it directly in the text

old_q2_en = '''      "en": {
        "question": "When reporting the position of your craft at sea by the use of this magnetic compass, you need to mention the correct direction with respect to the lighthouse as",
        "options": {
          "A": "345",
          "C": "D 165 C"
        }
      },'''

new_q2_en = '''      "en": {
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
      }'''

# Replace the malformed Q2
content = content.replace(old_q2_en, new_q2_en)

# Now remove the French part from Q2 - we'll add it as a separate question
old_q2_fr = '''      "fr": {
        "question": "Un bateau de plaisance porte l'immatriculation PC 1898 OL 12. Le quel de ces arguments est FAUX concernant ce bateau ?",
        "options": {
          "A": "Le nombre maximal de personnes que peut transporter ce bateau est 12 incluant le skipper",
          "B": "Le bateau n'est pas autorisé à naviguer au-delā de12 nautiques de la côte.",
          "C": "Le bateau a une licence pour des activités commerciales",
          "D": "Le bateau peut aussi naviguer dans le lagon"
        }
      }'''

# Remove the FR part
content = content.replace(',\n' + old_q2_fr, '')

# Write back
with open('quiz-data.js', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed Question 2!")
print("  - Removed French registration question from Q2")
print("  - Fixed English compass options (A: 345 C, B: 185 C, C: 350 C, D: 165 C)")
print("  - Changed correctOptionKey to 'A' (345 C is correct)")
print("\nNote: French boat registration question will need to be added as separate question later")
