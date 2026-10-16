import { FormEvent, useEffect, useState } from "react";
import { Link, Navigate, useNavigate, useSearchParams } from "react-router-dom";
import { api } from "./lib/api";
import { useAuth } from "./state";
import type { EmployerApplication, JobApplication, Resume, User, Vacancy } from "./types";
import { Button, Empty, Loading, Notice, PageLead, Status } from "./components";

const errorText = (error: unknown) => error instanceof Error ? error.message : "Ошибка запроса";
function Protected({ children, role }: { children: React.ReactNode; role?: User["role"] }) { const { user, ready } = useAuth(); if (!ready) return <Loading />; if (!user) return <Navigate to="/login" replace />; if (role && user.role !== role) return <Navigate to="/dashboard" replace />; return <>{children}</>; }
export function Verify() { const { verify } = useAuth(); const [query] = useSearchParams(); const navigate = useNavigate(); const [error, setError] = useState(""); const submit = async (event: FormEvent<HTMLFormElement>) => { event.preventDefault(); try { await verify(query.get("email") ?? "", String(new FormData(event.currentTarget).get("code"))); navigate("/dashboard"); } catch (error) { setError(errorText(error)); } }; return <main className="verify"><PageLead eyebrow="Email verification" title="Один короткий шаг."><p>Введите шестизначный код из письма. В development Backend может показать его в ответе регистрации.</p></PageLead><form className="form card-form" onSubmit={submit}><label>Код<input name="code" required pattern="[0-9]{6}" inputMode="numeric" maxLength={6} /></label>{error && <p className="form-error">{error}</p>}<Button>Подтвердить email</Button></form></main>; }

export function Dashboard() { return <Protected><DashboardContent /></Protected>; }
function DashboardContent() { const { user, refreshUser } = useAuth(); const [applications, setApplications] = useState<JobApplication[]>([]); const [resume, setResume] = useState<Resume | null>(null); const [loading, setLoading] = useState(true); useEffect(() => { Promise.all([api.applications(), api.resume().catch(() => null)]).then(([apps, savedResume]) => { setApplications(apps); setResume(savedResume); }).finally(() => setLoading(false)); }, []); if (!user) return null; return <main className="workspace"><PageLead eyebrow="Личный кабинет" title={<>Здравствуйте{user.profile?.full_name ? `, ${user.profile.full_name.split(" ")[0]}` : ""}.</>}><p>Управляйте профилем, резюме и статусами откликов в одном месте.</p></PageLead><div className="workspace-grid"><section className="panel profile-panel"><h2>Профиль</h2><ProfileForm onSaved={() => void refreshUser()} user={user} /></section><section className="panel"><h2>Основное резюме</h2>{loading ? <Loading /> : <ResumeEditor current={resume} onSaved={setResume} />}</section></div><section className="panel apps"><div className="panel-head"><h2>Мои отклики</h2><Status>{applications.length}</Status></div>{loading ? <Loading /> : applications.length ? <ul>{applications.map(app => <li key={app.id}><b>Вакансия #{app.vacancy_id}</b><span>{app.status}</span><time>{new Date(app.created_at).toLocaleDateString("ru")}</time></li>)}</ul> : <Empty title="Откликов пока нет">Перейдите в каталог, чтобы найти проверенную вакансию.</Empty>}</section></main>; }
function ProfileForm({ user, onSaved }: { user: User; onSaved: () => void }) { const [message, setMessage] = useState(""); return <form className="form compact-form" onSubmit={async event => { event.preventDefault(); const data = new FormData(event.currentTarget); try { await api.updateProfile({ full_name: String(data.get("full_name")), desired_position: String(data.get("desired_position")), bio: String(data.get("bio")) }); setMessage("Профиль сохранён"); onSaved(); } catch (error) { setMessage(errorText(error)); } }}><label>Имя<input name="full_name" defaultValue={user.profile?.full_name ?? ""} /></label><label>Желаемая должность<input name="desired_position" defaultValue={user.profile?.desired_position ?? ""} /></label><label>О себе<textarea name="bio" defaultValue={user.profile?.bio ?? ""} /></label>{message && <p className="form-message">{message}</p>}<Button>Сохранить профиль</Button></form>; }
function ResumeEditor({ current, onSaved }: { current: Resume | null; onSaved: (resume: Resume) => void }) {
  const [message, setMessage] = useState("");
  const [draft, setDraft] = useState({ title: current?.title ?? "", summary: current?.summary ?? "", skills: current?.skills.join(", ") ?? "", languages: current?.languages.join(", ") ?? "" });
  return <div className="resume-workbench"><form className="form compact-form" onSubmit={async event => {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    const payload = {
      title: String(data.get("title")),
      summary: String(data.get("summary")) || null,
      skills: String(data.get("skills")).split(",").map(skill => skill.trim()).filter(Boolean),
      languages: String(data.get("languages")).split(",").map(language => language.trim()).filter(Boolean),
      experience: current?.experience ?? [],
      education: current?.education ?? [],
      projects: current?.projects ?? [],
      links: current?.links ?? [],
      is_visible_to_employers: Boolean(data.get("visible")),
    };
    try {
      const result = current ? await api.updateResume(payload) : await api.createResume(payload);
      onSaved(result);
      setMessage("Резюме сохранено");
    } catch (error) { setMessage(errorText(error)); }
  }}><label>Желаемая должность<input name="title" required value={draft.title} onChange={event => setDraft({ ...draft, title: event.target.value })} /></label><label>Краткое описание<textarea name="summary" value={draft.summary} onChange={event => setDraft({ ...draft, summary: event.target.value })} /></label><label>Навыки через запятую<input name="skills" value={draft.skills} onChange={event => setDraft({ ...draft, skills: event.target.value })} /></label><label>Языки через запятую<input name="languages" value={draft.languages} onChange={event => setDraft({ ...draft, languages: event.target.value })} /></label><label className="check"><input type="checkbox" name="visible" defaultChecked={current?.is_visible_to_employers ?? true} /> Разрешить просмотр подтверждённым работодателям</label>{message && <p className="form-message" role="status">{message}</p>}<Button>{current ? "Сохранить изменения" : "Создать резюме"}</Button></form><article className="resume-preview" aria-label="Предпросмотр резюме"><p className="eyebrow">Предпросмотр / основное резюме</p><h3>{draft.title || "Ваша будущая должность"}</h3><p>{draft.summary || "Добавьте краткое описание профессиональных целей."}</p><h4>Навыки</h4><div className="resume-preview-tags">{draft.skills.split(",").map(skill => skill.trim()).filter(Boolean).map(skill => <span key={skill}>{skill}</span>)}</div><h4>Языки</h4><p>{draft.languages || "Не указаны"}</p><small>Изменения появятся в основном резюме после сохранения.</small></article></div>;
}

export function Employer() { return <Protected><EmployerContent /></Protected>; }
function EmployerContent() { const { user } = useAuth(); const [application, setApplication] = useState<EmployerApplication | null>(null); const [loading, setLoading] = useState(true); useEffect(() => { api.employerApplication().then(setApplication).catch(() => setApplication(null)).finally(() => setLoading(false)); }, []); if (!user) return null; if (user.role !== "employer") return <main className="workspace"><PageLead eyebrow="Работодатель" title="Разместите работу ответственно."><p>Статус работодателя присваивается только после проверки заявки администратором.</p></PageLead>{loading ? <Loading /> : application ? <section className="panel"><Status>{application.status}</Status><h2>{application.name}</h2><p>{application.review_reason ?? "Заявка принята и ожидает решения."}</p></section> : <EmployerApplicationForm onCreated={setApplication} />}</main>; return <main className="workspace employer"><PageLead eyebrow="Работодатель / verified" title={<>Создайте<br /><em>возможность.</em></>}><p>Каждая новая вакансия начинает путь как черновик и публикуется только после модерации.</p></PageLead><div className="workspace-grid"><section className="panel"><h2>Создать вакансию</h2><VacancyForm /></section><section className="panel muted-panel"><p className="eyebrow">Прозрачный процесс</p><h2>Путь вакансии</h2><ol className="vacancy-journey"><li><strong>Черновик</strong><span>Заполните условия постоянной удалённой работы.</span></li><li><strong>Проверка</strong><span>Отправьте вакансию администратору на модерацию.</span></li><li><strong>Публикация</strong><span>После одобрения вакансия появится в каталоге.</span></li></ol><Notice title="Кандидаты и Kanban пока недоступны">Backend ещё не возвращает список ваших вакансий и данные кандидатов для доски. Здесь нет фиктивных откликов.</Notice></section></div></main>; }
function EmployerApplicationForm({ onCreated }: { onCreated: (value: EmployerApplication) => void }) { const [message, setMessage] = useState(""); return <section className="panel employer-request"><h2>Заявка работодателя</h2><form className="form" onSubmit={async event => { event.preventDefault(); const data = new FormData(event.currentTarget); try { const result = await api.createEmployerApplication({ kind: String(data.get("kind")) as "company" | "individual", name: String(data.get("name")), description: String(data.get("description")), country: String(data.get("country")), contact: String(data.get("contact")), website: String(data.get("website")) || null }); onCreated(result); } catch (error) { setMessage(errorText(error)); } }}><label>Тип<select name="kind"><option value="company">Компания</option><option value="individual">Частный работодатель</option></select></label><label>Название / имя<input name="name" required /></label><label>Описание деятельности<textarea name="description" minLength={20} required /></label><label>Страна<input name="country" defaultValue="Tajikistan" required /></label><label>Контакт<input name="contact" required /></label><label>Сайт <small>Необязательно</small><input type="url" name="website" /></label>{message && <p className="form-error">{message}</p>}<Button>Отправить на проверку</Button></form></section>; }
function VacancyForm() {
  const [message, setMessage] = useState("");
  const [created, setCreated] = useState<Vacancy | null>(null);
  const [busy, setBusy] = useState(false);
  const submit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (busy || created) return;
    const data = new FormData(event.currentTarget);
    const expires = new Date();
    expires.setDate(expires.getDate() + Number(data.get("days")));
    setBusy(true);
    setMessage("");
    try {
      const vacancy = await api.createVacancy({ title: String(data.get("title")), description: String(data.get("description")), requirements: String(data.get("requirements")) || null, responsibilities: null, skills: String(data.get("skills")).split(",").map(skill => skill.trim()).filter(Boolean), experience_level: null, schedule: String(data.get("schedule")) || null, salary_min: Number(data.get("salary_min")) || null, salary_max: Number(data.get("salary_max")) || null, currency: String(data.get("currency")) || null, salary_negotiable: Boolean(data.get("negotiable")), work_conditions: [], work_language: null, expires_at: expires.toISOString() });
      setCreated(vacancy);
      setMessage("Черновик создан. Отправьте его на модерацию.");
    } catch (reason) { setMessage(errorText(reason)); }
    finally { setBusy(false); }
  };
  return <form className="form compact-form" onSubmit={submit}><label>Название<input name="title" required /></label><label>Описание<textarea name="description" minLength={20} required /></label><label>Требования<textarea name="requirements" /></label><label>Навыки<input name="skills" /></label><div className="form-row"><label>От<input type="number" min="0" name="salary_min" /></label><label>До<input type="number" min="0" name="salary_max" /></label><label>Валюта<select name="currency"><option value="">—</option><option>USD</option><option>TJS</option></select></label></div><label>График<select name="schedule"><option value="">Не указан</option><option value="full-time">Full-time</option><option value="part-time">Part-time</option></select></label><label>Срок публикации<select name="days"><option value="30">30 дней</option><option value="60">60 дней</option></select></label>{message && <p className="form-message" role="status">{message}</p>}<Button disabled={busy || Boolean(created)}>Создать черновик</Button>{created?.status === "draft" && <Button type="button" className="ghost" disabled={busy} onClick={async () => { setBusy(true); try { setCreated(await api.submitVacancy(created.id)); setMessage("Вакансия отправлена на модерацию."); } catch (reason) { setMessage(errorText(reason)); } finally { setBusy(false); } }}>Отправить на модерацию</Button>}{created?.status === "pending" && <Button type="button" className="ghost" onClick={event => { setCreated(null); setMessage(""); event.currentTarget.form?.reset(); }}>Создать другую вакансию</Button>}</form>;
}

export function Admin() { return <Protected role="admin"><AdminContent /></Protected>; }
function AdminContent() {
  const [users, setUsers] = useState<User[]>([]);
  const [applications, setApplications] = useState<EmployerApplication[]>([]);
  const [vacancies, setVacancies] = useState<Vacancy[]>([]);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const load = async () => {
    setLoading(true);
    try {
      const [people, requests, jobs] = await Promise.all([api.adminUsers(), api.adminEmployerApplications(), api.pendingVacancies()]);
      setUsers(people);
      setApplications(requests);
      setVacancies(jobs);
    } catch (reason) { setError(errorText(reason)); }
    finally { setLoading(false); }
  };
  useEffect(() => { void load(); }, []);
  const act = async (task: () => Promise<unknown>) => {
    setBusy(true);
    setError("");
    try { await task(); await load(); return true; }
    catch (reason) { setError(errorText(reason)); return false; }
    finally { setBusy(false); }
  };
  return <main className="admin"><PageLead eyebrow="IMKON / Администрирование" title={<>Очередь<br /><em>решений.</em></>}><p>Проверяйте заявки и вакансии перед публикацией. Решение всегда принимает администратор.</p></PageLead><nav className="admin-jumps" aria-label="Разделы администрирования"><a href="#employer-review">Работодатели <Status>{applications.filter(item => item.status === "pending").length}</Status></a><a href="#vacancy-review">Вакансии <Status>{vacancies.length}</Status></a><a href="#user-review">Пользователи <Status>{users.length}</Status></a></nav>{error && <p className="form-error" role="alert">{error}</p>}{loading ? <Loading /> : <>
    <section id="employer-review" className="panel admin-section"><h2>Заявки работодателей</h2>{applications.length ? <div className="admin-records">{applications.map(item => <article className="admin-record" key={item.id}><div className="admin-record-head"><div><p className="eyebrow">{item.kind === "company" ? "Компания" : "Частное лицо"} · {item.country}</p><h3>{item.name}</h3></div><Status>{item.status}</Status></div><p>{item.description}</p><p className="admin-meta">Контакт: {item.contact}{item.website ? ` · ${item.website}` : ""}</p>{item.review_reason && <p className="form-error">Причина: {item.review_reason}</p>}{(item.status === "pending" || item.status === "under_review") && <div className="admin-actions"><Button disabled={busy} onClick={() => { if (window.confirm(`Одобрить работодателя «${item.name}»?`)) void act(() => api.approveEmployer(item.id)); }}>Одобрить</Button><RejectForm disabled={busy} label="Отклонить заявку" onReject={reason => act(() => api.rejectEmployer(item.id, reason))} /></div>}</article>)}</div> : <Empty title="Нет заявок">Новые заявки появятся здесь.</Empty>}</section>
    <section id="vacancy-review" className="panel admin-section"><h2>Вакансии на модерации</h2>{vacancies.length ? <div className="admin-records">{vacancies.map(item => <article className="admin-record" key={item.id}><div className="admin-record-head"><div><p className="eyebrow">Вакансия #{item.id} · {item.expires_at.slice(0, 10)}</p><h3>{item.title}</h3></div><Status>pending</Status></div><p>{item.description}</p>{item.requirements && <p><strong>Требования:</strong> {item.requirements}</p>}<p className="admin-meta">{item.salary_min ?? "—"}–{item.salary_max ?? "—"} {item.currency ?? ""} · {item.schedule ?? "График не указан"}{item.is_demo ? " · Демонстрационная" : ""}</p><div className="admin-actions"><Button disabled={busy} onClick={() => { if (window.confirm(`Опубликовать вакансию «${item.title}»?`)) void act(() => api.approveVacancy(item.id)); }}>Опубликовать</Button><RejectForm disabled={busy} label="Отклонить вакансию" onReject={reason => act(() => api.rejectVacancy(item.id, reason))} /></div></article>)}</div> : <Empty title="Нет вакансий на модерации">Новые заявки появятся здесь.</Empty>}</section>
    <section id="user-review" className="panel admin-section"><h2>Пользователи</h2><div className="admin-records">{users.map(person => <article className="admin-record admin-user" key={person.id}><div><strong>{person.email}</strong><p className="admin-meta">{person.role} · {person.is_active ? "Активен" : "Заблокирован"}</p></div>{person.role !== "admin" && <Button className="ghost" disabled={busy} onClick={() => { if (window.confirm(`${person.is_active ? "Заблокировать" : "Разблокировать"} ${person.email}?`)) void act(() => person.is_active ? api.blockUser(person.id) : api.unblockUser(person.id)); }}>{person.is_active ? "Заблокировать" : "Разблокировать"}</Button>}</article>)}</div></section>
  </>}</main>;
}

function RejectForm({ disabled, label, onReject }: { disabled: boolean; label: string; onReject: (reason: string) => Promise<boolean> }) {
  const [open, setOpen] = useState(false);
  return open ? <form className="reject-form" onSubmit={event => {
    event.preventDefault();
    const reason = String(new FormData(event.currentTarget).get("reason") ?? "").trim();
    if (reason) void onReject(reason).then(success => { if (success) setOpen(false); });
  }}><label>Причина отклонения<textarea name="reason" required minLength={3} /></label><div><Button disabled={disabled}>{label}</Button><Button type="button" className="ghost" onClick={() => setOpen(false)}>Отмена</Button></div></form> : <Button type="button" className="ghost" disabled={disabled} onClick={() => setOpen(true)}>{label}</Button>;
}
