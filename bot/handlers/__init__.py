from bot.distpatchers import dp
from bot.handlers.common.conspect_handler import conspect_router
from bot.handlers.common.folder_handler import folder_router
from bot.handlers.common.test_handler import test_router
from bot.handlers.common.video_handler import video_router
from bot.handlers.group_events import group_router
from bot.handlers.language_handler import language_router
from bot.handlers.media_handler import media_router
from bot.handlers.mm.mm_accident_handler import accident_router
from bot.handlers.mm.mm_main_handler import mm_main_router
from bot.handlers.start_handler import main_router
from bot.handlers.sx.sx_main_handler import sx_main_router
from bot.handlers.text_handler import text_router

dp.include_routers(
    conspect_router,
    folder_router,
    test_router,
    video_router,
    accident_router,
    mm_main_router,
    sx_main_router,
    group_router,
    language_router,
    media_router,
    main_router,
    text_router,
)
