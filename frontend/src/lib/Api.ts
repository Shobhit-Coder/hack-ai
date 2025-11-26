import type {
  Settings,
} from "../types/models";
import { APPS_KEY } from "../constants";
import { api } from "./apiClient";
const wait = (ms: number) => new Promise((r) => setTimeout(r, ms));
const now = () => new Date().toISOString();
const uuid = () =>
  globalThis.crypto?.randomUUID?.() ?? Math.random().toString(36).slice(2);

let interviews = [
  {
    id: "iv1",
    jobId: "j1",
    candidateId: "c1",
    status: "in_progress",
    updatedAt: now(),
  },
  {
    id: "iv2",
    jobId: "j2",
    candidateId: "c2",
    status: "completed",
    updatedAt: now(),
  },
];
const questions: Record<string, string[]> = {
  iv1: [
    "Tell us about an API you built with FastAPI.",
    "How did you secure authentication and rate limiting?",
    "Describe a production incident and your fix.",
    "How do you optimize Postgres queries?",
    "What CI/CD pipeline have you set up?",
  ],
};
let invites: Record<string, string> = {
  xyz: "xyz",
  pqr: "pqr",
};
let settings: Settings = {
  reminderIntervalMin: 30,
  maxReminders: 3,
  maxInactivityMinutes: 240,
  scoringWeights: {
    skills: 0.4,
    relevance: 0.3,
    communication: 0.15,
    completeness: 0.15,
  },
};

function loadInvites() {
  try {
    return JSON.parse(localStorage.getItem("ai_sms_invites") || "{}");
  } catch {
    return {};
  }
}

function saveInvites(data: any) {
  localStorage.setItem("ai_sms_invites", JSON.stringify(data));
}

function lsGet<T>(key: string, fallback: T): T {
  try { const v = localStorage.getItem(key); return v ? JSON.parse(v) as T : fallback; }
  catch { return fallback; }
}
function lsSet<T>(key: string, v: T) { localStorage.setItem(key, JSON.stringify(v)); }

export const adminApi = {
  async getDashboardData() {
    const res = await api.get("/dashboard");
    console.log("Fetched dashboard data:", res, res.data);
    return res.data;
  },
  getAllInvites() {
    return loadInvites();
  },
  async listJobs({ page = 1, pageSize = 10 } = {}) {
    // await wait(150);
    const res = await api.get("/jobs", { params: { page, page_size: pageSize } });
    console.log("Fetched jobs data:", res, res.data);
    return res.data;
    // return [...jobs];
  },
  async createJob(p: {
  title: string;
  descriptionText?: string;
  category?: string;
  company_name?: string;
  location?: string;
  is_remote?: boolean;
  application_deadline?: string; // ISO
  // job_status?: string;
}) {
    // await wait(150);
    const payload = {
      title: p.title,
      description: p.descriptionText ?? "",
      category: p.category ?? "",
      company_name: p.company_name ?? "",
      location: p.location ?? "",
      is_remote: !!p.is_remote,
      application_deadline: p.application_deadline ?? null,
      // job_status: p.job_status ?? "Open",
    };
    try {
      // api is your axios instance (lib/apiClient.ts)
      const res = await api.post("/jobs/", payload);
      // backend should return created job object
      return res.data;
    } catch (err: any) {
      // rethrow so UI can show toast
      console.error("createJob error", err);
      throw err;
    }
  },
  async listCandidates({ page = 1, pageSize = 10 } = {}) {
    const res = await api.get("/candidates", { params: { page, page_size: pageSize } });
    console.log("Fetched candidates data:", res, res.data);
    return res.data;
    // return [...candidates];
  },
//   async createCandidate(p: { jobID: string;
//   // phoneE164: string;
//   // email?: string | null;
//   resumeFile?: File | null;
//  }) {
//     try {
//       const form = new FormData();
//       // adjust field names to match your backend
//       // const parts = (p.fullName || "").trim().split(/\s+/);
//       // const first_name = parts.shift() || "";
//       // const last_name = parts.join(" ") || "";
//       form.append("job_id", p?.jobID);
//       // form.append("last_name", last_name);
//       // form.append("phone_number", p.phoneE164);
//       // if (p.email) form.append("email", p.email);
//       if (p.resumeFile) form.append("file", p.resumeFile); // key name "resume" typical; change if backend expects "file" or "resume_file"
//       console.log("createCandidate form data:", form);
//       // Do not set Content-Type; axios will set it including boundary
//       const res = await api.post("/candidates/resumes", {

//     method: "POST",
//     // DO NOT set Content-Type here — browser will set it with boundary
//     body: form,
//     // credentials: "include" // only if you need cookies/auth
//   });
//       return res.data; // created candidate object
//     } catch (err: any) {
//       console.error("createCandidate error", err);
//       // rethrow so UI can show error details
//       throw err;
//     }
//   },
async createCandidate(p: { jobID: string; resumeFile?: File | null }) {
  try {
    console.log("createCandidate params", p);
    const form = new FormData();
    if (!p.jobID) throw new Error("jobID required");
    form.append("job_id", p.jobID);         // adjust key if backend expects a different name
    if (p.resumeFile) form.append("file", p.resumeFile); // adjust key to backend ("file" / "resume" / "cv")
    
    console.log("createCandidate params", p, form);
    // debug: log entries
    for (const [k, v] of form.entries()) console.log("form:", k, v);

    // If your axios instance has default headers forcing JSON,
    // temporarily remove that default for this request so browser/axios sets proper multipart header:
    const old = api.defaults?.headers?.post?.["Content-Type"];
    delete api.defaults.headers.post["Content-Type"];

    try {
      // Pass the FormData as the second argument; do NOT set Content-Type manually
      const res = await api.post("/candidates/resumes", form);
      return res.data;
    } finally {
      // restore previous default header (if any)
      if (old) api.defaults.headers.post["Content-Type"] = old;
    }
  } catch (err: any) {
    console.error("createCandidate error", err);
    throw err;
  }
}
,
  async listInterviews({ page = 1, pageSize = 10 } = {}) {
    const res = await api.get("/interviews", { params: { page, page_size: pageSize } });
    console.log("Fetched interviews data:", res, res.data);
    return res.data;
    // return [...interviews];
  },
  async getInterviewDetails(interviewId: string) {
  if (!interviewId) throw new Error("interviewId required");
  try {
    const res = await api.get(`/interviews/${interviewId}`);
    console.log("Fetched interview detail:", res, res.data);
    return res.data; // expected shape: { interview: {...}, messages: [...] }
  } catch (err: any) {
    console.error("getInterviewDetails error", err);
    throw err;
  }
},
  async startInterview(jobId: string, candidateId: string) {
    await wait(200);
    const i = {
      id: uuid(),
      jobId,
      candidateId,
      status: "not_started",
      updatedAt: now(),
    };
    interviews = [i, ...interviews];
    questions[i.id] = [
      "Please introduce yourself briefly for this role.",
      "Which achievement best demonstrates your fit for this job?",
      "Describe a challenging bug and how you solved it.",
      "Pick a project and explain your architecture choices.",
      "How do you manage time and priorities under pressure?",
    ];
    return i;
  },
  async issueInvite(interviewId: string) {
    try {
      const res = await api.post(`/interviews/${interviewId}/start`);
      console.log("Fetched interview detail:", res, res.data);
      return res.data; // expected shape: { interview: {...}, messages: [...] }
    } catch (err: any) {
      console.error("getInterviewDetails error", err);
      throw err;
    }
    // await wait(100);
    // const iv = interviews.find((x: any) => x.id === interviewId);
    // if (!iv) throw new Error("Interview not found");
    // const token = uuid().slice(0, 8);
    // const createdAt = now();
    // const expiresAt = new Date(Date.now() + 1000 * 60 * 60 * 24).toISOString();
    // const inv: InterviewInvite = {
    //   token,
    //   interviewId,
    //   candidateId: iv.candidateId,
    //   jobId: iv.jobId,
    //   timeLimitSec,
    //   createdAt,
    //   expiresAt,
    //   currentIndex: 0,
    //   transcript: [
    //     {
    //       role: "system",
    //       text: "Welcome! Click Start when ready. Your timer begins after you start.",
    //       ts: createdAt,
    //     },
    //   ],
    // };
    // const store = loadInvites();
    // store[token] = inv;
    // saveInvites(store);
    // // invites[token] = inv;
    // return inv;
  },
  async getSettings() {
    await wait(100);
    return settings;
  },
  async updateSettings(next: Settings) {
    await wait(100);
    settings = next;
    return settings;
  },
};
export const candidateApi = {
  async getInvite(token: string) {
    await wait(100);
    const store = loadInvites();
    const inv = store[token];
    // const inv = invites[token];
    if (!inv) throw new Error("Invite not found");
    return inv;
  },
  async acceptInvite(token: string) {
    await wait(120);
    const store = loadInvites();
    const inv = store[token];

    // const inv = invites[token];
    if (!inv) throw new Error("Invite not found");
    if (!inv.acceptedAt) {
      inv.acceptedAt = now();
      inv.endsAt = new Date(Date.now() + inv.timeLimitSec * 1000).toISOString();
      const iv = interviews.find((i: any) => i.id === inv.interviewId);
      if (iv) {
        iv.status = "in_progress";
        iv.updatedAt = now();
      }
      const q = questions[inv.interviewId]?.[0];
      if (q) inv.transcript.push({ role: "bot", text: q, ts: now() });
    }
    saveInvites(store);
    return inv;
  },
  async sendAnswer(token: string, answer: string) {
    await wait(140);
    const store = loadInvites();
    // const inv = invites[token];
    const inv = store[token];

    if (!inv) throw new Error("Invite not found");
    inv.transcript.push({ role: "candidate", text: answer, ts: now() });
    const list = questions[inv.interviewId] ?? [];
    const nextIndex = inv.currentIndex + 1;
    inv.currentIndex = nextIndex;
    const nextQ = list[nextIndex];
    if (nextQ) {
      inv.transcript.push({ role: "bot", text: nextQ, ts: now() });
    } else {
      const iv = interviews.find((i: any) => i.id === inv.interviewId);
      if (iv) {
        iv.status = "completed";
        iv.updatedAt = now();
      }
    }
    saveInvites(store);
    return inv;
  },
  async getTranscript(token: string) {
    await wait(100);
    const store = loadInvites();
    const inv = store[token];
    // const inv = invites[token];
    if (!inv) throw new Error("Invite not found");
    return {
      transcript: inv.transcript,
      endsAt: inv.endsAt,
      timeLimitSec: inv.timeLimitSec,
    };
  },
};

// --- PUBLIC JOBS & APPLY (stores applications in localStorage for now)

export const publicApi = {
  async listJobs(){ await wait(80); return adminApi.listJobs(); },
  async getJob(jobId: string){
    await wait(80);
    const list = await adminApi.listJobs();
    const j = list.find(j => j.id === jobId);
    if (!j) throw new Error("Job not found");
    return j;
  },
};
