# Future main-menu navigation

Recorded 2026-10-21 from user TV testing. Implemented and validated in the 2026-10-22 Ukrainian Fun Bank APK 0.9.0 (versionCode16), with the same layout. The bullets below describe the accepted behavior.

- Moving the remote's focus left/right onto a mode card selects that mode immediately. Avoid a separate selected-mode state that trails behind the focused card.
- Pressing OK/clicking the focused mode card moves focus to the next-step action for that mode: Start game, Create room, or the equivalent primary action.
- That first OK moves focus to the action; it does not also activate it. A subsequent OK activates the next step.
- Apply consistently to Trivia, Millionaire, one-versus-one/Turf War, and Imposter. Preserve the current screen layout.
- Verify that mode highlighting, action label/target and remote focus stay synchronized; no extra confirmation click should be needed to select a mode.
