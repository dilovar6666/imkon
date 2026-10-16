import assert from "node:assert/strict";
import { mkdir } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import AxeBuilder from "@axe-core/playwright";
import { chromium } from "playwright-core";

const baseUrl = process.env.IMKON_FRONTEND_URL ?? "http://127.0.0.1:5174";
const edgePath = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe";
const outputDir = path.join(os.tmpdir(), "imkon-browser-qa");
const sizes = [
  { width: 360, height: 800 },
  { width: 390, height: 844 },
  { width: 768, height: 1024 },
  { width: 1440, height: 900 },
  { width: 1920, height: 1080 },
];

await mkdir(outputDir, { recursive: true });
const browser = await chromium.launch({ executablePath: edgePath, headless: true });
const errors = [];
let checked = 0;
const audit = async (page, route) => {
  const results = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21aa", "wcag22aa"]).analyze();
  assert.deepEqual(results.violations.map(violation => `${violation.id}: ${violation.nodes.map(node => node.target.join(" ")).join(", ")}`), [], `${route}: accessibility violations`);
};
const assertNoOverflow = async (page, route) => {
  const widths = await page.evaluate(() => ({ document: document.documentElement.scrollWidth, viewport: document.documentElement.clientWidth }));
  assert.ok(widths.document <= widths.viewport + 2, `${route}: horizontal overflow ${JSON.stringify(widths)}`);
};

try {
  for (const size of sizes) {
    const page = await browser.newPage({ viewport: size, reducedMotion: "reduce" });
    page.on("pageerror", error => errors.push(`${size.width}: ${error.message}`));
    for (const route of ["/", "/vacancies", "/register", "/login", "/learn", "/ai", "/opportunity"]) {
      await page.goto(`${baseUrl}${route}`, { waitUntil: "domcontentloaded" });
      await page.locator(".loading").waitFor({ state: "hidden", timeout: 10000 });
      const metrics = await page.evaluate(() => {
        const heading = document.querySelector("h1");
        return {
          documentWidth: document.documentElement.scrollWidth,
          viewportWidth: document.documentElement.clientWidth,
          headingWidth: heading?.clientWidth ?? 0,
          headingContentWidth: heading?.scrollWidth ?? 0,
        };
      });
      assert.ok(metrics.documentWidth <= metrics.viewportWidth + 2, `${size.width}${route}: horizontal scroll ${JSON.stringify(metrics)}`);
      assert.ok(metrics.headingContentWidth <= metrics.headingWidth + 2, `${size.width}${route}: heading clipped ${JSON.stringify(metrics)}`);
      const label = route === "/" ? "home" : route.slice(1);
      await page.screenshot({ path: path.join(outputDir, `${label}-${size.width}.png`), fullPage: true });
      checked += 1;
    }
    if (size.width === 360) {
      await page.goto(baseUrl);
      const mobileNavigation = page.getByRole("navigation", { name: "Быстрая навигация" });
      await mobileNavigation.getByRole("link", { name: "Работа" }).click();
      assert.match(page.url(), /\/vacancies$/);
      await page.getByRole("button", { name: "Открыть меню" }).click();
      await page.getByRole("navigation", { name: "Основная навигация" }).getByRole("link", { name: "Войти" }).click();
      assert.match(page.url(), /\/login$/);
    }
    if (size.width === 1440) {
      await page.goto(`${baseUrl}/vacancies`, { waitUntil: "domcontentloaded" });
      await page.locator(".loading").waitFor({ state: "hidden", timeout: 10000 });
      assert.ok(await page.locator(".job-card").count() > 0, "Backend vacancy was not shown in catalogue");
      await page.getByLabel("Валюта").selectOption("TJS");
      await page.locator(".loading").waitFor({ state: "hidden", timeout: 10000 });
      assert.match(page.url(), /currency=TJS/);
      await page.getByRole("button", { name: "Сбросить" }).click();
      await page.locator(".job-card").first().waitFor({ timeout: 10000 });
      await page.goto(baseUrl);
      await page.getByRole("search").getByRole("textbox").fill("Python");
      await page.getByRole("search").getByRole("button", { name: "Искать вакансии" }).click();
      assert.match(page.url(), /\/vacancies\?query=Python/);
    }
    await page.close();
  }
  const accessibilityContext = await browser.newContext({ viewport: { width: 1440, height: 900 }, reducedMotion: "reduce" });
  const accessibilityPage = await accessibilityContext.newPage();
  for (const route of ["/", "/vacancies", "/register", "/learn", "/ai"]) {
    await accessibilityPage.goto(`${baseUrl}${route}`, { waitUntil: "domcontentloaded" });
    await accessibilityPage.locator(".loading").waitFor({ state: "hidden", timeout: 10000 });
    await audit(accessibilityPage, route);
  }
  await accessibilityPage.setViewportSize({ width: 360, height: 800 });
  await accessibilityPage.goto(`${baseUrl}/vacancies`, { waitUntil: "domcontentloaded" });
  await accessibilityPage.locator(".loading").waitFor({ state: "hidden", timeout: 10000 });
  await audit(accessibilityPage, "/vacancies mobile");
  await accessibilityPage.goto(baseUrl);
  await accessibilityPage.keyboard.press("Tab");
  assert.equal(await accessibilityPage.evaluate(() => document.activeElement?.tagName), "A", "First keyboard stop should be a link");
  await accessibilityContext.close();
  const accountContext = await browser.newContext({ viewport: { width: 1440, height: 900 }, reducedMotion: "reduce" });
  const accountPage = await accountContext.newPage();
  accountPage.on("pageerror", error => errors.push(`account: ${error.message}`));
  const email = `frontend.qa.${Date.now()}@example.com`;
  const password = "Frontend-QA-Only-2026!";
  const companyName = `Тестовая студия IMKON QA ${Date.now()}`;
  const vacancyTitle = `Python Developer IMKON QA ${Date.now()}`;
  await accountPage.goto(`${baseUrl}/register`);
  await accountPage.getByRole("textbox", { name: "Email" }).fill(email);
  await accountPage.getByLabel("Пароль").fill(password);
  await accountPage.getByRole("button", { name: "Продолжить" }).click();
  await Promise.race([
    accountPage.getByText(/Development code:/).waitFor({ timeout: 10000 }),
    accountPage.locator(".form-error").waitFor({ timeout: 10000 }),
  ]);
  const registrationText = await accountPage.locator(".auth-form").innerText();
  const code = registrationText.match(/Development code: (\d{6})/)?.[1];
  assert.ok(code, `Local development verification code not returned: ${registrationText}`);
  await accountPage.getByRole("link", { name: "Перейти к подтверждению" }).click();
  await accountPage.getByRole("textbox", { name: "Код" }).fill(code);
  await accountPage.getByRole("button", { name: "Подтвердить email" }).click();
  await accountPage.waitForURL("**/dashboard");
  await accountPage.getByRole("heading", { name: "Профиль" }).waitFor();
  await accountPage.getByLabel("Имя").fill("Тестовый соискатель");
  await accountPage.getByRole("button", { name: "Сохранить профиль" }).click();
  await accountPage.getByText("Профиль сохранён").waitFor();
  await accountPage.getByLabel("Желаемая должность").last().fill("Python Developer");
  assert.equal(await accountPage.locator(".resume-preview h3").innerText(), "Python Developer");
  await accountPage.getByRole("button", { name: "Создать резюме" }).click();
  await accountPage.getByText("Резюме сохранено").waitFor();
  await accountPage.screenshot({ path: path.join(outputDir, "dashboard-1440.png"), fullPage: true });
  await audit(accountPage, "/dashboard");
  await accountPage.setViewportSize({ width: 390, height: 844 });
  await assertNoOverflow(accountPage, "/dashboard mobile");
  await accountPage.screenshot({ path: path.join(outputDir, "dashboard-390.png"), fullPage: true });
  await audit(accountPage, "/dashboard mobile");
  await accountPage.setViewportSize({ width: 1440, height: 900 });
  await accountPage.goto(`${baseUrl}/vacancies`);
  await accountPage.locator(".job-card a").first().click();
  await accountPage.getByRole("button", { name: "Отправить отклик" }).click();
  await accountPage.getByText("Отклик отправлен").waitFor();
  await accountPage.screenshot({ path: path.join(outputDir, "vacancy-detail-1440.png"), fullPage: true });
  await audit(accountPage, "/vacancies/:id");
  await accountPage.goto(`${baseUrl}/employer`);
  await accountPage.getByRole("heading", { name: "Заявка работодателя" }).waitFor();
  await accountPage.getByLabel("Название / имя").fill(companyName);
  await accountPage.getByLabel("Описание деятельности").fill("Демонстрационная проверка сценария подачи заявки работодателя.");
  await accountPage.getByLabel("Контакт").fill("qa@example.com");
  await accountPage.getByRole("button", { name: "Отправить на проверку" }).click();
  await accountPage.getByText(companyName).waitFor();
  await accountPage.screenshot({ path: path.join(outputDir, "employer-1440.png"), fullPage: true });
  await accountContext.close();
  if (process.env.IMKON_QA_ADMIN_EMAIL && process.env.IMKON_QA_ADMIN_PASSWORD) {
    const adminContext = await browser.newContext({ viewport: { width: 1440, height: 900 } });
    const adminPage = await adminContext.newPage();
    adminPage.on("pageerror", error => errors.push(`admin: ${error.message}`));
    adminPage.on("dialog", dialog => void dialog.accept());
    await adminPage.goto(`${baseUrl}/login`);
    await adminPage.getByRole("textbox", { name: "Email" }).fill(process.env.IMKON_QA_ADMIN_EMAIL);
    await adminPage.getByLabel("Пароль").fill(process.env.IMKON_QA_ADMIN_PASSWORD);
    await adminPage.getByRole("button", { name: "Войти" }).click();
    await adminPage.waitForURL("**/dashboard");
    await adminPage.goto(`${baseUrl}/admin`);
    const companyRow = adminPage.locator(".admin-record").filter({ hasText: companyName });
    await companyRow.waitFor({ timeout: 10000 }).catch(async () => { throw new Error(`Admin application not visible: ${(await adminPage.locator("main").innerText()).slice(0, 1200)}`); });
    await companyRow.getByRole("button", { name: "Одобрить" }).click();
    await adminPage.locator(".loading").waitFor({ state: "hidden", timeout: 10000 });
    await adminPage.getByText(companyName).waitFor();
    await adminPage.locator(".admin-section").first().waitFor({ state: "visible" });
    await adminPage.screenshot({ path: path.join(outputDir, "admin-1440.png"), fullPage: true });
    await audit(adminPage, "/admin");
    await adminPage.setViewportSize({ width: 390, height: 844 });
    await assertNoOverflow(adminPage, "/admin mobile");
    await adminPage.screenshot({ path: path.join(outputDir, "admin-390.png"), fullPage: true });
    await adminPage.setViewportSize({ width: 1440, height: 900 });
    const employerContext = await browser.newContext({ viewport: { width: 1440, height: 900 } });
    const employerPage = await employerContext.newPage();
    employerPage.on("pageerror", error => errors.push(`employer: ${error.message}`));
    await employerPage.goto(`${baseUrl}/login`);
    await employerPage.getByRole("textbox", { name: "Email" }).fill(email);
    await employerPage.getByLabel("Пароль").fill(password);
    await employerPage.getByRole("button", { name: "Войти" }).click();
    await employerPage.waitForURL("**/dashboard");
    await employerPage.goto(`${baseUrl}/employer`);
    await employerPage.getByRole("heading", { name: "Создать вакансию" }).waitFor();
    await employerPage.getByLabel("Название").fill(vacancyTitle);
    await employerPage.getByLabel("Описание", { exact: true }).fill("Демонстрационная постоянная удалённая работа для проверки модерации вакансий IMKON.");
    await employerPage.getByRole("button", { name: "Создать черновик" }).click();
    await employerPage.getByRole("button", { name: "Отправить на модерацию" }).click();
    await employerPage.getByText("Вакансия отправлена на модерацию.").waitFor();
    await employerPage.screenshot({ path: path.join(outputDir, "employer-workspace-1440.png"), fullPage: true });
    await audit(employerPage, "/employer");
    await employerPage.setViewportSize({ width: 390, height: 844 });
    await assertNoOverflow(employerPage, "/employer mobile");
    await employerPage.screenshot({ path: path.join(outputDir, "employer-workspace-390.png"), fullPage: true });
    await employerPage.setViewportSize({ width: 1440, height: 900 });
    await adminPage.reload();
    const vacancyRow = adminPage.locator(".admin-record").filter({ hasText: vacancyTitle });
    await vacancyRow.getByRole("button", { name: "Опубликовать" }).click();
    await adminPage.goto(`${baseUrl}/vacancies?query=${encodeURIComponent(vacancyTitle)}`);
    await adminPage.getByRole("heading", { name: vacancyTitle }).waitFor();
    await employerContext.close();
    await adminContext.close();
  }
  assert.deepEqual(errors, [], `Browser page errors: ${errors.join("; ")}`);
  console.log(`Passed ${checked} responsive page checks and account flows; screenshots: ${outputDir}`);
} finally {
  await browser.close();
}
