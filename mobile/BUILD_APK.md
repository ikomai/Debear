# Building the Debear APK (works outside your home Wi-Fi)

The app is already configured to talk to your backend through a public
Cloudflare tunnel (baked into `app.json` → `expo.extra.apiUrl`). The APK is
built in the cloud with **EAS Build** — no Android Studio needed.

## One-time: build the APK

```powershell
cd "$env:USERPROFILE\Desktop\UpWork_TG\mobile"

# 1. Log in (create a free account at https://expo.dev if you don't have one)
eas login

# 2. Start the cloud build (APK profile)
eas build -p android --profile preview
```

On the first run EAS will ask to:
- create the project on your Expo account → **Yes**
- generate a new Android Keystore → **Yes** (EAS keeps it for you)

The build runs on Expo's servers (~10–20 min). When it finishes, the terminal
prints a **download link** for the `.apk` (also available at
https://expo.dev → your project → Builds).

## Install on a phone
1. Download the `.apk` to the phone (open the link, or send it via Telegram).
2. Tap it → allow "Install unknown apps" if prompted → Install.
3. Open **Debear**. It will reach your backend through the tunnel from any
   network (mobile data, other Wi-Fi, etc.).

---

## ⚠️ Important: what keeps the APK working

The APK points at the tunnel URL baked at build time. It works **only while
all of these are running on your PC**:
- the backend (`uvicorn api.main:app ... :8000`)
- the Cloudflare tunnel (`cloudflared tunnel --url http://localhost:8000`)
- (the bot, if you also want Telegram)

### The tunnel URL changes when cloudflared restarts
A free "quick tunnel" gets a **random URL each time** it starts. If you restart
cloudflared (or reboot the PC), the URL changes and the old APK can no longer
connect — you'd update `expo.extra.apiUrl` and rebuild.

To get a **stable URL** (no rebuilds), either:
- use a **named Cloudflare tunnel** (free, needs a Cloudflare account + a
  domain), or
- host the backend on a **VPS** with a fixed domain (true 24/7 production).

When you're ready for that, I can set it up.
