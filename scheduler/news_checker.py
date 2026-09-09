import logging

from services.wordpress_api import get_latest_posts
from services.subscription import get_last_post_id, get_subscribers, set_last_post_id

logger = logging.getLogger(__name__)


async def check_new_news(context) -> None:
    if not get_subscribers():
        return
    posts = await get_latest_posts(limit=3)
    if not posts:
        return

    new_posts = [p for p in posts if p["id"] > get_last_post_id()]
    if not new_posts:
        return

    for post in new_posts:
        for chat_id in get_subscribers():
            try:
                await context.bot.send_message(
                    chat_id,
                    f"🆕 <b>BERITA BARU</b>\n\n{post['title']}\n🔗 {post['link']}",
                    parse_mode="HTML",
                    disable_web_page_preview=True,
                )
            except Exception:
                logger.warning("Gagal kirim ke %s", chat_id)

    set_last_post_id(max(p["id"] for p in posts))