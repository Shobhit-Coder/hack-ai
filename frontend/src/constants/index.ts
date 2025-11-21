export const APPS_KEY = "ai_sms_applications";
export const JOBS_KEY = "ai_sms_jobs";
export const CANDIDATES_KEY = "ai_sms_candidates";
export const SETTINGS_KEY = "ai_sms_settings";

export const INTERVIEW_STATES = {
  NOT_STARTED: 'not_started',
  INVITED: 'invited',
  IN_PROGRESS: 'in_progress',
  PAUSED: 'paused',
  COMPLETED: 'completed',
  INCOMPLETE_CLOSED: 'incomplete_closed'
} as const;


export const JOB_CATEGORIES = [
  "Backend Developer",
  "Cloud Architect",
  "Data Analyst",
  "Data Engineer",
  "DevOps Engineer",
  "Frontend Developer",
  "Frontend Engineer",
  "Full Stack Developer",
  "ML Engineer",
  "Product Manager",
  "QA Engineer",
  "SDET",
  "Software Engineer"
]