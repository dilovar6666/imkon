import type { ApiError, EmployerApplication, JobApplication, Resume, TokenPair, User, Vacancy } from "../types";

const baseUrl = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000/api/v1";
let accessToken = sessionStorage.getItem("imkon.access") ?? "";
let refreshToken = "";
export const tokenStore = { set(tokens: TokenPair) { accessToken = tokens.access_token; refreshToken = tokens.refresh_token; sessionStorage.setItem("imkon.access", accessToken); }, clear() { accessToken = ""; refreshToken = ""; sessionStorage.removeItem("imkon.access"); }, hasAccess: () => Boolean(accessToken) };

async function request<T>(path: string, init: RequestInit = {}, retry = true): Promise<T> {
  const headers = new Headers(init.headers);
  if (init.body) headers.set("Content-Type", "application/json");
  if (accessToken) headers.set("Authorization", `Bearer ${accessToken}`);
  let response: Response;
  try { response = await fetch(`${baseUrl}${path}`, { ...init, headers }); } catch { const error = new Error("Не удалось связаться с сервером") as ApiError; error.status = 0; throw error; }
  if (response.status === 401 && retry && refreshToken) { try { const tokens = await request<TokenPair>("/auth/refresh", { method: "POST", body: JSON.stringify({ refresh_token: refreshToken }) }, false); tokenStore.set(tokens); return request<T>(path, init, false); } catch { tokenStore.clear(); } }
  if (!response.ok) { const body = await response.json().catch(() => ({})); const detail = typeof body.detail === "string" ? body.detail : response.status === 422 ? "Проверьте заполненные поля" : "Запрос не выполнен"; const error = new Error(detail) as ApiError; error.status = response.status; error.detail = body.detail; throw error; }
  return response.json() as Promise<T>;
}

export const api = {
  register: (email: string, password: string) => request<{ detail: string }>("/auth/register", { method: "POST", body: JSON.stringify({ email, password }) }),
  verify: (email: string, code: string) => request<TokenPair>("/auth/verify-email", { method: "POST", body: JSON.stringify({ email, code }) }),
  login: (email: string, password: string) => request<TokenPair>("/auth/login", { method: "POST", body: JSON.stringify({ email, password }) }),
  googleLogin: (idToken: string) => request<TokenPair>("/auth/google", { method: "POST", body: JSON.stringify({ id_token: idToken }) }),
  logout: () => request<{ detail: string }>("/auth/logout", { method: "POST", body: JSON.stringify({ refresh_token: refreshToken }) }),
  me: () => request<User>("/users/me"),
  updateProfile: (data: Partial<User["profile"]>) => request<User>("/users/me/profile", { method: "PATCH", body: JSON.stringify(data) }),
  resume: () => request<Resume>("/resumes/me"),
  createResume: (data: Omit<Resume, "id" | "user_id" | "is_primary" | "updated_at">) => request<Resume>("/resumes", { method: "POST", body: JSON.stringify(data) }),
  updateResume: (data: Omit<Resume, "id" | "user_id" | "is_primary" | "updated_at">) => request<Resume>("/resumes/me", { method: "PATCH", body: JSON.stringify(data) }),
  vacancies: (params = new URLSearchParams()) => request<Vacancy[]>(`/vacancies?${params.toString()}`),
  vacancy: (id: number) => request<Vacancy>(`/vacancies/${id}`),
  createVacancy: (data: Omit<Vacancy, "id" | "employer_id" | "status" | "is_demo" | "rejection_reason" | "created_at" | "updated_at">) => request<Vacancy>("/vacancies", { method: "POST", body: JSON.stringify(data) }),
  submitVacancy: (id: number) => request<Vacancy>(`/vacancies/${id}/submit`, { method: "POST" }),
  applications: () => request<JobApplication[]>("/applications/me"),
  apply: (vacancyId: number, resumeId: number, coverLetter: string) => request<JobApplication>(`/applications/vacancies/${vacancyId}`, { method: "POST", body: JSON.stringify({ resume_id: resumeId, cover_letter: coverLetter || null }) }),
  employerApplication: () => request<EmployerApplication>("/employer-applications/me"),
  createEmployerApplication: (data: Omit<EmployerApplication, "id" | "user_id" | "status" | "review_reason" | "created_at">) => request<EmployerApplication>("/employer-applications", { method: "POST", body: JSON.stringify(data) }),
  adminUsers: () => request<User[]>("/admin/users"),
  blockUser: (id: number) => request<{ detail: string }>(`/admin/users/${id}/block`, { method: "PATCH" }),
  unblockUser: (id: number) => request<{ detail: string }>(`/admin/users/${id}/unblock`, { method: "PATCH" }),
  adminEmployerApplications: () => request<EmployerApplication[]>("/admin/employer-applications"),
  approveEmployer: (id: number) => request<EmployerApplication>(`/admin/employer-applications/${id}/approve`, { method: "POST" }),
  rejectEmployer: (id: number, reason: string) => request<EmployerApplication>(`/admin/employer-applications/${id}/reject?reason=${encodeURIComponent(reason)}`, { method: "POST" }),
  pendingVacancies: () => request<Vacancy[]>("/admin/vacancies/pending"),
  approveVacancy: (id: number) => request<Vacancy>(`/admin/vacancies/${id}/approve`, { method: "POST" }),
  rejectVacancy: (id: number, reason: string) => request<Vacancy>(`/admin/vacancies/${id}/reject?reason=${encodeURIComponent(reason)}`, { method: "POST" }),
};
