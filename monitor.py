import asyncio
import sys
from telethon import TelegramClient, events
import config
import alerter
import state_manager

# Ensure UTF-8 output encoding for Windows console
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

if not config.TG_API_ID or not config.TG_API_HASH:
    print("[-] Error: TG_API_ID and TG_API_HASH must be configured in .env")
    sys.exit(1)

client = TelegramClient("monitor_session", config.TG_API_ID, config.TG_API_HASH)

def get_active_targets():
    """Combines targets from state_manager and config"""
    targets = []
    # Add from state manager
    for t in state_manager.get_targets():
        clean = t.strip()
        if clean:
            if clean.lstrip("-").isdigit():
                targets.append(int(clean))
            else:
                targets.append(clean)
    # Add from config if not present
    if config.TARGET_BOT_USERNAME:
        for item in config.TARGET_BOT_USERNAME.split(","):
            clean = item.strip()
            if clean:
                val = int(clean) if clean.lstrip("-").isdigit() else clean
                if val not in targets:
                    targets.append(val)
    return targets

@client.on(events.NewMessage)
async def new_message_handler(event):
    sender = await event.get_sender()
    if not sender:
        return
        
    sender_id = getattr(sender, 'id', None)
    sender_username = getattr(sender, 'username', '')
    
    active_targets = get_active_targets()
    is_target = False
    
    for t in active_targets:
        if isinstance(t, int) and sender_id == t:
            is_target = True
            break
        elif isinstance(t, str):
            clean_t = t.lstrip("@").lower()
            if sender_username and sender_username.lower() == clean_t:
                is_target = True
                break
                
    if is_target:
        bot_identifier = f"@{sender_username}" if sender_username else f"ID:{sender_id}"
        msg_text = event.raw_text or ""
        print(f"[+] Intercepted message from target {bot_identifier}!")
        await alerter.handle_new_alert(client, bot_identifier, msg_text)

async def main():
    print("========================================")
    print("  TG ALARM - DYNAMIC MONITOR USERBOT    ")
    print(f"  Monitored Targets: {get_active_targets()}")
    print("========================================")
    
    await client.start(phone=config.TG_PHONE)
    print("[+] Monitor Userbot successfully connected to Telegram MTProto!")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
