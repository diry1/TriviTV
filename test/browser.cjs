const { chromium } = require("playwright");
const assert = require("node:assert/strict");
(async () => {
  const { createAppServer } = await import("../src/server.js");
  const { questions } = await import("../src/questions.js");
  let timeOffset = 0;
  const server = createAppServer({
    partyDemo: true,
    answersRevealMs: 2000,
    correctRevealMs: 2000, // Hold stages for visual assertions; rule tests check production durations.
    now: () => Date.now() + timeOffset,
  });
  await new Promise((r) => server.listen(0, "127.0.0.1", r));
  const base = `http://127.0.0.1:${server.address().port}`;
  async function nextStage(page, expected) {
    const current = await page.evaluate(async () => {
      const session = JSON.parse(sessionStorage.getItem("trivitv-session"));
      return (
        await fetch(`/api/rooms/${session.code}`, {
          headers: { Authorization: `Bearer ${session.token}` },
        })
      ).json();
    });
    const deadline = current.stageEndsAt ?? current.review?.endsAt;
    assert(deadline != null, "expected a running stage deadline");
    timeOffset += Math.max(0, deadline - (Date.now() + timeOffset)) + 10;
    await page
      .locator(
        expected === "finished"
          ? ".results-page"
          : `.answers[data-stage="${expected}"]`,
      )
      .waitFor();
  }
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
      await host.locator('.answers[data-stage="answers"]').waitFor();
      assert.equal(await host.locator(".answer.correct").count(), 0);
      assert.equal(await host.locator(".answer-voters i").count(), 3);
      assert.equal(
        await host
          .locator(".answer")
          .first()
          .evaluate((el) => getComputedStyle(el).animationName),
        "reveal-picks",
      );
      await nextStage(host, "correct");
      assert.equal(await host.locator(".answer.correct").count(), 1);
      assert.equal(
        await host
          .locator(".answer.correct")
          .evaluate((el) => getComputedStyle(el).animationName),
        "reveal-correct",
      );
      await nextStage(host, "reveal");
      assert.equal(
        await host
          .locator("#pause-review,#review-countdown,#review-ring")
          .count(),
        0,
      );
      assert.equal(await host.locator("#reveal,#next").count(), 0);
      await nextStage(host, i === 9 ? "finished" : "question");
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
    await host.locator('.answers[data-stage="answers"]').waitFor();
    await nextStage(host, "correct");
    await nextStage(host, "reveal");
    assert.equal(await host.locator("#review-ring").count(), 1);
    assert.equal(await host.locator("#review-seconds").innerText(), "3");
    assert.equal(
      await host.evaluate(() => document.activeElement.id),
      "pause-review",
    );
    await host.screenshot({
      path: "/tmp/trivitv-millionaire-countdown.png",
      fullPage: true,
    });
    await host.keyboard.down("Enter");
    await host
      .locator("#review-countdown")
      .filter({ hasText: "Paused" })
      .waitFor();
    await host.keyboard.down("Enter");
    assert.equal(await host.locator("#pause-review").innerText(), "Resume");
    await host.keyboard.up("Enter");
    timeOffset += 10000;
    await host.reload();
    await host
      .locator("#review-countdown")
      .filter({ hasText: "Paused" })
      .waitFor();
    await host.locator("#pause-review").click();
    await host.locator("#pause-review").filter({ hasText: "Pause" }).waitFor();
    await nextStage(host, "question");
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
    await host.locator('.answers[data-stage="answers"]').waitFor();
    await nextStage(host, "correct");
    await nextStage(host, "reveal");
    assert.equal(await host.locator("#pause-review").count(), 0);
    await host.setViewportSize({ width: 390, height: 844 });
    assert.equal(
      await host.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      ),
      true,
    );
    await nextStage(host, "question");
    await host.locator("#answer-countdown").waitFor();
    timeOffset += 60000; // Neither shared-remote player answers this question.
    await host.locator('.answers[data-stage="answers"]').waitFor();
    assert.equal(
      await host
        .locator(".answer-voters i")
        .filter({ hasText: "random" })
        .count(),
      2,
    );
    await host.emulateMedia({ reducedMotion: "reduce" });
    assert.equal(
      await host
        .locator(".answer")
        .first()
        .evaluate((el) => getComputedStyle(el).animationName),
      "none",
    );
    await nextStage(host, "correct");
    await nextStage(host, "reveal");
    assert.deepEqual(errors, []);
    console.log(
      "PASS: three-player phone session, 10 rounds, results, region/categories, solo 50:50 and walk-away, automatic reveal/advance, Millionaire countdown/pause across reload, Trivia timeout/random picks, staged animations, reduced motion, shared remote handoff, mobile layout; no page errors",
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
