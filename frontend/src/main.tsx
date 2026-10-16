import { createRoot } from "react-dom/client";
import { lazy, Suspense } from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { Footer, Header, Loading, MobileNav } from "./components";
import { Home, Login, Register, Vacancies, VacancyDetail } from "./pages";
import { AuthProvider } from "./state";
import { GoogleButton } from "./components/GoogleButton";
import "./styles.css";
import "./redesign.css";

const Admin = lazy(() => import("./private-pages").then(module => ({ default: module.Admin })));
const Dashboard = lazy(() => import("./private-pages").then(module => ({ default: module.Dashboard })));
const Employer = lazy(() => import("./private-pages").then(module => ({ default: module.Employer })));
const Verify = lazy(() => import("./private-pages").then(module => ({ default: module.Verify })));
const LearnPage = lazy(() => import("./future-pages").then(module => ({ default: module.LearnPage })));
const AiPage = lazy(() => import("./future-pages").then(module => ({ default: module.AiPage })));
const OpportunityPage = lazy(() => import("./future-pages").then(module => ({ default: module.OpportunityPage })));

function App() { return <AuthProvider><div className="app-shell"><Header /><Suspense fallback={<Loading />}><Routes><Route path="/" element={<Home />} /><Route path="/vacancies" element={<Vacancies />} /><Route path="/vacancies/:id" element={<VacancyDetail />} /><Route path="/login" element={<Login />} /><Route path="/register" element={<Register />} /><Route path="/verify" element={<Verify />} /><Route path="/dashboard" element={<Dashboard />} /><Route path="/employer" element={<Employer />} /><Route path="/admin" element={<Admin />} /><Route path="/learn" element={<LearnPage />} /><Route path="/ai" element={<AiPage />} /><Route path="/opportunity" element={<OpportunityPage />} /></Routes></Suspense><GoogleButton /><Footer /><MobileNav /></div></AuthProvider>; }
function Root() { return <BrowserRouter><App /></BrowserRouter>; }
createRoot(document.getElementById("root")!).render(<Root />);
if (import.meta.env.PROD && "serviceWorker" in navigator) {
  window.addEventListener("load", () => { void navigator.serviceWorker.register("/sw.js"); });
}
