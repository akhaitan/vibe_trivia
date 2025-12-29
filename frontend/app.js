// API Configuration
// Use relative URLs when frontend and backend are on same origin (production)
// Use localhost:8000 when frontend is served separately (local dev with HTTP server)
const API_BASE_URL = (window.location.origin === 'http://localhost:8080' || 
                      window.location.origin === 'http://127.0.0.1:8080')
    ? 'http://localhost:8000' 
    : '';  // Empty string = same origin (works when served from FastAPI)

// State Management
let currentQuiz = {
    quizId: null,
    questions: [],
    userName: '',
    topic: ''
};

// DOM Elements
const welcomeScreen = document.getElementById('welcome-screen');
const quizScreen = document.getElementById('quiz-screen');
const resultsScreen = document.getElementById('results-screen');
const quizForm = document.getElementById('quiz-form');
const quizQuestionsForm = document.getElementById('quiz-questions-form');
const questionsContainer = document.getElementById('questions-container');
const submitBtn = document.getElementById('submit-btn');
const errorMessage = document.getElementById('error-message');
const generateBtn = document.getElementById('generate-btn');
const newQuizBtn = document.getElementById('new-quiz-btn');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    quizForm.addEventListener('submit', handleQuizGeneration);
    quizQuestionsForm.addEventListener('submit', handleQuizSubmit);
    newQuizBtn.addEventListener('click', resetToWelcome);
    
    // Enable submit button when all questions are answered
    questionsContainer.addEventListener('change', checkAllQuestionsAnswered);
    
    // Load quiz history on page load
    loadQuizHistory();
});

// Show screen helper
function showScreen(screen) {
    welcomeScreen.classList.remove('active');
    quizScreen.classList.remove('active');
    resultsScreen.classList.remove('active');
    screen.classList.add('active');
}

// Error handling
function showError(message) {
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
    setTimeout(() => {
        errorMessage.style.display = 'none';
    }, 5000);
}

function hideError() {
    errorMessage.style.display = 'none';
}

// Quiz Generation
async function handleQuizGeneration(e) {
    e.preventDefault();
    hideError();
    
    const userName = document.getElementById('user-name').value.trim();
    const topic = document.getElementById('topic').value.trim();
    
    if (!userName || !topic) {
        showError('Please fill in all fields');
        return;
    }
    
    // Set loading state
    generateBtn.classList.add('loading');
    generateBtn.disabled = true;
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/generate-quiz`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_name: userName,
                topic: topic
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to generate quiz');
        }
        
        const data = await response.json();
        
        // Store quiz data
        currentQuiz.quizId = data.quiz_id;
        currentQuiz.questions = data.questions;
        currentQuiz.userName = userName;
        currentQuiz.topic = topic;
        
        // Display quiz
        displayQuiz();
        showScreen(quizScreen);
        
    } catch (error) {
        console.error('Error generating quiz:', error);
        showError(error.message || 'Failed to generate quiz. Please try again.');
    } finally {
        generateBtn.classList.remove('loading');
        generateBtn.disabled = false;
    }
}

// Display Quiz
function displayQuiz() {
    // Set topic header
    document.getElementById('quiz-topic').textContent = currentQuiz.topic;
    
    // Clear previous questions
    questionsContainer.innerHTML = '';
    
    // Render questions
    currentQuiz.questions.forEach((question, index) => {
        const questionCard = createQuestionCard(question, index);
        questionsContainer.appendChild(questionCard);
    });
    
    // Reset submit button
    submitBtn.disabled = true;
}

function createQuestionCard(question, index) {
    const card = document.createElement('div');
    card.className = 'question-card';
    card.dataset.questionIndex = index;
    
    const questionText = document.createElement('div');
    questionText.className = 'question-text';
    questionText.textContent = `${index + 1}. ${question.question}`;
    card.appendChild(questionText);
    
    const optionsContainer = document.createElement('div');
    optionsContainer.className = 'options-container';
    
    question.options.forEach((option, optionIndex) => {
        const optionDiv = document.createElement('div');
        optionDiv.className = 'option';
        
        const radio = document.createElement('input');
        radio.type = 'radio';
        radio.name = `question-${index}`;
        radio.id = `question-${index}-option-${optionIndex}`;
        radio.value = option;
        radio.required = true;
        
        const label = document.createElement('label');
        label.htmlFor = `question-${index}-option-${optionIndex}`;
        label.textContent = option;
        
        optionDiv.appendChild(radio);
        optionDiv.appendChild(label);
        optionsContainer.appendChild(optionDiv);
    });
    
    card.appendChild(optionsContainer);
    return card;
}

// Check if all questions are answered
function checkAllQuestionsAnswered() {
    const totalQuestions = currentQuiz.questions.length;
    let answeredCount = 0;
    
    for (let i = 0; i < totalQuestions; i++) {
        const selected = document.querySelector(`input[name="question-${i}"]:checked`);
        if (selected) {
            answeredCount++;
        }
    }
    
    submitBtn.disabled = answeredCount !== totalQuestions;
}

// Submit Quiz
async function handleQuizSubmit(e) {
    e.preventDefault();
    hideError();
    
    // Collect answers
    const answers = [];
    for (let i = 0; i < currentQuiz.questions.length; i++) {
        const selected = document.querySelector(`input[name="question-${i}"]:checked`);
        if (!selected) {
            showError('Please answer all questions');
            return;
        }
        answers.push(selected.value);
    }
    
    // Set loading state
    submitBtn.disabled = true;
    submitBtn.textContent = 'Submitting...';
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/submit-quiz`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                quiz_id: currentQuiz.quizId,
                user_name: currentQuiz.userName,
                answers: answers
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to submit quiz');
        }
        
        const data = await response.json();
        
        // Display results
        displayResults(data);
        showScreen(resultsScreen);
        
    } catch (error) {
        console.error('Error submitting quiz:', error);
        showError(error.message || 'Failed to submit quiz. Please try again.');
        submitBtn.disabled = false;
        submitBtn.textContent = 'Submit Quiz';
    }
}

// Display Results
function displayResults(data) {
    // Display score
    const scoreDisplay = document.getElementById('score-display');
    const scorePercentage = document.getElementById('score-percentage');
    const performancePhrase = document.getElementById('performance-phrase');
    
    // Format: "Score/10, [Performance Phrase]"
    scoreDisplay.textContent = `${data.score} / ${data.total}`;
    const percentage = Math.round((data.score / data.total) * 100);
    scorePercentage.textContent = `${percentage}%`;
    
    // Display performance phrase
    if (data.performance_phrase) {
        performancePhrase.textContent = data.performance_phrase;
        performancePhrase.style.display = 'block';
    } else {
        performancePhrase.style.display = 'none';
    }
    
    // Display detailed results
    const resultsContainer = document.getElementById('results-container');
    resultsContainer.innerHTML = '';
    
    // Update question cards with results
    data.results.forEach((result, index) => {
        const questionCard = document.querySelector(`[data-question-index="${index}"]`);
        if (questionCard) {
            // Mark all options
            const options = questionCard.querySelectorAll('.option');
            options.forEach(optionDiv => {
                const radio = optionDiv.querySelector('input[type="radio"]');
                const optionValue = radio.value;
                
                optionDiv.classList.remove('selected', 'correct', 'incorrect');
                
                if (optionValue === result.correct) {
                    optionDiv.classList.add('correct');
                }
                
                if (optionValue === result.selected) {
                    optionDiv.classList.add('selected');
                    if (!result.is_correct) {
                        optionDiv.classList.add('incorrect');
                    }
                }
            });
        }
        
        // Create result summary item
        const resultItem = document.createElement('div');
        resultItem.className = 'result-item';
        
        const questionText = document.createElement('div');
        questionText.className = 'result-question';
        questionText.textContent = `${index + 1}. ${result.question}`;
        resultItem.appendChild(questionText);
        
        const selectedAnswer = document.createElement('div');
        selectedAnswer.className = `result-answer ${result.is_correct ? 'correct' : 'incorrect'}`;
        selectedAnswer.textContent = `Your answer: ${result.selected} ${result.is_correct ? '✓' : '✗'}`;
        resultItem.appendChild(selectedAnswer);
        
        if (!result.is_correct) {
            const correctAnswer = document.createElement('div');
            correctAnswer.className = 'result-answer correct';
            correctAnswer.textContent = `Correct answer: ${result.correct}`;
            resultItem.appendChild(correctAnswer);
        }
        
        resultsContainer.appendChild(resultItem);
    });
    
    // Scroll to top
    window.scrollTo(0, 0);
}

// Reset to Welcome Screen
function resetToWelcome() {
    // Reset form
    quizForm.reset();
    
    // Reset state
    currentQuiz = {
        quizId: null,
        questions: [],
        userName: '',
        topic: ''
    };
    
    // Reset UI
    questionsContainer.innerHTML = '';
    submitBtn.disabled = true;
    submitBtn.textContent = 'Submit Quiz';
    hideError();
    
    showScreen(welcomeScreen);
    
    // Reload history when returning to welcome screen
    loadQuizHistory();
}

// Load Quiz History
async function loadQuizHistory() {
    const historyLoading = document.getElementById('history-loading');
    const historyEmpty = document.getElementById('history-empty');
    const historyTableContainer = document.getElementById('history-table-container');
    const historyTableBody = document.getElementById('history-table-body');
    
    // Show loading state
    historyLoading.style.display = 'block';
    historyEmpty.style.display = 'none';
    historyTableContainer.style.display = 'none';
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/history`);
        
        if (!response.ok) {
            throw new Error('Failed to load quiz history');
        }
        
        const data = await response.json();
        const attempts = data.attempts || [];
        
        // Hide loading
        historyLoading.style.display = 'none';
        
        if (attempts.length === 0) {
            historyEmpty.style.display = 'block';
            historyTableContainer.style.display = 'none';
        } else {
            historyEmpty.style.display = 'none';
            historyTableContainer.style.display = 'block';
            
            // Clear existing rows
            historyTableBody.innerHTML = '';
            
            // Add rows for each attempt
            attempts.forEach(attempt => {
                const row = document.createElement('tr');
                
                // Format timestamp
                const timestamp = new Date(attempt.timestamp);
                const formattedDate = timestamp.toLocaleDateString();
                const formattedTime = timestamp.toLocaleTimeString();
                const formattedTimestamp = `${formattedDate} ${formattedTime}`;
                
                row.innerHTML = `
                    <td>${escapeHtml(attempt.user_name)}</td>
                    <td>${escapeHtml(attempt.quiz_topic)}</td>
                    <td>${attempt.score} / ${attempt.total}</td>
                    <td>${formattedTimestamp}</td>
                `;
                
                historyTableBody.appendChild(row);
            });
        }
    } catch (error) {
        console.error('Error loading quiz history:', error);
        historyLoading.style.display = 'none';
        historyEmpty.style.display = 'block';
        historyEmpty.textContent = 'Failed to load quiz history.';
        historyTableContainer.style.display = 'none';
    }
}

// Helper function to escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

