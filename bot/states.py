from aiogram.fsm.state import StatesGroup, State

class Registration(StatesGroup):
    """Start handler states"""
    full_name = State()
    phone_number = State()


class MenuState(StatesGroup):
    """Language handler states"""
    language = State()


class TestState(StatesGroup):
    """Test handler states"""
    choosing_category = State()      # Kategoriya tanlash
    answering_question = State()     # Savolga javob berish
    showing_answer = State()         # Javobni ko'rsatish
    finished = State()               # Test tugadi


class ConspectState(StatesGroup):
    """Konspekt handler states"""
    choosing_category = State()
    viewing_files = State()
    viewing_statistics = State()


class VideoState(StatesGroup):
    """Video handler states"""
    choosing_category = State()
    viewing_videos = State()
    viewing_statistics = State()


class AccidentState(StatesGroup):
    """Baxtsiz hodisalar handler states"""
    viewing_years = State()
    viewing_accidents = State()
    viewing_detail = State()
    viewing_statistics = State()



class FolderState(StatesGroup):
    """Folder handler states (7 ta bo'lim uchun umumiy)"""
    choosing_folder = State()
    viewing_files = State()
    viewing_detail = State()
    viewing_statistics = State()