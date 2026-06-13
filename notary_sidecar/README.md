# Terminal 3 notary sidecar

Real Ed25519 agent identity + signing + mandate gate over HTTP. The Python Notary
auto-detects this on `http://127.0.0.1:8787` — **start it and the Terminal 3 stage
goes LIVE** (the stage tag flips from `MOCK`). Zero npm install required.

```bash
node notary_sidecar/server.js        # or: cd notary_sidecar && npm start
```

## Endpoints
- `GET  /health` → `{ ok, did, scheme }`
- `POST /sign` `{ report_b64, mandate }` → `{ did, report_hash, signature, verified, scheme, mandate }`
- `POST /verify` `{ report_b64, signature }` → `{ verified }`
- `POST /mandate/check` `{ mandate, action }` → `{ authorized, reason }`

The agent identity persists in `.identity.json` (stable DID across restarts).

To go to the real Terminal 3 testnet, swap the built-in signer for `@terminal3/t3n-sdk`
(`npm install`, then follow the TODO block at the bottom of `server.js`). The HTTP
surface is unchanged, so no Python changes are needed.
