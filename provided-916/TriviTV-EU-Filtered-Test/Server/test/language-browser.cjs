const { chromium } = require("playwright");
const assert = require("node:assert/strict");
(async () => {
  const { createAppServer } = await import("../src/server.js");
  let offset = 0;
  let frozenAt = null;
  const server = createAppServer({ now: () => frozenAt ?? Date.now() + offset });
  await new Promise((r) => server.listen(0, "127.0.0.1", r));
  const base = `http://127.0.0.1:${server.address().port}`;
  let browser;
  try {
    browser = await chromium.launch({
      headless: true,
      executablePath: process.env.CHROMIUM_PATH || undefined,
      args: ["--no-sandbox"],
    });
    const context = await browser.newContext({
      viewport: { width: 1440, height: 1080 },
    });
    const errors = [];
    context.on("page", (p) => p.on("pageerror", (e) => errors.push(e.message)));
    const apkEntry = await context.newPage();
    await apkEntry.goto(`${base}/?language=uk`);
    await apkEntry.locator("#create").filter({ hasText: "Створити гру" }).waitFor();
    assert.equal(await apkEntry.getAttribute("html", "lang"), "uk");
    assert.equal(await apkEntry.locator("#language").inputValue(), "uk");
    assert.equal(await apkEntry.locator('[data-region="Europe"]').getAttribute("aria-pressed"), "true");
    const configuration = await (await fetch(`${base}/api/config`)).json();
    assert.match(await apkEntry.locator("#pool-availability").innerText(),
      new RegExp(`: ${configuration.pools.uk.Europe.count}\\.$`));
    await apkEntry.locator("#category-toggle").click();
    await apkEntry.locator("#all-categories").click();
    assert(await apkEntry.locator("#create").isDisabled());
    await apkEntry.locator('[data-category="Television"]').click();
    assert.match(await apkEntry.locator("#pool-availability").innerText(),
      new RegExp(`: ${configuration.pools.uk.Europe.categories.Television}\\.$`));
    assert(!(await apkEntry.locator("#create").isDisabled()));
    await apkEntry.close();
    const host = await context.newPage();
    await host.goto(base);
    await host.locator("#create").waitFor();
    await host.locator('[data-region="US"]').click();
    await host.selectOption("#language", "uk");
    assert.equal(await host.locator('[data-region="Europe"]').getAttribute("aria-pressed"), "true");
    await host.locator("#create").filter({ hasText: "Створити гру" }).waitFor();
    assert.equal(await host.getAttribute("html", "lang"), "uk");
    assert.match(
      await host.locator(".translation-preview").innerText(),
      /Перекладено \d+ із 38926/,
    );
    await host.locator("#category-toggle").click();
    assert.match(
      await host.locator('[data-category="Animals"]').innerText(),
      /Тварини/,
    );
    assert.equal(await host.locator("[data-category]").count(), 20);
    await host.locator("#category-toggle").click();
    await host.screenshot({ path: "/tmp/trivitv-uk-home.png", fullPage: true });
    await host.reload();
    await host.locator("#create").filter({ hasText: "Створити гру" }).waitFor();
    await host.locator("#create").click();
    await host.locator("#start").waitFor();
    assert(await host.locator("#language").isDisabled());
    const session = await host.evaluate(() =>
      JSON.parse(sessionStorage.getItem("trivitv-session")),
    );
    const phone = await context.newPage();
    await phone.setViewportSize({ width: 390, height: 844 });
    // A phone initially in English must adopt the room's language after joining.
    await phone.goto(`${base}/?join=${session.code}`);
    await phone.selectOption("#language", "en");
    await phone.locator("[name=name]").fill("Ready");
    await phone.locator("#join-form button").click();
    await phone.getByText("Чекаємо на ведучого…", { exact: true }).waitFor();
    assert.equal(await phone.getAttribute("html", "lang"), "uk");
    assert.equal(
      await phone
        .locator(".player strong")
        .filter({ hasText: /^Ready$/ })
        .count(),
      1,
    );
    assert(
      await phone.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      ),
    );
    await host.locator("#start").click();
    await host.locator(".answer:not(:disabled)").first().waitFor();
    assert.match(
      await host.locator(".question").innerText(),
      /[А-Яа-яІіЇїЄєҐґ]/u,
    );
    assert.equal(
      await phone.locator(".question").innerText(),
      await host.locator(".question").innerText(),
    );
    await host.locator('[data-answer="0"]').click();
    await phone.locator('[data-answer="1"]').click();
    await host.locator("#review-ring").waitFor();
    // Freeze the injected clock while inspecting/clicking the short review UI.
    // A slow browser/long question must not consume its four-second window.
    frozenAt = Date.now() + offset;
    assert.equal(
      (await host.locator("#pause-review").innerText()).trim(),
      "Пауза",
    );
    assert.match(
      await host.locator(".result-note").innerText(),
      /^Правильна відповідь:/,
    );
    await host.locator("#pause-review").click();
    await host
      .locator("#review-countdown")
      .filter({ hasText: "Пауза" })
      .waitFor();
    assert.match(
      (await host.locator("#pause-review").innerText()).trim(),
      /Продовжити/,
    );
    frozenAt = null;
    await host.screenshot({
      path: "/tmp/trivitv-uk-trivia.png",
      fullPage: true,
    });
    // Return to setup, switch modes and retain Ukrainian independently of region.
    host.once("dialog", (d) => d.accept());
    await host.locator("#home").click();
    await host.locator("[data-mode=millionaire]").click();
    await host.locator("[data-region=US]").click();
    await host.locator("#create").click();
    await host.locator("#start").click();
    await host.locator(".answer:not(:disabled)").first().waitFor();
    await host.locator('[data-answer="0"]').click();
    await host.locator("#next").waitFor();
    assert.match(
      await host.locator("#next").innerText(),
      /Наступне запитання|Переглянути результати/,
    );
    assert.equal(await host.evaluate(() => document.activeElement.id), "next");
    assert.equal(await host.locator("#review-ring").count(), 0);
    await host.screenshot({
      path: "/tmp/trivitv-uk-millionaire.png",
      fullPage: true,
    });
    host.once("dialog", (d) => d.accept());
    await host.locator("#home").click();
    await host.selectOption("#language", "en");
    assert.equal(await host.getAttribute("html", "lang"), "en");
    assert.equal(
      await host.locator(".header-note").innerText(),
      "GOOD COMPANY. GREAT QUESTIONS.",
    );
    assert.equal(await host.locator(".translation-preview").count(), 0);
    assert.deepEqual(errors, []);
    console.log(
      "PASS: Ukrainian setup and persistence, all category labels, cross-language phone joining, unchanged player names, matching questions, answer reveal/pause, Millionaire Next, independent US region, mobile layout and switching back to English; no page errors",
    );
  } finally {
    await browser?.close();
    await new Promise((r) => {
      server.closeAllConnections();
      server.close(r);
    });
  }
})().catch((e) => {
  console.error(e);
  process.exitCode = 1;
});
