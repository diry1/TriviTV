const { chromium } = require("playwright");
const assert = require("node:assert/strict");
(async () => {
  const { createAppServer } = await import("../src/server.js");
  const { questions } = await import("../src/questions.js");
  let timeOffset = 0;
  const server = createAppServer({
    partyDemo: true,
    now: () => Date.now() + timeOffset,
  });
  await new Promise((r) => server.listen(0, "127.0.0.1", r));
  const base = `http://127.0.0.1:${server.address().port}`;
  let browser;
  try {
    browser = await chromium.launch({
      headless: true,
      executablePath: process.env.CHROMIUM_PATH || undefined,
      args: ["--no-sandbox"],
    });
    const errors = [];
    const ctx = await browser.newContext({
      viewport: { width: 1440, height: 1100 },
    });
    const host = await ctx.newPage();
    host.on("pageerror", (e) => errors.push(e.message));
    await host.goto(base);
    await host.locator("#create").waitFor();
    await host.screenshot({
      path: process.env.TRIVITV_SCREENSHOT || "/tmp/trivitv-home.png",
      fullPage: true,
    });
    await host.locator("[data-mode=trivia]").focus();
    await host.keyboard.press("ArrowDown");
    assert.equal(
      await host.evaluate(() => document.activeElement.dataset.mode),
      "millionaire",
    );
    await host.keyboard.press("Enter");
    assert(
      await host
        .locator("[data-mode=millionaire]")
        .evaluate((el) => el.classList.contains("active")),
    );
    await host.locator("[data-mode=trivia]").click();
    await host.locator("#all-categories").click();
    assert(await host.locator("#create").isDisabled());
    await host.locator("#all-categories").click();
    await host.locator("[data-region=US]").click();
    await host.locator("[data-category=Arts]").click();
    await host.locator("#create").click();
    await host.locator("#start").waitFor();
    const room = await host.evaluate(() =>
      JSON.parse(sessionStorage.getItem("trivitv-session")),
    );
    assert.equal(room.state.settings.region, "US");
    assert(!room.state.settings.categories.includes("Arts"));
    const phones = [];
    for (const name of ["Alice", "Bob"]) {
      const context = await browser.newContext({
        viewport: { width: 390, height: 844 },
      });
      const page = await context.newPage();
      page.on("pageerror", (e) => errors.push(e.message));
      await page.goto(`${base}/?join=${room.code}`);
      await page.locator("[name=name]").fill(name);
      await page.locator("#join-form button").click();
      await page.locator(".room-code").waitFor();
      assert.equal(
        await page.evaluate(
          () => document.documentElement.scrollWidth <= innerWidth,
        ),
        true,
      );
      phones.push(page);
    }
    await host.locator(".player").filter({ hasText: "Bob" }).waitFor();
    assert.equal(await host.locator(".player").count(), 3);
    await host.locator("#start").click();
    await host.locator('[data-answer="0"]').waitFor();
    for (let i = 0; i < 10; i++) {
      await host
        .locator(".game-meta")
        .filter({ hasText: `QUESTION ${i + 1} / 10` })
        .waitFor();
      await host.locator('[data-answer="0"]:not(:disabled)').click();
      for (let p = 0; p < phones.length; p++) {
        const phone = phones[p];
        await phone
          .locator(".game-meta")
          .filter({ hasText: `QUESTION ${i + 1} / 10` })
          .waitFor();
        await phone.locator('[data-answer="1"]:not(:disabled)').click();
        if (i === 0 && p === 0) {
          await phone.reload();
          await phone
            .locator(".answer-status")
            .filter({ hasText: "locked" })
            .waitFor();
          assert(await phone.locator('[data-answer="1"]').isDisabled());
          assert.equal(await phone.locator(".answer.correct").count(), 0);
        }
      }
      await host.locator(".answer.correct").waitFor();
      assert.equal(await host.locator("#reveal,#next").count(), 0);
      if (i === 0) {
        assert.equal(
          await host.evaluate(() => document.activeElement.id),
          "pause-review",
        );
        await host.keyboard.down("Enter");
        await host
          .locator("#review-countdown")
          .filter({ hasText: "Paused" })
          .waitFor();
        await host.keyboard.down("Enter"); // a held key must not toggle again
        assert.equal(await host.locator("#pause-review").innerText(), "Resume");
        await host.keyboard.up("Enter");
        timeOffset += 10000;
        await host.reload();
        await host
          .locator("#review-countdown")
          .filter({ hasText: "Paused" })
          .waitFor();
        assert.equal(await phones[0].locator("#pause-review").count(), 0);
        await host.locator("#pause-review").click();
        await host
          .locator("#pause-review")
          .filter({ hasText: "Pause" })
          .waitFor();
      }
      timeOffset += 5000; // advance server clock; no Next API or button exists
    }
    await host.locator("#finish").waitFor();
    assert.equal(await host.locator(".standings .player").count(), 3);
    await host.locator("#finish").click();
    await host.locator("[data-mode=millionaire]").click();
    await host.locator("#create").click();
    await host.locator("#start").click();
    await host.locator("#fifty").click();
    await host.locator(".answer:disabled").nth(1).waitFor();
    assert.equal(await host.locator(".answer:not(:disabled)").count(), 2);
    const text = await host.locator(".question").innerText();
    const answer = questions.find((q) => q.text === text).choices[0];
    await host
      .locator(".answer:not(:disabled)")
      .filter({ hasText: answer })
      .click();
    await host.locator(".answer.correct").waitFor();
    timeOffset += 5000;
    await host
      .locator(".game-meta")
      .filter({ hasText: "QUESTION 2 /" })
      .waitFor();
    host.once("dialog", (d) => d.accept());
    await host.locator("#walk").click();
    await host.locator("#finish").waitFor();
    assert.match(await host.locator(".big-score").innerText(), /100/);
    // Shared-remote handoff: answer only one selected local player at a time.
    await host.locator("#finish").click();
    await host.locator("[data-mode=trivia]").click();
    await host.locator("#create").click();
    await host.locator("#local-name").fill("Sofa friend");
    await host.locator("#add-form button").click();
    await host.locator(".player").filter({ hasText: "Sofa friend" }).waitFor();
    await host.locator("#start").click();
    await host.locator('[data-answer="0"]').click();
    await host
      .locator(".remote-turn")
      .filter({ hasText: "Sofa friend" })
      .waitFor();
    assert.equal(await host.locator("#local-player").count(), 0);
    assert.equal(
      await host.evaluate(() => document.activeElement.dataset.answer),
      "0",
    );
    await host.keyboard.press("ArrowRight");
    assert.equal(
      await host.evaluate(() => document.activeElement.dataset.answer),
      "1",
    );
    await host.keyboard.press("Enter");
    await host.locator(".answer.correct").waitFor();
    await host.setViewportSize({ width: 390, height: 844 });
    assert.equal(
      await host.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      ),
      true,
    );
    assert.deepEqual(errors, []);
    console.log(
      "PASS: three-player phone session, 10 rounds, results, region/categories, solo 50:50 and walk-away, automatic reveal/advance, Player 1 pause/resume across reload, held-key protection, shared remote handoff, keyboard navigation, mobile layout; no page errors",
    );
  } finally {
    await browser?.close();
    server.closeAllConnections();
    await new Promise((r) => server.close(r));
  }
})().catch((e) => {
  console.error(e);
  process.exit(1);
});
