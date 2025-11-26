export const wait = (ms: number) => new Promise((r) => setTimeout(r, ms));
export const nowISO = () => new Date().toISOString();
export const uuid = () => globalThis.crypto?.randomUUID?.() ?? Math.random().toString(36).slice(2);
export const isValidPhone = (s: string) => /^\+?[1-9]\d{7,14}$/.test(s);
