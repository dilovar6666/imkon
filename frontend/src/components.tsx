import { ArrowRight, BriefcaseBusiness, CheckCircle2, ChevronRight, GraduationCap, House, LoaderCircle, Menu, Sparkles, UserRound, X } from "lucide-react";
import { Link, NavLink } from "react-router-dom";
import { useState } from "react";
import { copy } from "./lib/i18n";
import { useAuth } from "./state";

export { Button } from "./components/ui/button";
export function Brand() { return <Link className="brand" to="/" aria-label="IMKON, главная"><span>IM</span>KON<i /></Link>; }
export function Header() {
  const [open, setOpen] = useState(false); const { user, signOut } = useAuth(); const t = copy.ru;
  return <header className="site-header"><Brand /><nav className={open ? "open" : ""} aria-label="Основная навигация" onClick={() => setOpen(false)}><NavLink to="/vacancies">{t.work}</NavLink><NavLink to="/learn">{t.learn}</NavLink><NavLink to="/opportunity">Opportunity</NavLink><NavLink to="/ai">AI</NavLink>{user ? <><NavLink className="mobile-nav-link" to={user.role === "admin" ? "/admin" : user.role === "employer" ? "/employer" : "/dashboard"}>Кабинет</NavLink><button className="mobile-nav-link text-button" onClick={() => void signOut()}>Выйти</button></> : <><NavLink className="mobile-nav-link" to="/login">{t.signIn}</NavLink><NavLink className="mobile-nav-link" to="/register">{t.join}</NavLink></>}</nav><div className="head-actions"><span className="language-indicator" aria-label="Язык интерфейса: русский">RU</span>{user ? <><Link className="account-link" to={user.role === "admin" ? "/admin" : user.role === "employer" ? "/employer" : "/dashboard"}>Кабинет</Link><button className="text-button" onClick={() => void signOut()}>Выйти</button></> : <><Link className="text-button" to="/login">{t.signIn}</Link><Link className="button compact join-link" to="/register">{t.join}<ArrowRight size={15} /></Link></>}<button className="menu" type="button" aria-expanded={open} aria-label={open ? "Закрыть меню" : "Открыть меню"} onClick={() => setOpen(!open)}>{open ? <X /> : <Menu />}</button></div></header>;
}
export function Footer() { return <footer><Brand /><p>IMKON — цифровая платформа равных возможностей.</p><p>© {new Date().getFullYear()} · Бесплатно для соискателей и работодателей</p></footer>; }
export function MobileNav() {
  const { user } = useAuth();
  const accountPath = user?.role === "admin" ? "/admin" : user?.role === "employer" ? "/employer" : user ? "/dashboard" : "/login";
  return <nav className="mobile-bottom-nav" aria-label="Быстрая навигация"><NavLink end to="/"><House size={20} /><span>Главная</span></NavLink><NavLink to="/vacancies"><BriefcaseBusiness size={20} /><span>Работа</span></NavLink><NavLink to="/learn"><GraduationCap size={20} /><span>Обучение</span></NavLink><NavLink to={accountPath}><UserRound size={20} /><span>Кабинет</span></NavLink></nav>;
}
export function PageLead({ eyebrow, title, children }: { eyebrow: string; title: React.ReactNode; children?: React.ReactNode }) { return <section className="page-lead"><p className="eyebrow">{eyebrow}</p><h1>{title}</h1>{children}</section>; }
export function Notice({ title, children }: { title: string; children: React.ReactNode }) { return <aside className="notice"><Sparkles size={18} /><div><strong>{title}</strong><p>{children}</p></div></aside>; }
export function Loading() { return <div className="loading"><LoaderCircle className="spin" /> Загрузка…</div>; }
export function Empty({ title, children }: { title: string; children: React.ReactNode }) { return <div className="empty"><CheckCircle2 size={26} /><h3>{title}</h3><p>{children}</p></div>; }
export function Status({ children }: { children: React.ReactNode }) { return <span className="status">{children}</span>; }
export function ArrowLink({ to, children }: { to: string; children: React.ReactNode }) { return <Link className="arrow-link" to={to}>{children}<ChevronRight size={17} /></Link>; }
