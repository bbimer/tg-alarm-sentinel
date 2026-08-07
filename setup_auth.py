import asyncio
from telethon import TelegramClient
import config

async def setup():
    print("========================================")
    print("  TG ALARM - ONE-TIME SESSION AUTH SETUP")
    print("========================================")
    print("\n1. Authorizing Main Monitor Account...")
    
    if not config.TG_API_ID or not config.TG_API_HASH:
        print("[!] Please set TG_API_ID and TG_API_HASH in .env first!")
        return

    client = TelegramClient("monitor_session", config.TG_API_ID, config.TG_API_HASH)
    await client.start(phone=config.TG_PHONE)
    me = await client.get_me()
    print(f"[SUCCESS] Monitor Account logged in as: {me.first_name} (@{me.username}) ID: {me.id}")
    await client.disconnect()

    if config.CALLER_PHONE and config.CALLER_API_ID:
        print("\n2. Authorizing Caller Account (Second TG account)...")
        caller_client = TelegramClient(config.CALLER_SESSION_NAME, config.CALLER_API_ID, config.CALLER_API_HASH)
        await caller_client.start(phone=config.CALLER_PHONE)
        caller_me = await caller_client.get_me()
        print(f"[SUCCESS] Caller Account logged in as: {caller_me.first_name} (@{caller_me.username}) ID: {caller_me.id}")
        await caller_client.disconnect()
    else:
        print("\n[!] Caller account credentials not provided in .env (Skipped).")

    print("\n[OK] Sessions initialized successfully! `monitor_session.session` created.")

if __name__ == "__main__":
    asyncio.run(setup())
