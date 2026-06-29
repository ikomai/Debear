# Debear — mobile app (Expo / React Native)

The same insurance flow as the Telegram bot, as a phone app. It talks to the
FastAPI backend (`../api`) which shares the bot's database and validation.

## What's inside
- 🏠 Home menu
- 📝 Full application form (property, validated address, details, owner,
  mortgage, coverage, risks, sum & term, extra questions, consent)
- ✅ Real-data checks: country (offline) + city/street (geocoder) with
  "did you mean" suggestion chips — same logic as the bot
- 📋 My applications + status
- 📄 Application detail + open PDF

## Prerequisites
- Node.js (you have v22) — no Android Studio needed
- The **Expo Go** app on your phone (App Store / Google Play)
- Phone and PC on the **same Wi-Fi**

## Run

**1. Start the backend** (from the project root, in the Python venv):
```powershell
cd "$env:USERPROFILE\Desktop\UpWork_TG"
.\.venv\Scripts\python.exe -m uvicorn api.main:app --host 0.0.0.0 --port 8000
```
Check it: open http://localhost:8000/docs in a browser.

**2. Start the app:**
```powershell
cd "$env:USERPROFILE\Desktop\UpWork_TG\mobile"
npm install        # first time only
npx expo start
```
A QR code appears in the terminal. Open **Expo Go** on your phone and scan it.
The app auto-detects your PC's LAN IP for the backend (see `src/config.js`).

> If the app can't reach the backend, set the IP manually in `src/config.js`
> (`API_BASE_URL`). Find your PC IP with `ipconfig` (IPv4 Address).

## Notes / roadmap
- **Auth:** the app identifies a user by a random device id (stored locally),
  used like a Telegram id on the backend. Add real auth (SMS/OAuth) for
  production.
- **Document upload** from the phone (camera/gallery) is the one feature not
  yet wired (the bot uses Telegram file ids). Add `expo-image-picker` + a
  multipart upload endpoint to reach full parity.
- For production, point the backend at MySQL (`DB_ENGINE=mysql`) and host it
  behind HTTPS.
