import React, { useState, useMemo, useCallback } from 'react';
import { CheckCircle2, XCircle, ChevronRight, RefreshCw, Trophy } from 'lucide-react';
import { quizData as importedQuizData, appTexts as importedAppTexts } from './quiz-data.js';

// --- Use imported quiz data from quiz-data.js ---
// Original mock data kept below for reference but commented out
/* const quizData = [
  {
    id: 1,
    correctOptionKey: 'B',
    translations: {
      en: {
        question: "According to the Tourism Authority Act 2006, the 'skipper' of a pleasure craft is the person who:",
        options: {
          A: "represents the owner of the boat when the boat is at sea",
          B: "changes the course and speed of the boat at sea",
          C: "is responsible for engine maintenance",
          D: "is responsible for sea rescue",
        }
      },
      fr: {
        question: "D’après la Tourism Authority Act 2006, le ‘skipper’ d’un bateau de plaisance est celui qui:",
        options: {
          A: "représente le propriétaire du bateau quand le bateau est en mer",
          B: "change le cap et la vitesse du bateau en mer",
          C: "se charge de la maintenance des moteurs",
          D: "se charge du sauvetage en mer",
        }
      },
      ru: {
        question: "Согласно Закону об управлении туризма 2006 года, «шкипер» прогулочного судна – это человек, который:",
        options: {
          A: "представляет владельца лодки, когда она находится в море",
          B: "изменяет курс и скорость лодки в море",
          C: "отвечает за техническое обслуживание двигателей",
          D: "отвечает за спасение на море",
        }
      },
    }
  },
  {
    id: 2,
    correctOptionKey: 'B',
    translations: {
      en: {
        question: "What is the 'draft' of a boat?",
        options: {
          A: "The weight of the boat without propulsion means",
          B: "The vertical distance between the waterline and the keel of the boat",
          C: "The vertical distance between the waterline and the gunwale of the boat",
          D: "The distance between the bow and the stern of the boat",
        }
      },
      fr: {
        question: "C’est quoi ‘ le tirant d’eau’ d’un bateau ?",
        options: {
          A: "le poids du bateau sans les moyens de propulsion",
          B: "la distance verticale entre la ligne de flottaison et la quille du bateau",
          C: "la distance verticale entre la ligne de flottaison et le plat-bord du bateau",
          D: "la distance entre la proue et la poupe du bateau",
        }
      },
      ru: {
        question: "Что такое 'осадка' лодки?",
        options: {
          A: "Вес лодки без средств движения",
          B: "Вертикальное расстояние между ватерлинией и килем лодки",
          C: "Вертикальное расстояние между ватерлинией и бортом лодки",
          D: "Расстояние между носом и кормой лодки",
        }
      },
    }
  },
  {
    id: 3,
    correctOptionKey: 'D',
    translations: {
      en: {
        question: "Which term is known for the onboard system that changes the boat's course?",
        options: {
          A: "The Compass",
          B: "The Knot",
          C: "The Current",
          D: "The Helm / Bar",
        }
      },
      fr: {
        question: "Par quel terme est connu le système de bord permettant de changer le cap du bateau ?",
        options: {
          A: "Le compas",
          B: "Le nœud",
          C: "Le courant",
          D: "La barre",
        }
      },
      ru: {
        question: "Каким термином называют бортовую систему, которая меняет курс лодки?",
        options: {
          A: "Компас",
          B: "Узел",
          C: "Течение",
          D: "Руль / Штурвал",
        }
      },
    }
  },
  {
    id: 4,
    correctOptionKey: 'C',
    translations: {
      en: {
        question: "Which of the following describes the 'freeboard' of a vessel?",
        options: {
          A: "The distance from the bow to the stern",
          B: "The vertical distance from the keel to the masthead",
          C: "The vertical distance from the waterline to the main deck/gunwale",
          D: "The maximum width of the hull",
        }
      },
      fr: {
        question: "Lequel des éléments suivants décrit le 'franc-bord' d'un navire ?",
        options: {
          A: "La distance de la proue à la poupe",
          B: "La distance verticale de la quille au sommet du mât",
          C: "La distance verticale entre la ligne de flottaison et le plat-bord principal",
          D: "La largeur maximale de la coque",
        }
      },
      ru: {
        question: "Что из перечисленного описывает 'надводный борт' судна?",
        options: {
          A: "Расстояние от носа до кормы",
          B: "Вертикальное расстояние от киля до топа мачты",
          C: "Вертикальное расстояние от ватерлинии до главной палубы/борта",
          D: "Максимальная ширина корпуса",
        }
      },
    }
  },
];
*/

// Use the imported data
const quizData = importedQuizData;
const appTexts = importedAppTexts;

// Original app texts kept below for reference but commented out
/* const appTexts = {
  en: {
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
  },
  fr: {
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
  },
  ru: {
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
  }
};
*/

// Set the desired order of languages for the stacked question/answer text
const languages = ['en', 'fr', 'ru'];
const stackedLanguages = ['fr', 'en', 'ru'];

// Helper to determine the style of an option button
const getOptionStyle = (optionKey, correctOptionKey, selectedOptionKey) => {
  const isSelected = selectedOptionKey === optionKey;
  const isCorrect = correctOptionKey === optionKey;
  const isAnswered = selectedOptionKey !== null;

  if (isAnswered) {
    if (isCorrect) {
      // Highlight correct answer in green
      return 'bg-green-100 border-green-500 hover:bg-green-100 text-green-800';
    }
    if (isSelected && !isCorrect) {
      // Highlight incorrect selected answer in red
      return 'bg-red-100 border-red-500 hover:bg-red-100 text-red-800';
    }
    // Default style for other options once an answer is chosen
    return 'bg-white border-gray-200 text-gray-700 opacity-50 cursor-default';
  }

  // Default style for un-answered state
  return 'bg-white border-gray-200 hover:bg-indigo-50 text-gray-700 cursor-pointer transition-colors';
};

const ResultRow = React.memo(({ index, questionData, userAnswers, appTexts }) => {
  const userSelection = userAnswers[index];
  const correctKey = questionData.correctOptionKey;
  const isCorrect = userSelection === correctKey;

  const getOptionText = (lang, key) => {
    return questionData.translations[lang].options[key];
  };

  return (
    <div className={`p-4 mb-4 rounded-xl shadow-md transition-all ${isCorrect ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'} border-l-4`}>
      <h4 className="flex items-center text-lg font-semibold mb-2">
        {isCorrect ? <CheckCircle2 className="w-5 h-5 text-green-600 mr-2" /> : <XCircle className="w-5 h-5 text-red-600 mr-2" />}
        {appTexts.en.question} {index + 1}
      </h4>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm mt-3">
        {languages.map(lang => (
          <div key={lang} className="p-3 border rounded-lg bg-white shadow-sm">
            <h5 className="font-bold uppercase text-xs mb-1 text-gray-500">{lang}</h5>
            <p className="font-medium mb-2">{questionData.translations[lang].question}</p>
            
            <div className="mt-3 space-y-1">
              {/* Correct Answer */}
              <p className="text-green-600">
                <span className="font-bold">{appTexts[lang].correctAnswer}</span> {correctKey}: {getOptionText(lang, correctKey)}
              </p>
              
              {/* User Selection */}
              {userSelection && (
                <p className={isCorrect ? "text-green-500" : "text-red-500"}>
                  <span className="font-bold">{appTexts[lang].selectedAnswer}</span> {userSelection}: {getOptionText(lang, userSelection)}
                </p>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
});

export default function App() {
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  // userAnswers stores { questionIndex: selectedOptionKey (A, B, C, or D) }
  const [userAnswers, setUserAnswers] = useState({}); 
  const [showCorrectAnswer, setShowCorrectAnswer] = useState(null); // Stores the selected key for the current question
  const [language, setLanguage] = useState('fr'); // Default language for UI text, changed to FR as data is French

  const currentQuestion = quizData[currentQuestionIndex];
  const totalQuestions = quizData.length;
  const isQuizFinished = currentQuestionIndex >= totalQuestions;

  // --- Calculations ---

  const calculateScore = useCallback(() => {
    let score = 0;
    quizData.forEach((q, index) => {
      if (userAnswers[index] === q.correctOptionKey) {
        score++;
      }
    });
    return score;
  }, [userAnswers]);
  
  const score = useMemo(() => calculateScore(), [calculateScore]);
  const currentLanguageText = appTexts[language];

  // --- Handlers ---

  const handleAnswerSelect = (optionKey) => {
    if (showCorrectAnswer === null) {
      // 1. Record the answer locally
      setShowCorrectAnswer(optionKey);

      // 2. Update the main state (userAnswers) after a slight delay
      setTimeout(() => {
        setUserAnswers(prev => ({
          ...prev,
          [currentQuestionIndex]: optionKey
        }));
      }, 100); 
    }
  };

  const handleNext = () => {
    if (currentQuestionIndex < totalQuestions) {
      setCurrentQuestionIndex(prev => prev + 1);
      setShowCorrectAnswer(null);
    }
  };

  const resetQuiz = () => {
    setCurrentQuestionIndex(0);
    setUserAnswers({});
    setShowCorrectAnswer(null);
    setLanguage('fr'); // Reset UI language to default (French)
  };

  const handleFinish = () => {
    setCurrentQuestionIndex(totalQuestions); // Set index past the last question to trigger summary
  };

  // --- Render Functions ---

  const renderSummary = () => {
    const incorrectCount = totalQuestions - score;
    return (
      <div className="bg-white p-8 md:p-10 rounded-xl shadow-2xl w-full max-w-4xl mx-auto border-t-4 border-indigo-500">
        <div className="text-center mb-8">
          <Trophy className="w-16 h-16 text-yellow-500 mx-auto mb-4" />
          <h2 className="text-4xl font-extrabold text-indigo-800 mb-2">{currentLanguageText.summary}</h2>
          <p className="text-xl text-gray-600">
            {currentLanguageText.score}: <span className="font-bold text-indigo-600">{score}</span> / {totalQuestions}
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-center mb-8 font-medium">
            <div className="p-4 bg-green-100 rounded-lg shadow-inner">
                <p className="text-3xl font-bold text-green-700">{score}</p>
                <p className="text-green-800">{currentLanguageText.correct}</p>
            </div>
            <div className="p-4 bg-red-100 rounded-lg shadow-inner">
                <p className="text-3xl font-bold text-red-700">{incorrectCount}</p>
                <p className="text-red-800">{currentLanguageText.incorrect}</p>
            </div>
            <div className="p-4 bg-gray-100 rounded-lg shadow-inner">
                <p className="text-3xl font-bold text-gray-700">{totalQuestions}</p>
                <p className="text-gray-800">Total</p>
            </div>
        </div>

        <h3 className="text-2xl font-semibold text-gray-700 mb-4 border-b pb-2">Detailed Results</h3>
        <div className="max-h-[50vh] overflow-y-auto pr-2">
            {quizData.map((q, index) => (
                <ResultRow 
                    key={q.id} 
                    index={index} 
                    questionData={q} 
                    userAnswers={userAnswers} 
                    appTexts={appTexts}
                />
            ))}
        </div>

        <div className="mt-8 text-center">
          <button
            onClick={resetQuiz}
            className="flex items-center justify-center mx-auto px-8 py-3 bg-indigo-600 text-white font-semibold rounded-full shadow-lg hover:bg-indigo-700 transition-all transform hover:scale-105"
          >
            <RefreshCw className="w-5 h-5 mr-2" /> {currentLanguageText.reset}
          </button>
        </div>
      </div>
    );
  };

  const renderQuiz = () => {
    return (
      <div className="w-full max-w-4xl mx-auto space-y-8">
        {/* Progress Bar and Status */}
        <div className="bg-white p-6 rounded-xl shadow-lg border-t-4 border-indigo-500">
          <p className="text-lg font-medium text-gray-600 mb-3">
            {currentLanguageText.question} {currentQuestionIndex + 1} / {totalQuestions}
          </p>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div
              className="bg-indigo-600 h-3 rounded-full transition-all duration-500 ease-in-out"
              style={{ width: `${((currentQuestionIndex + 1) / totalQuestions) * 100}%` }}
            ></div>
          </div>
        </div>

        {/* Main Question Card - All translations stacked vertically (Fr-En-Ru) */}
        <div className="bg-white p-6 md:p-8 rounded-xl shadow-2xl border-l-4 border-indigo-600">
            {/* Question Texts */}
            <h2 className="text-2xl font-bold text-indigo-800 mb-4 pb-2 border-b">
                {currentLanguageText.question}
            </h2>
            {stackedLanguages.map((langCode, index) => (
            <div key={langCode} className={`mb-3 py-1 ${index < stackedLanguages.length - 1 ? 'border-b border-gray-100' : ''}`}>
                <h3 className="text-base font-bold text-indigo-700 uppercase mb-1">
                {langCode}
                </h3>
                <p className="text-gray-900 font-medium text-lg">
                {currentQuestion.translations[langCode].question}
                </p>
            </div>
            ))}

            {/* Display images if available */}
            {currentQuestion.images && currentQuestion.images.length > 0 && (
            <div className="mt-6 space-y-3">
                {currentQuestion.images.map((imageData, idx) => (
                <div key={idx} className="rounded-lg overflow-hidden border-2 border-indigo-200">
                    <img 
                    src={imageData} 
                    alt={`Question ${currentQuestionIndex + 1} - Image ${idx + 1}`}
                    className="w-full h-auto max-h-96 object-contain bg-gray-50"
                    />
                </div>
                ))}
            </div>
            )}
        </div>

        {/* Answer Options - All translations stacked in each option box (Fr-En-Ru) */}
        <div className="p-6 md:p-8 bg-white rounded-xl shadow-lg">
            <h3 className="text-xl font-bold text-gray-700 mb-4 border-b pb-2">
                {currentLanguageText.question} Options
            </h3>
            
            <div className="flex flex-col space-y-3">
                {/* Use French options keys as the base, assuming all languages have the same keys (A, B, C, D) */}
                {Object.keys(currentQuestion.translations.fr.options).map((optionKey) => {
                const style = getOptionStyle(optionKey, currentQuestion.correctOptionKey, showCorrectAnswer);
                const disabled = showCorrectAnswer !== null;
                
                return (
                    <button
                    key={optionKey}
                    onClick={() => !disabled && handleAnswerSelect(optionKey)}
                    className={`p-3 text-left rounded-lg border-2 transition-all duration-200 ease-in-out shadow-sm ${style}`}
                    disabled={disabled}
                    >
                        {/* Option Letter (A, B, C, D) */}
                        <span className="font-extrabold text-xl mr-3 align-top inline-block w-6 text-indigo-900">
                            {optionKey}.
                        </span>
                        
                        {/* Stacked Translations */}
                        <div className="inline-block align-top ml-2 w-11/12">
                            {stackedLanguages.map((langCode) => (
                                <p 
                                    key={langCode} 
                                    // Make French text slightly more prominent as it is the original QCM language
                                    className={`text-sm md:text-base ${langCode === 'fr' ? 'font-bold text-gray-900' : 'font-medium text-gray-700'} ${langCode !== stackedLanguages[stackedLanguages.length - 1] ? 'mb-1' : ''}`}
                                >
                                    <span className="text-xs font-semibold mr-1 uppercase opacity-60">[{langCode}]</span>
                                    {currentQuestion.translations[langCode].options[optionKey]}
                                </p>
                            ))}
                        </div>
                    </button>
                );
                })}
            </div>
        </div>


        {/* Navigation Buttons */}
        <div className="flex justify-between items-center pt-4 border-t border-gray-200">
          <button
            onClick={resetQuiz}
            className="flex items-center px-4 py-2 text-sm text-gray-600 bg-gray-100 rounded-full hover:bg-gray-200 transition-colors"
          >
            <RefreshCw className="w-4 h-4 mr-2" /> {currentLanguageText.reset}
          </button>

          {/* Next/Finish Button */}
          <button
            onClick={currentQuestionIndex === totalQuestions - 1 ? handleFinish : handleNext}
            disabled={showCorrectAnswer === null}
            className={`flex items-center px-6 py-3 font-semibold rounded-full transition-all duration-300 ${
              showCorrectAnswer !== null
                ? 'bg-indigo-600 text-white hover:bg-indigo-700 shadow-md'
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }`}
          >
            {currentQuestionIndex === totalQuestions - 1
              ? currentLanguageText.finish
              : currentLanguageText.next}
            <ChevronRight className="w-5 h-5 ml-2" />
          </button>
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50 font-sans p-4 sm:p-8">
      {/* Header and Language Selector */}
      <header className="flex flex-col md:flex-row justify-between items-center max-w-6xl mx-auto mb-8">
        <h1 className="text-3xl font-extrabold text-indigo-700 mb-4 md:mb-0">
          {currentLanguageText.title}
        </h1>
        <div className="flex space-x-2 bg-white p-1 rounded-full shadow-inner border">
          {['en', 'fr', 'ru'].map(langCode => (
            <button
              key={langCode}
              onClick={() => setLanguage(langCode)}
              className={`px-4 py-2 text-sm font-medium uppercase rounded-full transition-colors ${
                language === langCode
                  ? 'bg-indigo-500 text-white shadow-md'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              {langCode}
            </button>
          ))}
        </div>
      </header>

      {/* Main Content Area */}
      {isQuizFinished ? renderSummary() : renderQuiz()}
      
      {/* Footer / Debug Info (optional, helpful for dev) */}
      <footer className="mt-10 text-center text-xs text-gray-400">
        <p>Data based on `French Skipper Licence - Permis_Bateau_Maurice_QCM_merge.csv` with mock translations for English and Russian.</p>
      </footer>
    </div>
  );
}