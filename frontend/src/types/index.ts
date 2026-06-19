/// <reference types="vitest" />

export interface Profile {
  id: string;
  user_id: string;
  headline?: string;
  summary?: string;
  years_of_experience?: number;
  current_role?: string;
  preferred_roles: string[];
  location_city?: string;
  location_state?: string;
  location_country?: string;
  location_type?: string;
  open_to_work: boolean;
  target_salary_min?: number;
  target_salary_max?: number;
  target_salary_currency: string;
  created_at: string;
  updated_at: string;
  personal_info?: PersonalInfo;
  skills: Skill[];
  work_experiences: WorkExperience[];
  education: Education[];
  projects: Project[];
  certifications: Certification[];
}

export interface PersonalInfo {
  id: string;
  profile_id: string;
  full_name: string;
  email?: string;
  phone?: string;
  location?: string; // kept for backward compat — derived from city/state/country in API
  city?: string;
  state?: string;
  country?: string;
  linkedin_url?: string;
  portfolio_url?: string;
  github_url?: string;
  website_url?: string;
}

export interface Skill {
  id: string;
  name: string;
  category: string;
  proficiency: string;
  years_experience?: number;
  is_top_skill: boolean;
}

// Renamed from Experience to WorkExperience to match backend work_experiences field
export interface WorkExperience {
  id: string;
  company_name: string;
  job_title: string;
  title?: string;
  location?: string;
  start_date: string;
  end_date?: string;
  is_current: boolean;
  description?: string;
  achievements: string[];
  technologies: string[];
  skills_used?: string[];
}

// Keep Experience as an alias for backward compatibility
export type Experience = WorkExperience;

export interface Education {
  id: string;
  institution: string;
  degree?: string;
  field?: string;
  field_of_study?: string;
  start_date?: string;
  end_date?: string;
  is_current?: boolean;
  description?: string;
  gpa?: number;
  grade?: string;
  achievements: string[];
  activities?: string[];
}

export interface Project {
  id: string;
  name: string;
  description?: string;
  technologies: string[];
  url?: string;
  role?: string;
  start_date?: string;
  end_date?: string;
  is_current: boolean;
  highlights: string[];
}

export interface Certification {
  id: string;
  name: string;
  issuer?: string;
  issue_date?: string;
  expiry_date?: string;
  credential_id?: string;
  credential_url?: string;
}

export interface Job {
  id: number;
  title: string;
  company_name: string;
  company_url?: string;
  company_logo_url?: string;
  location: string;
  location_type: string;
  salary_min?: number;
  salary_max?: number;
  salary_currency: string;
  description: string;
  requirements?: string;
  required_skills: string[];
  preferred_skills: string[];
  experience_required?: string;
  employment_type: string;
  posted_date: string;
  source_url: string;
}

export interface Match {
  id: string;
  profile_id: string;
  job_id: number;
  match_score: number;
  skills_match: { matched: string[]; missing: string[]; extra: string[] };
  experience_match: { score: number; analysis: string };
  strength_areas: string[];
  gaps: string[];
  recommendation: string;
}

export interface Application {
  id: number;
  profile_id: string;
  job_id: number;
  status: string;
  company_name?: string;
  job_title?: string;
  job_location?: string;
  match_score?: number;
  resume_id?: number;
  cover_letter_id?: number;
  email_id?: number;
  delivery_status?: string;
  sent_at?: string;
  retry_count: number;
  notes?: string;
  created_at: string;
  updated_at: string;
  allowed_transitions: string[];
  progress_percentage: number;
  events?: ApplicationEvent[];
}

export interface ApplicationEvent {
  id: number;
  application_id: number;
  from_status?: string;
  to_status: string;
  event_type: string;
  description?: string;
  actor: string;
  created_at: string;
}

export interface Resume {
  id: string;
  profile_id: string;
  title: string;
  resume_type: string;
  target_role?: string;
  content: Record<string, unknown>;
  ats_score?: number;
  version: number;
  created_at: string;
  updated_at: string;
}

export interface ResumeTemplate {
  id: number;
  name: string;
  description?: string;
  is_default: boolean;
}

export interface OutreachContent {
  id: string;
  content_type: string;
  subject?: string;
  body: string;
  tone: string;
  status: string;
  version: number;
  company_name?: string;
  recipient_name?: string;
  created_at: string;
}

export interface User {
  id: string;
  email: string;
  role: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
}

export interface ApiResponse<T> {
  data: T;
  meta?: {
    page: number;
    per_page: number;
    total: number;
  };
  errors?: Array<{ code: string; field?: string; message: string }>;
}

export interface PaginatedResponse<T> {
  data: T[];
  meta: {
    page: number;
    per_page: number;
    total: number;
  };
}
