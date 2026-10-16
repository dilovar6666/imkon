export type Locale = "ru" | "tg" | "en";
export const copy = {
  ru: { work: "Работа", learn: "Обучение", signIn: "Войти", join: "Создать аккаунт", find: "Найти работу", mission: "Возможности для каждого", unavailable: "Пока недоступно" },
  tg: { work: "Кор", learn: "Омӯзиш", signIn: "Ворид шудан", join: "Эҷоди ҳисоб", find: "Ёфтани кор", mission: "Имконият барои ҳар кас", unavailable: "Ҳоло дастрас нест" },
  en: { work: "Work", learn: "Learn", signIn: "Sign in", join: "Create account", find: "Find work", mission: "Opportunities for everyone", unavailable: "Not available yet" },
} as const;
