import os
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ChatMemberStatus

# 1. Botni sozlash va Oltin Sozlamalar
BOT_TOKEN = 7937531270:AAG3XeMB4iPIFxuSVHLMg_zIlFGQgv0vBso  # @BotFather bergan kod
CHANNELS = ["@telefon_bozor_off"]        # Majburiy a'zolik kanalingiz (masalan: @telefon_bozor)

# Loglarni sozlash (Xatoliklarni ko'rish uchun)
logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# 2. Majburiy a'zolikni tekshirish funksiyasi (Daxshatli tezkor)
async def check_subscription(user_id: int) -> bool:
    for channel in CHANNELS:
        try:
            member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status in [ChatMemberStatus.LEFT, ChatMemberStatus.KICKED]:
                return False
        except Exception as e:
            logging.error(f"Kanalni tekshirishda xato: {e}")
            return False
    return True

# 3. /start buyrug'i - Zamonaviy interfeys dizayni
@dp.message(Command("start"))
async def start_command(message: types.Message):
    user_name = message.from_user.first_name
    is_subbed = await check_subscription(message.from_user.id)
    
    if not is_subbed:
        # Agar kanala a'zo bo'lmasa, daxshatli inline tugma chiqadi
        builder = InlineKeyboardBuilder()
        for channel in CHANNELS:
            builder.row(types.InlineKeyboardButton(text="📢 Kanalga a'zo bo'lish", url=f"https://t.me/{channel.replace('@', '')}"))
        builder.row(types.InlineKeyboardButton(text="✅ Tekshirish / Ishga tushirish", callback_data="check_sub"))
        
        await message.answer(
            f"⚡️ **Xush kelibsiz, {user_name}!**\n\n"
            f"Botni daxshatli rejimda ishga tushirish va barcha funksiyalardan tekinga foydalanish uchun "
            f"homiy kanalimizga a'zo bo'lishingiz shart. 🚀",
            parse_mode="Markdown",
            reply_markup=builder.as_markup()
        )
        return

    # Agar a'zo bo'lgan bo'lsa - Premium Dizayn
    await message.answer(
        f"👑 **MUTANT MEDIA DOWNLOADER v1.0** 👑\n\n"
        f"Salom, **{user_name}**! Bot Malibu motoridek silliq holatda tayyor.\n\n"
        f"📥 **Men nimalar qila olaman:**\n"
        f"• TikTok videolar (Suv belgisiz)\n"
        f"• Instagram Reels & Postlar\n"
        f"• YouTube Videolar & Shorts\n"
        f"• Istalgan qo'shiq va musiqalar\n\n"
        f"⚡️ **Menga shunchaki ssilka (link) yoki musiqa nomini yuboring!**",
        parse_mode="Markdown"
    )

# 4. Tekshirish tugmasi bosilganda (Callback Query)
@dp.callback_query(F.data == "check_sub")
async def process_check_sub(callback_query: types.CallbackQuery):
    is_subbed = await check_subscription(callback_query.from_user.id)
    
    if is_subbed:
        await callback_query.message.delete()
        await callback_query.message.answer(
            "🚀 **A'zolik tasdiqlandi!** Bot to'liq aktivlashdi.\n"
            "Menga ssilka yoki musiqa nomini yuboring, daxshatli tezlikda yuklab beraman!",
            parse_mode="Markdown"
        )
    else:
        await callback_query.answer("❌ Siz hali kanalga a'zo bo'lmadingiz! Iltimos, ro'yxatdan o'ting.", show_alert=True)

# 5. Ssilka yoki Musiqa kelganda ishlaydigan asosiy blok
@dp.message()
async def handle_multimedia(message: types.Message):
    # Avval a'zolikni tekshiramiz
    is_subbed = await check_subscription(message.from_user.id)
    if not is_subbed:
        await start_command(message)
        return

    text = message.text
    
    # Yuklanmoqda animatsiyasi (Zamonaviy effekt)
    status_msg = await message.answer("🔄 **So'rov qabul qilindi. Kontent 'Malibu' tezligida qayta ishlanmoqda...**", parse_mode="Markdown")

    try:
        # INSTAGRAM YUKLOVCHI TIZIM
        if "instagram.com" in text:
            await status_msg.edit_text("📥 *Instagram serverlaridan video sug'urib olinmoqda...*", parse_mode="Markdown")
            # Bu yerga API yoki yuklovchi skript ulanadi
            # Hozircha namuna uchun tayyor video yuborish:
            await message.reply_video(video="https://utils.tg.dev/static/video.mp4", caption="🔥 @mutantprime_media loyihasi taqdim etadi!")
            
        # TIKTOK YUKLOVCHI TIZIM
        elif "tiktok.com" in text:
            await status_msg.edit_text("⚡️ *TikTok videosi suv belgisiz (No Watermark) yuklanmoqda...*", parse_mode="Markdown")
            await message.reply_video(video="https://utils.tg.dev/static/video.mp4", caption="🚀 TikTok'dan daxshatli yuklov!")

        # YOUTUBE YUKLOVCHI TIZIM
        elif "youtube.com" in text or "youtu.be" in text:
            await status_msg.edit_text("🎬 *YouTube serverlaridan Shorts/Video yuklanmoqda...*", parse_mode="Markdown")
            await message.reply_video(video="https://utils.tg.dev/static/video.mp4", caption="🌟 YouTube daxshatli tahriri!")

        # MUSIQA QIDIRUV TIZIMI (Agar ssilka bo'lmasa, demak qo'shiq nomi)
        else:
            await status_msg.edit_text(f"🔍 *'{text}' musiqasi global bazadan qidirilmoqda...*", parse_mode="Markdown")
            # Namuna sifatida audio fayl qaytarish:
            await message.reply_audio(audio="https://utils.tg.dev/static/audio.mp3", title=text, performer="Monster Music")

        # Ish bitgandan keyin "Yuklanmoqda" xabarini o'chirib tashlaymiz
        await status_msg.delete()

    except Exception as e:
        await status_msg.edit_text(f"❌ **Xatolik yuz berdi!** Ssilka noto'g'ri yoki server band. Birozdan so'ng urunib ko'ring.")
        logging.error(f"Yuklashda xato: {e}")

# 6. Botni daxshatli yuritish (Polling)
if __name__ == "__main__":
    dp.run_polling(bot)
                                                                                                                      
