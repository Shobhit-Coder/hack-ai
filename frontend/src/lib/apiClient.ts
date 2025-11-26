import axios from "axios";

const baseURL = import.meta.env.VITE_API_URL || "https://4db7912fce77.ngrok-free.app/api";
export const api = axios.create({
  baseURL,
  // headers: {
  //   "Content-Type": "application/json",
  // },
  timeout: 10000,
});

// Add interceptors if needed
api.interceptors.response.use(
  (res) => res,
  (err) => {
    console.error("API Error:", err);
    return Promise.reject(err);
  }
);
