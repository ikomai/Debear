import axios from "axios";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { API_BASE_URL } from "./config";

const client = axios.create({ baseURL: API_BASE_URL, timeout: 15000 });

/** A stable per-device id (used like a Telegram user id on the backend). */
export async function getClientId() {
  let id = await AsyncStorage.getItem("client_id");
  if (!id) {
    id = String(Math.floor(100000000 + Math.random() * 900000000));
    await AsyncStorage.setItem("client_id", id);
  }
  return Number(id);
}

export async function getMeta() {
  const { data } = await client.get("/api/meta");
  return data;
}

export async function validateField(kind, value, ctx = {}) {
  const { data } = await client.post(`/api/validate/${kind}`, { value, ...ctx });
  return data; // { ok, value, message, suggestions }
}

export async function createApplication(form) {
  const client_id = await getClientId();
  const { data } = await client.post("/api/applications", { client_id, ...form });
  return data;
}

export async function listApplications() {
  const client_id = await getClientId();
  const { data } = await client.get("/api/applications", { params: { client_id } });
  return data;
}

export async function getApplication(id) {
  const { data } = await client.get(`/api/applications/${id}`);
  return data;
}

export function pdfUrl(id) {
  return `${API_BASE_URL}/api/applications/${id}/pdf`;
}
