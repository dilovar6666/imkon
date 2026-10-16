import { BriefcaseBusiness, CircleHelp, Clock3, FileText, GraduationCap, Layers3, MapPin, Search, Send, ShieldCheck, Sparkles, UserRound } from "lucide-react";
import { FormEvent, useEffect, useState } from "react";
import { Link, Navigate, useNavigate, useParams, useSearchParams } from "react-router-dom";
import { api } from "./lib/api";
import { useAuth } from "./state";
import type { EmployerApplication, JobApplication, Resume, Vacancy } from "./types";
import { ArrowLink, Button, Empty, Loading, Notice, PageLead, Status } from "./components";

const errorText = (error: unknown) => error instanceof Error ? error.message : "Что-то пошло не так";
const salary = (item: Vacancy) => item.salary_negotiable ? "По договорённости" : item.salary_min || item.salary_max ? `${item.salary_min ?? ""}${item.salary_max ? `–${item.salary_max}` : ""} ${item.currency ?? ""}` : "Не указана";

function HomeSearch() { const navigate = useNavigate(); return <form className="quick-search" role="search" onSubmit={event => { event.preventDefault(); const query = String(new FormData(event.currentTarget).get("query") ?? "").trim(); navigate(query ? `/vacancies?query=${encodeURIComponent(query)}` : "/vacancies"); }}><label htmlFor="home-search">Начните с должности или навыка</label><div className="quick-search-field"><Search size={21} aria-hidden="true" /><input id="home-search" name="query" placeholder="Например, Python Developer" /><Button>Искать вакансии</Button></div><p>Только опубликованные вакансии после модерации.</p></form>; }

export function Home() { const [jobs, setJobs] = useState<Vacancy[]>([]); const [loading, setLoading] = useState(true); useEffect(() => { api.vacancies(new URLSearchParams({ limit: "3" })).then(setJobs).catch(() => setJobs([])).finally(() => setLoading(false)); }, []); return <>
  <section className="hero"><div className="hero-intro"><p className="eyebrow">IMKON / ПЛАТФОРМА ВОЗМОЖНОСТЕЙ</p><span>01 — Открытый путь</span></div><div className="hero-grid"><div className="hero-statement"><h1>Возможности<br /><em>для каждого.</em></h1><p>Постоянная удалённая работа — без платных барьеров и лишних ярлыков.</p><div className="hero-actions"><Link className="button light" to="/vacancies">Найти работу <Search size={17} /></Link><Link className="button ghost" to="/learn">Обучение — скоро</Link></div></div><div className="hero-side"><svg className="hero-path" viewBox="0 0 320 220" fill="none" aria-hidden="true"><path d="M21 177C71 177 71 46 150 46S198 177 296 177" stroke="currentColor" strokeWidth="2" strokeDasharray="4 9"/><circle cx="21" cy="177" r="8" fill="currentColor"/><circle cx="150" cy="46" r="8" fill="currentColor"/><circle cx="296" cy="177" r="8" fill="currentColor"/></svg><p>IMKON соединяет навыки людей с проверенными удалёнными возможностями. Ваш следующий шаг начинается здесь.</p><ol><li>Профиль и резюме</li><li>Проверенные вакансии</li><li>Прямой отклик работодателю</li></ol></div></div><div className="hero-bottom"><span>Бесплатно для соискателей и работодателей</span><span>Таджикистан · открыто для всех</span></div></section>
  <HomeSearch />
  <section className="section jobs-home"><div className="section-head"><div><p className="eyebrow">02 / Work</p><h2>Актуальные<br /><em>возможности</em></h2></div><ArrowLink to="/vacancies">Все вакансии</ArrowLink></div>{loading ? <Loading /> : jobs.length ? <div className="job-grid">{jobs.map(job => <JobCard key={job.id} item={job} />)}</div> : <Empty title="Пока нет опубликованных вакансий">Каталог обновится, когда работодатели пройдут модерацию.</Empty>}</section>
  <section className="section impact"><div><p className="eyebrow">03 / The way forward</p><h2>Не «особый»<br />путь.<br /><em>Свой путь.</em></h2></div><ol><li><b>01</b><span>Создайте профиль и резюме — расскажите о своих навыках, а не о диагнозах.</span></li><li><b>02</b><span>Находите проверенные вакансии и откликайтесь с выбранным резюме.</span></li><li><b>03</b><span>Учитесь бесплатно и расширяйте карьерные возможности.</span></li></ol></section>
  <section className="section employer-cta"><div><p className="eyebrow">Для работодателей</p><h2>Найдите людей,<br /><em>готовых работать.</em></h2></div><div><p>Публикуйте вакансии бесплатно. Перед размещением потребуется короткая заявка и проверка — это помогает беречь доверие сообщества.</p><Link className="button light" to="/employer">Подать заявку <Send size={16} /></Link></div></section>
  <section className="section future-grid"><div><GraduationCap /><h3>Бесплатное обучение</h3><p>Курсы и сертификаты появятся после запуска образовательного API.</p><Link to="/learn">Смотреть статус →</Link></div><div><Sparkles /><h3>AI-помощник</h3><p>Будет помогать в поиске и подготовке, но не принимает решений о найме.</p><Link to="/ai">Смотреть статус →</Link></div><div><ShieldCheck /><h3>Безопасная среда</h3><p>Каждая новая вакансия проходит модерацию до публикации.</p><Link to="/opportunity">О миссии →</Link></div></section>
 </>; }

export function JobCard({ item }: { item: Vacancy }) { return <article className="job-card"><div className="job-top"><Status>{item.is_demo ? "Демонстрационная" : "Проверенная вакансия"}</Status><span>{item.work_language ?? "Удалённо"}</span></div><h3>{item.title}</h3><p className="salary">{salary(item)}</p><div className="tags">{item.skills.slice(0, 3).map(skill => <span key={skill}>{skill}</span>)}</div><div className="job-foot"><span>{item.schedule ?? "График не указан"}</span><Link to={`/vacancies/${item.id}`} aria-label={`Открыть ${item.title}`}>Подробнее <span aria-hidden="true">↗</span></Link></div></article>; }

export function Vacancies() {
  const [params, setParams] = useSearchParams();
  const [jobs, setJobs] = useState<Vacancy[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const query = params.get("query") ?? "";
  const skip = Number(params.get("skip") ?? 0);
  const pageSize = 9;
  const update = (key: string, value: string) => {
    const next = new URLSearchParams(params);
    value ? next.set(key, value) : next.delete(key);
    next.delete("skip");
    setParams(next);
  };
  useEffect(() => {
    let active = true;
    setLoading(true);
    setError("");
    const search = new URLSearchParams(params);
    search.set("limit", String(pageSize));
    api.vacancies(search).then(result => { if (active) setJobs(result); }).catch(reason => { if (active) setError(errorText(reason)); }).finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [params]);
  const submit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    update("query", String(new FormData(event.currentTarget).get("query") ?? "").trim());
  };
  const changePage = (nextSkip: number) => {
    const next = new URLSearchParams(params);
    nextSkip ? next.set("skip", String(nextSkip)) : next.delete("skip");
    setParams(next);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };
  return <main className="catalog"><PageLead eyebrow="01 / Work catalogue" title={<>Удалённая работа<br /><em>без лишних барьеров.</em></>}><p>В каталоге показываются только опубликованные и неистёкшие вакансии.</p></PageLead><form className="catalog-search" onSubmit={submit}><Search /><input key={query} name="query" defaultValue={query} aria-label="Поиск вакансий" placeholder="Должность, навык или ключевое слово" /><Button>Найти</Button></form><div className="filters"><label>Валюта<select value={params.get("currency") ?? ""} onChange={event => update("currency", event.target.value)}><option value="">Любая</option><option>USD</option><option>TJS</option></select></label><label>График<select value={params.get("schedule") ?? ""} onChange={event => update("schedule", event.target.value)}><option value="">Любой</option><option value="full-time">Full-time</option><option value="part-time">Part-time</option></select></label><label>Опыт<select value={params.get("experience_level") ?? ""} onChange={event => update("experience_level", event.target.value)}><option value="">Любой</option><option value="junior">Начальный</option><option value="middle">Средний</option><option value="senior">Опытный</option></select></label><label>Зарплата от<input type="number" min="0" key={params.get("salary_min") ?? ""} defaultValue={params.get("salary_min") ?? ""} onBlur={event => update("salary_min", event.target.value)} /></label><button type="button" className="text-button" onClick={() => setParams({})}>Сбросить</button></div>{error ? <Notice title="Не удалось загрузить вакансии">{error}</Notice> : loading ? <Loading /> : jobs.length ? <><div className="job-grid catalog-grid">{jobs.map(job => <JobCard key={job.id} item={job} />)}</div><nav className="pagination" aria-label="Страницы вакансий"><Button type="button" className="ghost" disabled={skip === 0} onClick={() => changePage(Math.max(0, skip - pageSize))}>Назад</Button><span>Страница {Math.floor(skip / pageSize) + 1}</span><Button type="button" className="ghost" disabled={jobs.length < pageSize} onClick={() => changePage(skip + pageSize)}>Далее</Button></nav></> : <Empty title="Ничего не найдено">Попробуйте изменить запрос или сбросить фильтры.</Empty>}<Notice title="AI-поиск в разработке">Поиск естественным языком появится после подключения безопасного AI API.</Notice></main>;
}

export function VacancyDetail() {
  const { id } = useParams();
  const { user, ready } = useAuth();
  const [vacancy, setVacancy] = useState<Vacancy | null>(null);
  const [resume, setResume] = useState<Resume | null>(null);
  const [application, setApplication] = useState<JobApplication | null>(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  useEffect(() => {
    let active = true;
    setLoading(true);
    setError("");
    api.vacancy(Number(id)).then(result => { if (active) setVacancy(result); }).catch(reason => { if (active) setError(errorText(reason)); }).finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [id]);
  useEffect(() => {
    if (!user || user.role !== "seeker") return;
    let active = true;
    Promise.all([api.resume().catch(() => null), api.applications()]).then(([savedResume, applications]) => {
      if (active) { setResume(savedResume); setApplication(applications.find(item => item.vacancy_id === Number(id)) ?? null); }
    }).catch(reason => { if (active) setError(errorText(reason)); });
    return () => { active = false; };
  }, [user?.id, id]);
  const apply = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!resume || busy) return;
    setBusy(true);
    setError("");
    try {
      const coverLetter = String(new FormData(event.currentTarget).get("cover_letter") ?? "");
      setApplication(await api.apply(Number(id), resume.id, coverLetter));
    } catch (reason) { setError(errorText(reason)); }
    finally { setBusy(false); }
  };
  if (loading || !ready) return <main className="detail"><Loading /></main>;
  if (!vacancy) return <main className="detail"><PageLead eyebrow="Vacancy" title="Вакансия недоступна."><p>{error || "Вакансия закрыта или ещё не прошла модерацию."}</p></PageLead><Link className="button" to="/vacancies">Вернуться в каталог</Link></main>;
  return <main className="detail"><div className="detail-back"><ArrowLink to="/vacancies">Все вакансии</ArrowLink></div><PageLead eyebrow="01 / Verified opportunity" title={vacancy.title}><p>Подтверждённый работодатель · постоянная удалённая работа</p></PageLead><div className="detail-layout"><article className="detail-content"><div className="detail-facts"><div><span>Зарплата</span><strong>{salary(vacancy)}</strong></div><div><span>График</span><strong>{vacancy.schedule ?? "Не указан"}</strong></div><div><span>Опыт</span><strong>{vacancy.experience_level ?? "Не указан"}</strong></div><div><span>Действует до</span><strong>{new Date(vacancy.expires_at).toLocaleDateString("ru")}</strong></div></div>{vacancy.is_demo && <Notice title="Демонстрационная вакансия">Эта запись создана для проверки платформы и не является реальным предложением о работе.</Notice>}<section><h2>О работе</h2><p>{vacancy.description}</p></section>{vacancy.requirements && <section><h2>Требования</h2><p>{vacancy.requirements}</p></section>}{vacancy.responsibilities && <section><h2>Обязанности</h2><p>{vacancy.responsibilities}</p></section>}{vacancy.skills.length > 0 && <section><h2>Навыки</h2><div className="tags">{vacancy.skills.map(skill => <span key={skill}>{skill}</span>)}</div></section>}{vacancy.work_conditions.length > 0 && <section><h2>Условия работы</h2><ul>{vacancy.work_conditions.map(condition => <li key={condition}>{condition}</li>)}</ul></section>}</article><aside className="detail-apply"><p className="eyebrow">Ваш следующий шаг</p><h2>Откликнуться</h2>{!user ? <><p>Войдите, чтобы отправить отклик с вашим резюме.</p><Link className="button" to={`/login?next=${encodeURIComponent(`/vacancies/${id}`)}`}>Войти и откликнуться</Link></> : user.role !== "seeker" ? <p>Отклик доступен аккаунту соискателя.</p> : application ? <Notice title="Отклик отправлен">Текущий статус: {application.status}. Повторная отправка недоступна.</Notice> : !resume ? <><p>Для отклика сначала создайте основное резюме.</p><Link className="button" to="/dashboard">Создать резюме</Link></> : <form className="form" onSubmit={apply}><p>Будет приложено резюме: <strong>{resume.title}</strong></p><label>Сопроводительное сообщение <small>Необязательно</small><textarea name="cover_letter" maxLength={5000} /></label>{error && <p className="form-error" role="alert">{error}</p>}<Button disabled={busy}>{busy ? "Отправляем…" : "Отправить отклик"}</Button></form>}</aside></div></main>;
}

export function Login() { const { signIn } = useAuth(); const navigate = useNavigate(); const [params] = useSearchParams(); const [error, setError] = useState(""); const [busy, setBusy] = useState(false); const submit = async (event: FormEvent<HTMLFormElement>) => { event.preventDefault(); setBusy(true); setError(""); const form = new FormData(event.currentTarget); try { await signIn(String(form.get("email")), String(form.get("password"))); const next = params.get("next"); navigate(next?.startsWith("/") && !next.startsWith("//") ? next : "/dashboard"); } catch (error) { setError(errorText(error)); } finally { setBusy(false); } }; return <AuthShell title="С возвращением."><form onSubmit={submit} className="form"><label>Email<input required type="email" name="email" autoComplete="email" /></label><label>Пароль<input required minLength={12} type="password" name="password" autoComplete="current-password" /></label>{error && <p className="form-error" role="alert">{error}</p>}<Button disabled={busy}>{busy ? "Входим…" : "Войти"}</Button><p>Нет аккаунта? <Link to="/register">Создать бесплатно</Link></p></form></AuthShell>; }

export function Register() { const [email, setEmail] = useState(""); const [error, setError] = useState(""); const [message, setMessage] = useState(""); const submit = async (event: FormEvent<HTMLFormElement>) => { event.preventDefault(); const form = new FormData(event.currentTarget); setError(""); try { const response = await api.register(String(form.get("email")), String(form.get("password"))); setEmail(String(form.get("email"))); setMessage(response.detail); } catch (error) { setError(errorText(error)); } }; if (message) return <AuthShell title="Подтвердите email"><p>{message}</p><Link className="button" to={`/verify?email=${encodeURIComponent(email)}`}>Перейти к подтверждению</Link></AuthShell>; return <AuthShell title="Создайте свой путь."><form className="form" onSubmit={submit}><label>Email<input required name="email" type="email" autoComplete="email" /></label><label>Пароль <small>Минимум 12 символов</small><input required name="password" minLength={12} type="password" autoComplete="new-password" /></label>{error && <p className="form-error" role="alert">{error}</p>}<Button>Продолжить</Button><p>Уже есть аккаунт? <Link to="/login">Войти</Link></p></form></AuthShell>; }

function AuthShell({ title, children }: { title: string; children: React.ReactNode }) { return <main className="auth-page"><div className="auth-art"><p className="eyebrow">IMKON / opportunity</p><h1>{title}</h1><p>Платформа строится вокруг навыков, выбора и доступа — без обязательного раскрытия медицинской информации.</p></div><div className="auth-form">{children}</div></main>; }
