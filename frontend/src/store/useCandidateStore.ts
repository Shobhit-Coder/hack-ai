import { create } from "zustand";
import type { InterviewInvite } from "../types/models";
import { candidateApi } from "../lib/fakeApi";
interface CandidateState {
  invite?: InterviewInvite;
  loading: boolean;
  error?: string;
  fetchInvite: (token: string) => Promise<void>;
  start: (token: string) => Promise<void>;
  send: (token: string, text: string) => Promise<void>;
  refreshTranscript: (token: string) => Promise<void>;
}
export const useCandidateStore = create<CandidateState>((set, get) => ({
  invite: undefined,
  loading: false,
  error: undefined,
  async fetchInvite(token) {
    set({ loading: true, error: undefined });
    try {
      const inv = await candidateApi.getInvite(token);
      set({ invite: inv });
    } catch (e: any) {
      set({ error: e.message });
    } finally {
      set({ loading: false });
    }
  },
  async start(token) {
    set({ loading: true });
    try {
      const inv = await candidateApi.acceptInvite(token);
      set({ invite: inv });
    } finally {
      set({ loading: false });
    }
  },
  async send(token, text) {
    set({ loading: true });
    try {
      const inv = await candidateApi.sendAnswer(token, text);
      set({ invite: inv });
    } finally {
      set({ loading: false });
    }
  },
  async refreshTranscript(token) {
    const inv = get().invite;
    if (!inv) return;
    const data = await candidateApi.getTranscript(token);
    set({
      invite: { ...inv, transcript: data.transcript, endsAt: data.endsAt },
    });
  },
}));
