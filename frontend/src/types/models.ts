export type ID = string;
export type InterviewStatus = "not_started" | "in_progress" | "completed" | "incomplete";
export interface JobPosting { id: ID; title: string; descriptionText?: string; createdAt: string; }
export interface JobItem {
  id: string;
  created_at: string;
  modified_at: string;
  title: string;
  category: string;
  description: string;
  company_name: string;
  location: string;
  is_remote: boolean;
  posted_date: string;
  application_deadline: string | null;
  job_status: string;
}
export interface Candidate { id: ID; fullName: string; phoneE164: string; resumeFileUrl?: string; }
export interface Message { id: ID; interviewId: ID; direction: "outbound"|"inbound"; body: string; ts: string; }
export interface QA { index: number; question: string; type: "tech"|"experience"|"behavioral"; answer?: string; }
export interface Interview { id: ID; jobId: ID; candidateId: ID; status: InterviewStatus; updatedAt: string; }
export interface Settings { reminderIntervalMin: number; maxReminders: number; maxInactivityMinutes: number;
  scoringWeights: { skills:number; relevance:number; communication:number; completeness:number } }
export interface InterviewInvite {
  token: string; interviewId: ID; candidateId: ID; jobId: ID;
  timeLimitSec: number; createdAt: string; acceptedAt?: string; expiresAt: string; endsAt?: string;
  currentIndex: number; transcript: Array<{ role: "system"|"candidate"|"bot"; text: string; ts: string; }>;
}
export type InterviewDetail = {
  interview: {
    id: string;
    candidate_name: string;
    job_category: string;
    created_at: string;
    modified_at: string;
    scheduled_at?: string | null;
    started_at?: string | null;
    ended_at?: string | null;
    job_fit_score?: number | null;
    status?: string | null;
    candidate?: string | null;
    job?: string | null;
  };
  messages: Array<{
    message_id: string;
    created_at: string;
    modified_at?: string;
    direction: "inbound" | "outbound" | string;
    message_text: string;
    status?: string;
    interview?: string;
    related_question?: string | null;
  }>;
};