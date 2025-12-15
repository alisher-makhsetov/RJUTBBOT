# ============ TEST CONSTANTS ============
QUESTION_TIME_LIMIT = 60  # Har bir savol uchun vaqt (soniya)
UPDATE_INTERVAL = 5       # Timer yangilanish intervali (soniya)
MAX_QUESTIONS = 10        # Maksimal savol soni
MIN_SHARE_PERCENTAGE = 70 # Ulashish uchun minimal foiz

# ============ MESSAGE CONSTANTS ============
MAX_STORED_MESSAGES = 2   # Saqlanadigan xabarlar soni

# ============ LANGUAGE CONSTANTS ============
DEFAULT_LANGUAGE = "uz"   # Asosiy til
SUPPORTED_LANGUAGES = ["uz", "ru", "en"]  # Qo'llab-quvvatlanadigan tillar

# ============ GRADE CONSTANTS ============
GRADE_EXCELLENT = 90      # A'lo baho uchun minimal foiz
GRADE_GOOD = 80          # Yaxshi baho uchun minimal foiz
GRADE_SATISFACTORY = 70  # Qoniqarli baho uchun minimal foiz
GRADE_AVERAGE = 60       # O'rtacha baho uchun minimal foiz

# ============ EMOJI CONSTANTS ============
GRADE_EMOJIS = {
    "excellent": "🏆",
    "good": "🥇",
    "satisfactory": "🥈",
    "average": "🥉",
    "poor": "📚"
}

GRADE_TEXTS = {
    "excellent": "A'lo!",
    "good": "Yaxshi!",
    "satisfactory": "Qoniqarli!",
    "average": "O'rtacha!",
    "poor": "Ko'proq o'qish kerak!"
}

# ============ ANSWER LETTERS ============
ANSWER_LETTERS = ['A', 'B', 'C', 'D']