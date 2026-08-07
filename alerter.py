import sys
import asyncio
import time
import requests
from telethon import TelegramClient
from telethon.tl.functions.phone import RequestCallRequest
import config
import state_manager

# Ensure UTF-8 output encoding for Windows console
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Cooldown lock to prevent call spamming (at most 1 call per 60 seconds)
_last_call_time = 0

async def trigger_tg_call_request(client, user_id: int):
    """
    Initiates a Telegram Call request via existing active Telethon client instance.
    """
    if not client or not client.is_connected():
        print("[!] Client is not connected, skipping TG call.")
        return False

    try:
        print(f"[>] Initiating Telegram Call to user...")
        # Resolve target user entity and convert to InputUser
        target_entity = await client.get_entity(config.ADMIN_CHAT_ID)
        input_user = __import__('telethon').tl.types.InputUser(
            user_id=target_entity.id,
            access_hash=target_entity.access_hash
        )
        
        # Generate valid DH key exchange parameter & sha256 hash
        import os, hashlib
        g_a = os.urandom(256)
        g_a_hash = hashlib.sha256(g_a).digest()

        call = await client(__import__('telethon').tl.functions.phone.RequestCallRequest(
            user_id=input_user,
            random_id=int(time.time()),
            g_a_hash=g_a_hash,
            protocol=__import__('telethon').tl.types.PhoneCallProtocol(
                min_layer=92,
                max_layer=92,
                udp_p2p=True,
                udp_reflector=True,
                library_versions=['1.0.0']
            )
        ))
        print(f"[+] Telegram Call successfully triggered! Status: {call}")
        return True
    except Exception as e:
        print(f"[!] Error making Telegram Call: {e}")
        return False

def trigger_twilio_call():
    """Backup call via Twilio API if credentials exist"""
    if not (config.TWILIO_ACCOUNT_SID and config.TWILIO_AUTH_TOKEN and config.TWILIO_TO_NUMBER):
        return False
    try:
        url = f"https://api.twilio.com/2010-04-01/Accounts/{config.TWILIO_ACCOUNT_SID}/Calls.json"
        data = {
            "Url": "http://demo.twilio.com/docs/voice.xml",
            "To": config.TWILIO_TO_NUMBER,
            "From": config.TWILIO_FROM_NUMBER
        }
        res = requests.post(url, data=data, auth=(config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN))
        print(f"[+] Twilio Call response: {res.status_code}")
        return res.status_code in [200, 201]
    except Exception as e:
        print(f"[!] Twilio call failed: {e}")
        return False

async def handle_new_alert(client, bot_username: str, message_text: str):
    """
    Central handler when a new message from the target bot is intercepted.
    """
    global _last_call_time
    
    state = state_manager.record_alert()
    is_sleeping = state.get("is_sleeping", True)
    
    alert_time = time.strftime("%H:%M:%S")
    snippet = message_text[:300] if message_text else "[Media / Empty Text]"
    
    print(f"\n[ALERT TRIGGERED] Target: {bot_username} | Sleep Mode: {is_sleeping} | Time: {alert_time}")
    
    # 1. Format admin notification text
    if is_sleeping:
        msg_header = "🚨🚨 **CRITICAL ALERT! SLEEP MODE ACTIVE!** 🚨🚨"
    else:
        msg_header = "ℹ️ **NEW MESSAGE FROM TARGET (Awake Mode)**"
        
    full_msg = (
        f"{msg_header}\n\n"
        f"🤖 **Sender:** `{bot_username}`\n"
        f"⏰ **Time:** `{alert_time}`\n\n"
        f"💬 **Message Content:**\n"
        f"```\n{snippet}\n```"
    )
    
    # 2. Send via Bot API
    if config.ADMIN_BOT_TOKEN and config.ADMIN_CHAT_ID:
        try:
            requests.post(
                f"https://api.telegram.org/bot{config.ADMIN_BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": config.ADMIN_CHAT_ID,
                    "text": full_msg,
                    "parse_mode": "Markdown",
                    "disable_notification": False
                },
                timeout=10
            )
        except Exception as e:
            print(f"[!] Failed sending Bot API message: {e}")

    # 3. Trigger Waking Call ONLY IF sleeping
    if is_sleeping:
        now = time.time()
        if now - _last_call_time > 45: # Cooldown protection
            _last_call_time = now
            
            # Attempt TG Call from Caller userbot
            call_success = await trigger_tg_call_request(client, config.ADMIN_CHAT_ID)
            
            # If TG Call failed or Twilio enabled, try Twilio call
            if not call_success and config.TWILIO_ACCOUNT_SID:
                print("[>] TG Call failed, falling back to Twilio call...")
                trigger_twilio_call()
        else:
            print("[!] Call skipped due to 45s cooldown protection.")

if __name__ == "__main__":
    print("Alerter module loaded.")
