from sqlalchemy import BigInteger, String, ForeignKey, Text, Boolean, DateTime, Integer, Table, Column, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db import Base
from db.utils import CreatedModel

# ============================================
# USER MODELI
# Telegram bot foydalanuvchilari
# ============================================

class User(CreatedModel):
    """
    Bot foydalanuvchilari
    Ro'yxatdan o'tish: ism-familya, telefon raqam
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[str | None] = mapped_column(String(56), nullable=True)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(20), nullable=False)
    language_code: Mapped[str] = mapped_column(String(5), default="uz")  # uz, qq, ru
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)  # Faolmi

    def __str__(self):
        return f"{self.full_name} - {self.phone_number}"

    def __repr__(self):
        return f"User(id={self.id}, name='{self.full_name}', phone='{self.phone_number}')"

# ============================================
# TESTLAR MODELI (MM va SX uchun)
# Test kategoriyalari, savollari va javoblari
# ============================================

test_category_association = Table(
    'test_category_association',
    Base.metadata,
    Column('test_id', ForeignKey('tests.id', ondelete='CASCADE'), primary_key=True),
    Column('category_id', ForeignKey('test_categories.id', ondelete='CASCADE'), primary_key=True)
)

class TestCategory(CreatedModel):
    """
    Test kategoriyalari
    MM va SX uchun test bo'limlari
    """
    __tablename__ = "test_categories"
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    section: Mapped[str] = mapped_column(String(10), nullable=False)  # 'MM' yoki 'SX'

    # Many-to-Many relationship
    tests: Mapped[list["Test"]] = relationship(
        secondary=test_category_association,
        back_populates="categories",
        order_by="Test.created_at"  # ✅ Birinchi yaratilgan birinchi (lekin botda random)
    )

    def __str__(self):
        return f"{self.name} ({self.section})"


class Test(CreatedModel):
    """
    Test savollari
    Har bir test bir necha kategoriyaga tegishli bo'lishi mumkin
    """
    __tablename__ = "tests"
    text: Mapped[str] = mapped_column(Text, nullable=False)
    image: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Many-to-Many relationship
    categories: Mapped[list["TestCategory"]] = relationship(
        secondary=test_category_association,
        back_populates="tests"
    )

    answers: Mapped[list["TestAnswer"]] = relationship(
        back_populates="test",
        cascade="all, delete-orphan"
    )

    def __str__(self):
        return self.text[:30] + "..." if len(self.text) > 30 else self.text


class TestAnswer(CreatedModel):
    """
    Test javoblari
    Har bir testda 4 ta javob: A, B, C, D
    """
    __tablename__ = "test_answers"
    text: Mapped[str] = mapped_column(String(500), nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False)
    test_id: Mapped[int] = mapped_column(ForeignKey("tests.id", ondelete='CASCADE'))
    test: Mapped["Test"] = relationship(back_populates="answers")

    def __str__(self):
        return self.text


# ============================================
# VIDEO ROLIKLAR MODELI (MM va SX uchun)
# Video kategoriyalari va videolar
# ============================================

class VideoCategory(CreatedModel):
    """Video kategoriyalari"""
    __tablename__ = "video_categories"
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    section: Mapped[str] = mapped_column(String(10), nullable=False)
    videos: Mapped[list["Video"]] = relationship(
        back_populates="category",
        cascade="all, delete-orphan",
        order_by="Video.created_at"  # ✅ Faqat shu
    )

    def __str__(self):
        return f"{self.name} ({self.section})"


class Video(CreatedModel):
    """Video roliklar"""
    __tablename__ = "videos"
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text)
    file: Mapped[str] = mapped_column(String)
    # order_index kerak emas ✅
    category_id: Mapped[int] = mapped_column(ForeignKey("video_categories.id", ondelete='CASCADE'))
    category: Mapped["VideoCategory"] = relationship(back_populates="videos")

    def __str__(self):
        return self.name

# ============================================
# KONSPEKTLAR MODELI (MM va SX uchun)
# Konspekt kategoriyalari va konspektlar
# ============================================

class ConspectCategory(CreatedModel):
    """
    Konspekt kategoriyalari
    MM va SX uchun konspektlar bo'limlari
    """
    __tablename__ = "conspect_categories"
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    section: Mapped[str] = mapped_column(String(10), nullable=False)  # 'MM' yoki 'SX'
    conspects: Mapped[list["Conspect"]] = relationship(
        back_populates="category",
        cascade="all, delete-orphan",
        order_by="Conspect.created_at"  # ✅ Sodda - faqat created_at
    )

    def __str__(self):
        return f"{self.name} ({self.section})"


class Conspect(CreatedModel):
    """
    Konspektlar - PDF, DOC, DOCX fayllar
    """
    __tablename__ = "conspects"
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text)
    file: Mapped[str] = mapped_column(String)  # Telegram file_id
    category_id: Mapped[int] = mapped_column(ForeignKey("conspect_categories.id", ondelete='CASCADE'))
    category: Mapped["ConspectCategory"] = relationship(back_populates="conspects")

    def __str__(self):
        return self.name


# ============================================
# FOLDER VA FILE MODELI
# Faqat bitta bo'limda bo'lgan qismlar uchun
# ============================================
# MM: Himoya vositalari, Nizomlar, O'quv texnik mashg'ulot
# SX: Kranlar, Qozonxonalar, Bosim idishlari, To'liq texnik ko'rik
# ============================================

class Folder(CreatedModel):
    """Papkalar - MM va SX maxsus bo'limlari uchun"""
    __tablename__ = "folders"

    # ✅ PARENT_TYPE CHOICES
    PARENT_TYPE_CHOICES = [
        # MM bo'limlari
        ('himoya_vositalari', 'Himoya Vositalari'),
        ('nizomlar', 'Nizomlar'),
        ('oquv_texnik', "O'quv Texnik Mashg'ulot"),
        # SX bo'limlari
        ('kranlar', 'Kranlar'),
        ('qozonxonalar', 'Qozonxonalar'),
        ('bosim_idishlari', 'Bosim Idishlari'),
        ('toliq_texnik', "To'liq Texnik Ko'rik"),
    ]

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    section: Mapped[str] = mapped_column(String(10), nullable=False)  # 'MM' yoki 'SX'
    parent_type: Mapped[str] = mapped_column(String(50), nullable=False)  # CHOICES dan
    order_index: Mapped[int] = mapped_column(Integer, default=0)

    files: Mapped[list["File"]] = relationship(
        back_populates="folder",
        cascade="all, delete-orphan",
        order_by="File.order_index, File.created_at"
    )

    def __str__(self):
        return f"{self.name} ({self.section} - {self.get_parent_type_display()})"

    def get_parent_type_display(self):
        """Parent type nomini olish"""
        for key, value in self.PARENT_TYPE_CHOICES:
            if key == self.parent_type:
                return value
        return self.parent_type


class FileView(CreatedModel):
    """
    Fayl ko'rishlar - User bo'yicha unique
    Har bir user faylni faqat 1 marta ko'rgan hisoblanadi
    """
    __tablename__ = "file_views"

    file_id: Mapped[int] = mapped_column(
        ForeignKey("files.id", ondelete='CASCADE'),
        nullable=False
    )
    user_id: Mapped[int] = mapped_column(nullable=False)  # Telegram user_id

    # Relationships
    file: Mapped["File"] = relationship(back_populates="views")

    # ✅ UNIQUE CONSTRAINT - User faqat 1 marta
    __table_args__ = (
        UniqueConstraint('file_id', 'user_id', name='unique_file_user_view'),
    )

    def __str__(self):
        return f"FileView(file_id={self.file_id}, user_id={self.user_id})"


# ✅ FILE MODELNI YANGILASH
class File(CreatedModel):
    """Fayllar - Papkalarga tegishli"""
    __tablename__ = "files"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_id: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    folder_id: Mapped[int] = mapped_column(ForeignKey("folders.id", ondelete='CASCADE'))
    order_index: Mapped[int] = mapped_column(Integer, default=0)

    # ✅ RELATIONSHIP
    folder: Mapped["Folder"] = relationship(back_populates="files")
    views: Mapped[list["FileView"]] = relationship(
        back_populates="file",
        cascade="all, delete-orphan"
    )

    @property
    def views_count(self) -> int:
        """Unique userlar soni"""
        return len(self.views)

    def __str__(self):
        return self.name


# ============================================
# BAXTSIZ HODISALAR MODELI (faqat MM uchun)
# Kategoriyalar, Yillar va Hodisalar + Views
# ============================================

class AccidentCategory(CreatedModel):
    """Baxtsiz hodisa kategoriyalari"""
    __tablename__ = "accident_categories"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    accidents: Mapped[list["Accident"]] = relationship(
        back_populates="category",
        order_by="Accident.created_at.desc()"
    )

    def __str__(self):
        return self.name


class AccidentYear(CreatedModel):
    """Baxtsiz hodisa yillari"""
    __tablename__ = "accident_years"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    accidents: Mapped[list["Accident"]] = relationship(
        back_populates="year",
        order_by="Accident.created_at.desc()"
    )

    @property
    def year_number(self) -> int:
        """Yil raqamini olish (tartiblash uchun)"""
        import re
        match = re.search(r'(\d{4})', self.name)
        return int(match.group(1)) if match else 0

    @property
    def has_accidents(self) -> bool:
        """Bu yilda baxtsiz hodisalar bormi?"""
        return len(self.accidents) > 0

    def __str__(self):
        return self.name


class AccidentView(CreatedModel):
    """
    Baxtsiz hodisa ko'rishlar - User bo'yicha unique
    Har bir user hodisani faqat 1 marta ko'rgan hisoblanadi
    """
    __tablename__ = "accident_views"

    accident_id: Mapped[int] = mapped_column(
        ForeignKey("accidents.id", ondelete='CASCADE'),
        nullable=False
    )
    user_id: Mapped[int] = mapped_column(nullable=False)  # Telegram user_id

    # Relationships
    accident: Mapped["Accident"] = relationship(back_populates="views")

    # ✅ UNIQUE CONSTRAINT - User faqat 1 marta
    __table_args__ = (
        UniqueConstraint('accident_id', 'user_id', name='unique_accident_user_view'),
    )

    def __str__(self):
        return f"AccidentView(accident_id={self.accident_id}, user_id={self.user_id})"


class Accident(CreatedModel):
    """Baxtsiz hodisalar"""
    __tablename__ = "accidents"

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    file_pdf: Mapped[str] = mapped_column(String, nullable=False)

    year_id: Mapped[int] = mapped_column(
        ForeignKey("accident_years.id", ondelete='RESTRICT')
    )
    category_id: Mapped[int] = mapped_column(
        ForeignKey("accident_categories.id", ondelete='RESTRICT')
    )

    year: Mapped["AccidentYear"] = relationship(back_populates="accidents")
    category: Mapped["AccidentCategory"] = relationship(back_populates="accidents")

    # ✅ YANGI RELATIONSHIP - VIEWS
    views: Mapped[list["AccidentView"]] = relationship(
        back_populates="accident",
        cascade="all, delete-orphan"
    )

    @property
    def views_count(self) -> int:
        """Unique userlar soni"""
        return len(self.views)

    def __str__(self):
        return self.title


# ============================================
# GURUH MODELI
# Yopiq guruh - zayavka jo'natish uchun
# ============================================

class Group(CreatedModel):
    __tablename__ = "groups"

    chat_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)  # Guruh ID
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)  # Guruh nomi
    link: Mapped[str | None] = mapped_column(String, nullable=True)  # Guruh linki (ixtiyoriy)
    is_required: Mapped[bool] = mapped_column(Boolean, default=True)  # Majburiy guruhmi

    def __str__(self):
        return self.title or "Guruh"


# ============================================
# STATISTIKA MODELI
# Foydalanuvchi faolligi
# ============================================

class UserActivity(CreatedModel):
    """
    Foydalanuvchi faolligi
    Har bir muhim faoliyat saqlanadi (test, konspekt, video, folder...)
    """
    __tablename__ = "user_activities"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete='CASCADE'))
    activity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # 'test_start', 'conspect_view', 'video_view', 'folder_open', 'accident_view'

    section: Mapped[str | None] = mapped_column(String(10), nullable=True)  # 'MM', 'SX'
    parent_type: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # 'nizomlar', 'kranlar', 'himoya_vositalari', 'qozonxonalar', ...

    # created_at - avtomatik CreatedModel'dan

    def __str__(self):
        return f"{self.user_id} - {self.activity_type} ({self.section})"


metadata = Base.metadata
