"""Sponsor integration layer. Each module exposes the same async function whether
it hits the real API (key present) or the cached fixture (mock) — so agents never
branch on liveness and the demo can't break."""
