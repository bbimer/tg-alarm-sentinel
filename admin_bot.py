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
    
    toggle_text = "☀️ Switch to: AWAKE" if is_sleeping else "💤 Switch to: SLEEPING"
    toggle_callback = "set_awake" if is_sleeping else "set_sleep"
    
    kb = [
        [InlineKeyboardButton(text=toggle_text, callback_data=toggle_callback)],
        [
            InlineKeyboardButton(text="⏳ Awake 2h", callback_data="timer_2"),
            InlineKeyboardButton(text="⏳ Awake 4h", callback_data="timer_4"),
            InlineKeyboardButton(text="⏳ Awake 8h", callback_data="timer_8")
        ],
        [
            InlineKeyboardButton(text="🎯 Manage Targets", callback_data="manage_targets"),
            InlineKeyboardButton(text="🔄 Refresh Status", callback_data="refresh_status")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def build_targets_keyboard() -> InlineKeyboardMarkup:
    targets = state_manager.get_targets()
    kb = []
    
    for t in targets:
        kb.append([
            InlineKeyboardButton(text=f"📌 {t}", callback_data=f"info_target_{t}"),
            InlineKeyboardButton(text=f"❌ Remove", callback_data=f"del_target_{t}")
        ])
        
    kb.append([InlineKeyboardButton(text="➕ Add Target", callback_data="add_target_btn")])
    kb.append([InlineKeyboardButton(text="🔙 Main Menu", callback_data="refresh_status")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_status_text() -> str:
    state = state_manager.load_state()
    is_sleeping = state.get("is_sleeping", True)
    auto_wake = state.get("auto_wake_until", 0)
    last_trigger = state.get("last_trigger_time", "Never")
    total_alerts = state.get("total_alerts_count", 0)
    targets = state_manager.get_targets()
    
    status_icon = "💤" if is_sleeping else "☀️"
    status_title = "SLEEPING (Voice Calls ON)" if is_sleeping else "AWAKE (Voice Calls OFF)"
    
    timer_info = ""
    if not is_sleeping and auto_wake > 0:
        remaining_min = int((auto_wake - time.time()) / 60)
        timer_info = f"\n⏱ **Auto-sleep in:** `{remaining_min}` mins"

    targets_str = ", ".join([f"`{t}`" for t in targets]) if targets else "_No active targets_"

    return (
        f"⚙️ **TG ALARM - CONTROL PANEL**\n\n"
        f"Current Mode: {status_icon} **{status_title}**{timer_info}\n\n"
        f"🎯 **Monitored Targets ({len(targets)}):** {targets_str}\n\n"
        f"📊 **Statistics:**\n"
        f"▪️ Total Alerts: `{total_alerts}`\n"
        f"▪️ Last Trigger: `{last_trigger}`\n"
        f"▪️ Server Time: `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`"
    )

@dp.message(Command("start", "menu"))
async def cmd_start(message: types.Message, state: FSMContext):
    if config.ADMIN_CHAT_ID and message.from_user.id != config.ADMIN_CHAT_ID:
        await message.reply("⛔ Access denied.")
        return
    await state.clear()
    await message.answer(get_status_text(), reply_markup=build_main_keyboard(), parse_mode="Markdown")

@dp.callback_query(F.data == "set_sleep")
async def cb_set_sleep(callback: types.CallbackQuery):
    if config.ADMIN_CHAT_ID and callback.from_user.id != config.ADMIN_CHAT_ID:
        await callback.answer("⛔ Access denied", show_alert=True)
        return
    state_manager.set_sleeping(True)
    await callback.answer("💤 SLEEP Mode ON! Voice calls enabled for new alerts.")
    await callback.message.edit_text(get_status_text(), reply_markup=build_main_keyboard(), parse_mode="Markdown")

@dp.callback_query(F.data == "set_awake")
async def cb_set_awake(callback: types.CallbackQuery):
    if config.ADMIN_CHAT_ID and callback.from_user.id != config.ADMIN_CHAT_ID:
        await callback.answer("⛔ Access denied", show_alert=True)
        return
    state_manager.set_sleeping(False)
    await callback.answer("☀️ AWAKE Mode ON. Voice calls disabled.")
    await callback.message.edit_text(get_status_text(), reply_markup=build_main_keyboard(), parse_mode="Markdown")

@dp.callback_query(F.data.startswith("timer_"))
async def cb_timer(callback: types.CallbackQuery):
    if config.ADMIN_CHAT_ID and callback.from_user.id != config.ADMIN_CHAT_ID:
        await callback.answer("⛔ Access denied", show_alert=True)
        return
    hours = float(callback.data.split("_")[1])
    state_manager.set_sleeping(False, wake_hours=hours)
    await callback.answer(f"⏳ Calls paused for {hours}h. Auto-sleep will trigger afterwards.")
    await callback.message.edit_text(get_status_text(), reply_markup=build_main_keyboard(), parse_mode="Markdown")

@dp.callback_query(F.data == "refresh_status")
async def cb_refresh(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer("Refreshed!")
    await callback.message.edit_text(get_status_text(), reply_markup=build_main_keyboard(), parse_mode="Markdown")

@dp.callback_query(F.data == "manage_targets")
async def cb_manage_targets(callback: types.CallbackQuery):
    targets = state_manager.get_targets()
    text = (
        f"🎯 **MONITORED TARGETS MANAGEMENT**\n\n"
        f"You can monitor any bots, users, channels, or groups.\n\n"
        f"Active Targets: `{len(targets)}`"
    )
    await callback.message.edit_text(text, reply_markup=build_targets_keyboard(), parse_mode="Markdown")

@dp.callback_query(F.data.startswith("del_target_"))
async def cb_del_target(callback: types.CallbackQuery):
    target = callback.data.replace("del_target_", "")
    removed = state_manager.remove_target(target)
    if removed:
        await callback.answer(f"✅ Target {target} removed!")
    else:
        await callback.answer("⚠️ Target not found")
    await cb_manage_targets(callback)

@dp.callback_query(F.data == "add_target_btn")
async def cb_add_target_prompt(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(TargetStates.waiting_for_target)
    cancel_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Cancel", callback_data="manage_targets")]
    ])
    await callback.message.edit_text(
        "➕ **Send target username or ID:**\n\n"
        "Examples:\n"
        "▪️ `@example_signal_bot`\n"
        "▪️ `123456789`\n"
        "▪️ `@important_channel`",
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
            await message.reply(f"✅ Target **{text}** successfully added to monitoring!", parse_mode="Markdown")
        else:
            await message.reply(f"⚠️ Target **{text}** is already in the list!", parse_mode="Markdown")
        
        await message.answer(get_status_text(), reply_markup=build_main_keyboard(), parse_mode="Markdown")

async def main():
    print("[+] Starting TG Alarm Admin Bot...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
