import { useEffect, useRef, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { createPortal } from "react-dom";
import { useAuth } from "../state";

declare global {
  interface Window {
    google?: { accounts: { id: { initialize: (options: { client_id: string; callback: (response: { credential: string }) => void }) => void; renderButton: (element: HTMLElement, options: Record<string, string>) => void } } };
  }
}

export function GoogleButton() {
  const location = useLocation();
  const navigate = useNavigate();
  const { signInWithGoogle } = useAuth();
  const container = useRef<HTMLDivElement>(null);
  const [error, setError] = useState("");
  const [target, setTarget] = useState<HTMLElement | null>(null);
  useEffect(() => { setTarget(document.querySelector<HTMLElement>(".auth-form")); }, [location.pathname]);
  useEffect(() => {
    const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID as string | undefined;
    if (!clientId || !["/login", "/register"].includes(location.pathname)) return;
    const render = () => {
      if (!window.google || !container.current) return;
      window.google.accounts.id.initialize({ client_id: clientId, callback: response => {
        void signInWithGoogle(response.credential).then(() => navigate("/dashboard")).catch(reason => setError(reason instanceof Error ? reason.message : "Google авторизация не выполнена"));
      } });
      window.google.accounts.id.renderButton(container.current, { theme: "outline", size: "large", width: "360" });
    };
    const script = document.querySelector<HTMLScriptElement>('script[data-google-gsi="true"]');
    if (script) { render(); return; }
    const next = document.createElement("script");
    next.src = "https://accounts.google.com/gsi/client"; next.async = true; next.defer = true; next.dataset.googleGsi = "true"; next.onload = render; next.onerror = () => setError("Не удалось загрузить Google авторизацию"); document.head.appendChild(next);
  }, [location.pathname, navigate, signInWithGoogle]);
  if (!["/login", "/register"].includes(location.pathname) || !import.meta.env.VITE_GOOGLE_CLIENT_ID) return null;
  if (!target) return null;
  return createPortal(<div className="google-auth"><p className="oauth-label">Или продолжить с Google</p><div ref={container} aria-label="Продолжить с Google" />{error && <p className="form-error" role="alert">{error}</p>}</div>, target);
}
