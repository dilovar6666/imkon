export type Role = "seeker" | "employer" | "admin";
export type VacancyStatus = "draft" | "pending" | "approved" | "rejected" | "published" | "closed" | "expired";
export type ApplicationStatus = "submitted" | "viewed" | "reviewing" | "chatting" | "offer" | "accepted" | "rejected";

export interface Profile { full_name: string | null; bio: string | null; desired_position: string | null; schedule_preference: string | null; contact_preference: string | null; work_conditions: string[]; skills: string[]; languages: string[]; portfolio_urls: string[]; }
export interface User { id: number; email: string; role: Role; is_email_verified: boolean; is_active: boolean; created_at: string; profile: Profile | null; }
export interface TokenPair { access_token: string; refresh_token: string; token_type: "bearer"; }
export interface Resume { id: number; user_id: number; title: string; summary: string | null; experience: Record<string, unknown>[]; skills: string[]; education: Record<string, unknown>[]; projects: Record<string, unknown>[]; languages: string[]; links: string[]; is_primary: boolean; is_visible_to_employers: boolean; updated_at: string; }
export interface Vacancy { id: number; employer_id: number; title: string; description: string; requirements: string | null; responsibilities: string | null; skills: string[]; experience_level: string | null; schedule: string | null; salary_min: number | null; salary_max: number | null; currency: string | null; salary_negotiable: boolean; work_conditions: string[]; work_language: string | null; expires_at: string; status: VacancyStatus; is_demo: boolean; rejection_reason: string | null; created_at: string; updated_at: string; }
export interface JobApplication { id: number; vacancy_id: number; user_id: number; resume_id: number; cover_letter: string | null; status: ApplicationStatus; created_at: string; }
export interface EmployerApplication { id: number; user_id: number; kind: "company" | "individual"; name: string; description: string; country: string; contact: string; website: string | null; status: "pending" | "under_review" | "approved" | "rejected"; review_reason: string | null; created_at: string; }
export interface ApiError extends Error { status?: number; detail?: string; }
