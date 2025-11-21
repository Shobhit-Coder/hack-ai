import { create } from "zustand";
import { adminApi, adminApi as api } from "../lib/fakeApi";
import type { Candidate, Interview, InterviewDetail, JobItem, JobPosting, Settings } from "../types/models";

interface AppState {
  loading: boolean;
  jobs: JobItem[];
  candidates: Candidate[];
  interviews: Interview[];
  settings?: Settings;
  metrics?: Record<string, unknown>;
  category?: Record<string, unknown>;
  job_status?: Record<string, unknown>;
  bootstrap: () => Promise<void>;
  getJob:() => Promise<void>;
  getCandidates:() => Promise<void>;
  getInterview:() => Promise<void>;
  interviewDetails?: InterviewDetail | null;
  getInterviewDetails: (interviewId: string) => Promise<void>;
  addJob: (payload: {
    title: string;
    descriptionText?: string;
    category?: string;
    company_name?: string;
    location?: string;
    is_remote?: boolean;
    application_deadline?: string;
    // job_status?: string;
  }) => Promise<unknown>;
  addCandidate: (jobID:string, resumeBase64?: string | null) => Promise<void>;
  startInterview: (jobId:string, candidateId:string)=> Promise<void>;
  saveSettings: (s: Settings)=> Promise<void>;
  issueInvite: (interviewId: string) => Promise<void>
}

export const useAppStore = create<AppState>((set, get) => ({
  loading: false,
  jobs: [],
  candidates: [],
  interviews: [],
  settings: undefined,
  interviewDetails: null,

  async bootstrap(){
    set({ loading: true });
    const res = await api.getDashboardData();
    set({ metrics: res?.metrics, category: res?.category, job_status: res?.job_status, loading: false });
  },
  async getJob(page = 1, pageSize = 10){
    set({ loading: true });
    const allJob = await api.listJobs({ page, pageSize });
    set({jobs: allJob, loading: false})
  },
  async addJob(payload:{title: string, descriptionText: string, category: string, company_name: string, location: string, is_remote?: boolean,application_deadline?: string }){
    try {
      const created = await api.createJob(payload);
      return created;
    } catch (err) {
      console.error("addJob store error", err);
      throw err;
    }
  },
  async getCandidates(page = 1, pageSize = 10){
    set({ loading: true });
    const allCandidates = await api.listCandidates({ page, pageSize });
    set({candidates: allCandidates, loading: false})
  },
  async addCandidate(jobID: string, resumeBase64?: string | null){
    try {
      const created = await adminApi.createCandidate({ jobID, resumeFile: resumeBase64 });
      const prev = get().candidates;
      return created;
    } catch (err) {
      console.error("addCandidate store error", err);
      throw err;
    }
  },
  async getInterview(page = 1, pageSize = 10){
    set({ loading: true });
    const allInterviews = await api.listInterviews({ page, pageSize });
    set({interviews: allInterviews, loading:false})
  },
  async getInterviewDetails(interviewId: string) {
    if (!interviewId) throw new Error("interviewId required");
    set({ loading: true });
    try {
      const data = await api.getInterviewDetails(interviewId);
      set({ interviewDetails: data, loading: false });
    } catch (err: any) {
      console.error("getInterviewDetails error", err);
      set({ interviewDetails: null, loading: false });
      throw err;
    }
  },
  async issueInvite(interviewId: string){
    set({ loading: true });
    try {
      const inv = await api.issueInvite(interviewId);
    } catch (e: any) {
      console.error("issueInvite error", e);
      // toast.error(e.message ?? "Failed to issue invite");
    }
    set({ loading: false });
  },
  async startInterview(jobId : string, candidateId : string){
    const i = await api.startInterview(jobId, candidateId);
    set({ interviews: [i, ...get().interviews] });
  },

  async saveSettings(s: Settings){
    const saved = await api.updateSettings(s);
    set({ settings: saved });
  },
}));
