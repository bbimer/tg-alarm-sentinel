import asyncio
import time
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import config
import state_manager

bot = Bot(token=config.ADMIN_BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

class TargetStates(StatesGroup):
    waiting_for_target = State()

def build_main_keyboard() -> InlineKeyboardMarkup:
    state = state_manager.load_state()
    is_sleeping = state.get("is_sleeping", True)
    
    toggle_text = "☀️ Переключить на: НЕ СПЛЮ" if is_sleeping else "💤 Переключить на: СПЛЮ"
    toggle_callback = "set_awake" if is_sleeping else "set_sleep"
    
    kb = [
        [InlineKeyboardButton(text=toggle_text, callback_data=toggle_callback)],
        [
            InlineKeyboardButton(text="⏳ Не спать 2ч", callback_data="timer_2"),
            InlineKeyboardButton(text="⏳ Не спать 4ч", callback_data="timer_4"),
            InlineKeyboardButton(text="⏳ Не спать 8ч", callback_data="timer_8")
        ],
        [
            InlineKeyboardButton(text="🎯 Управление целями", callback_data="manage_targets"),
            InlineKeyboardButton(text="🔄 Обновить статус", callback_data="refresh_status")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def build_targets_keyboard() -> InlineKeyboardMarkup:
    targets = state_manager.get_targets()
    kb = []
    
    for t in targets:
        kb.append([
            InlineKeyboardButton(text=f"📌 {t}", callback_data=f"info_target_{t}"),
            InlineKeyboardButton(text=f"❌ Удалить", callback_data=f"del_target_{t}")
        ])
        
    kb.append([InlineKeyboardButton(text="➕ Добавить цель", callback_data="add_target_btn")])
    kb.append([InlineKeyboardButton(text="🔙 Главное меню", callback_data="refresh_status")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_status_text() -> str:
    state = state_manager.load_state()
    is_sleeping = state.get("is_sleeping", True)
    auto_wake = state.get("auto_wake_until", 0)
    last_trigger = state.get("last_trigger_time", "Никогда")
    total_alerts = state.get("total_alerts_count", 0)
    targets = state_manager.get_targets()
    
    status_icon = "💤" if is_sleeping else "☀️"
    status_title = "СПЛЮ (Алерты со звонком ВКЛЮЧЕНЫ)" if is_sleeping else "БОДРСТВУЮ (Звонки ОТКЛЮЧЕНЫ)"
    
    timer_info = ""
    if not is_sleeping and auto_wake > 0:
        remaining_min = int((auto_wake - time.time()) / 60)
        timer_info = f"\n⏱ **Авто-включение сна через:** `{remaining_min}` мин."

    targets_str = ", ".join([f"`{t}`" for t in targets]) if targets else "_Нет целей_"

    return (
        f"⚙️ **TG ALARM - ПАНЕЛЬ УПРАВЛЕНИЯ**\n\n"
        f"Текущий режим: {status_icon} **{status_title}**{timer_info}\n\n"
        f"🎯 **Активные цели ({len(targets)}):** {targets_str}\n\n"
        f"📊 **Статистика:**\n"
        f"▪️ Всего алертов: `{total_alerts}`\n"
        f"▪️ Последний триггер: `{last_trigger}`\n"
        f"▪️ Время сервера: `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`"
    )

@dp.message(Command("start", "menu"))
async def cmd_start(message: types.Message, state: FSMContext):
    if config.ADMIN_CHAT_ID and message.from_user.id != config.ADMIN_CHAT_ID:
        await message.reply("⛔ Доступ запрещен.")
        return
    await state.clear()
    await message.answer(get_status_text(), reply_markup=build_main_keyboard(), parse_mode="Markdown")

@dp.callback_query(F.data == "set_sleep")
async def cb_set_sleep(callback: types.CallbackQuery):
    if config.ADMIN_CHAT_ID and callback.from_user.id != config.ADMIN_CHAT_ID:
        await callback.answer("⛔ Нет доступа", show_alert=True)
        return
    state_manager.set_sleeping(True)
    await callback.answer("💤 Режим СНА включен! Теперь при входящих сообщениях будет звонок.")
    await callback.message.edit_text(get_status_text(), reply_markup=build_main_keyboard(), parse_mode="Markdown")

@dp.callback_query(F.data == "set_awake")
async def cb_set_awake(callback: types.CallbackQuery):
    if config.ADMIN_CHAT_ID and callback.from_user.id != config.ADMIN_CHAT_ID:
        await callback.answer("⛔ Нет доступа", show_alert=True)
        return
    state_manager.set_sleeping(False)
    await callback.answer("☀️ Режим БОДРСТВОВАНИЯ включен. Звонки отключены.")
    await callback.message.edit_text(get_status_text(), reply_markup=build_main_keyboard(), parse_mode="Markdown")

@dp.callback_query(F.data.startswith("timer_"))
async def cb_timer(callback: types.CallbackQuery):
    if config.ADMIN_CHAT_ID and callback.from_user.id != config.ADMIN_CHAT_ID:
        await callback.answer("⛔ Нет доступа", show_alert=True)
        return
    hours = float(callback.data.split("_")[1])
    state_manager.set_sleeping(False, wake_hours=hours)
    await callback.answer(f"⏳ Звонки отключены на {hours} ч. Режим сна включится автоматически!")
    await callback.message.edit_text(get_status_text(), reply_markup=build_main_keyboard(), parse_mode="Markdown")

@dp.callback_query(F.data == "refresh_status")
async def cb_refresh(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer("Обновлено!")
    await callback.message.edit_text(get_status_text(), reply_markup=build_main_keyboard(), parse_mode="Markdown")

@dp.callback_query(F.data == "manage_targets")
async def cb_manage_targets(callback: types.CallbackQuery):
    targets = state_manager.get_targets()
    text = (
        f"🎯 **УПРАВЛЕНИЕ ЦЕЛЯМИ МОНИТОРИНГА**\n\n"
        f"Вы можете отслеживать любых ботов, пользователей, каналы или группы.\n\n"
        f"Список активных целей: `{len(targets)}`"
    )
    await callback.message.edit_text(text, reply_markup=build_targets_keyboard(), parse_mode="Markdown")

@dp.callback_query(F.data.startswith("del_target_"))
async def cb_del_target(callback: types.CallbackQuery):
    target = callback.data.replace("del_target_", "")
    removed = state_manager.remove_target(target)
    if removed:
        await callback.answer(f"✅ Цель {target} удалена!")
    else:
        await callback.answer("⚠️ Не удалось удалить")
    await cb_manage_targets(callback)

@dp.callback_query(F.data == "add_target_btn")
async def cb_add_target_prompt(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(TargetStates.waiting_for_target)
    cancel_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отмена", callback_data="manage_targets")]
    ])
    await callback.message.edit_text(
        "➕ **Отправьте username или ID цели:**\n\n"
        "Примеры:\n"
        "▪️ `@furyadmin_bot`\n"
        "▪️ `123456789`\n"
        "▪️ `@my_important_channel`",
        reply_markup=cancel_kb,
        parse_mode="Markdown"
    )

@dp.message(TargetStates.waiting_for_target)
async def process_add_target(message: types.Message, state: FSMContext):
    if config.ADMIN_CHAT_ID and message.from_user.id != config.ADMIN_CHAT_ID:
        return
    text = message.text.strip()
    if text:
        added = state_manager.add_target(text)
        await state.clear()
        if added:
            await message.reply(f"✅ Цель **{text}** успешно добавлена в мониторинг!", parse_mode="Markdown")
        else:
            await message.reply(f"⚠️ Цель **{text}** уже находится в списке!", parse_mode="Markdown")
        
        # Send updated main menu
        await message.answer(get_status_text(), reply_markup=build_main_keyboard(), parse_mode="Markdown")

async def main():
    print("[+] Starting TG Alarm Admin Bot...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
