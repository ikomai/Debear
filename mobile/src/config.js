import Constants from "expo-constants";

/**
 * Base URL of the FastAPI backend.
 *
 * When you run the app through Expo Go on your phone, the backend must be
 * reachable on your computer's LAN IP (not "localhost", which would point to
 * the phone itself). We auto-derive the computer's IP from the Expo dev-server
 * host, so it "just works" as long as the phone and PC are on the same Wi-Fi
 * and the backend runs with:  uvicorn api.main:app --host 0.0.0.0 --port 8000
 *
 * If auto-detection fails, set API_BASE_URL manually below.
 */
const PORT = 8000;

// 1) In a production build (APK), use the public backend URL baked into
//    app.json -> expo.extra.apiUrl. This is what makes the app work anywhere.
const prodApiUrl = Constants.expoConfig?.extra?.apiUrl;

// 2) In Expo Go (development), auto-derive the PC's LAN IP from the dev server.
const hostUri =
  Constants.expoConfig?.hostUri ||
  Constants.manifest2?.extra?.expoGo?.developer?.host ||
  "";
const lanIp = hostUri.split(":")[0];

export const API_BASE_URL =
  (prodApiUrl && prodApiUrl.trim()) ||
  (lanIp ? `http://${lanIp}:${PORT}` : `http://localhost:${PORT}`);
