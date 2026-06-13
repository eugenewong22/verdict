#!/usr/bin/env node
/*
 * Terminal 3 notary sidecar.
 *
 * Real Ed25519 agent identity + signing + mandate gate, exposed over HTTP for the
 * Python Notary to call. Zero npm dependencies — uses Node's built-in crypto, so
 * it runs with just `node server.js` (no install). When this is up, the Python
 * side auto-detects it and the Terminal 3 stage goes LIVE.
 *
 * The mandate model mirrors Terminal 3's delegation credential: a set of granted
 * functions + a value ceiling; an action is authorized only if in scope.
 *
 * To go to the real Terminal 3 testnet, swap signWithBuiltin() for the
 * @terminal3/t3n-sdk path — see TODO at the bottom.
 */
const http = require("http");
const crypto = require("crypto");
const fs = require("fs");
const path = require("path");

const PORT = process.env.T3_SIDECAR_PORT || 8787;
const KEY_PATH = path.join(__dirname, ".identity.json");

const b64u = (buf) => Buffer.from(buf).toString("base64url");

function loadIdentity() {
  let priv;
  if (fs.existsSync(KEY_PATH)) {
    priv = crypto.createPrivateKey({ key: JSON.parse(fs.readFileSync(KEY_PATH, "utf8")), format: "jwk" });
  } else {
    priv = crypto.generateKeyPairSync("ed25519").privateKey;
    fs.writeFileSync(KEY_PATH, JSON.stringify(priv.export({ format: "jwk" })));
  }
  const pub = crypto.createPublicKey(priv);
  const did = "did:key:z" + pub.export({ format: "jwk" }).x; // base64url 32-byte pubkey
  return { priv, pub, did };
}

const ID = loadIdentity();
const SCHEME = "ed25519 (terminal3 sidecar)";

const sign = (bytes) => b64u(crypto.sign(null, bytes, ID.priv));
const verify = (bytes, sig) => {
  try { return crypto.verify(null, bytes, ID.pub, Buffer.from(sig, "base64url")); }
  catch { return false; }
};
const sha256 = (bytes) => crypto.createHash("sha256").update(bytes).digest("hex");

function checkMandate(mandate, action) {
  const fns = mandate.functions || [];
  const cap = mandate.max_value_usd || 0;
  const val = action.value_usd || 0;
  if (val > cap) {
    const capH = cap >= 1e6 ? "$" + Math.round(cap / 1e6) + "M" : "$" + cap;
    return { authorized: false, reason: `mandate exceeded · cap ${capH}` };
  }
  if (!fns.includes(action.function)) return { authorized: false, reason: `'${action.function}' not in granted scope [${fns.join(", ")}]` };
  return { authorized: true, reason: "" };
}

const send = (res, code, obj) => { res.writeHead(code, { "Content-Type": "application/json" }); res.end(JSON.stringify(obj)); };
const readBody = (req) => new Promise((r) => { let d = ""; req.on("data", (c) => (d += c)); req.on("end", () => { try { r(JSON.parse(d || "{}")); } catch { r({}); } }); });

const server = http.createServer(async (req, res) => {
  try {
    if (req.method === "GET" && req.url === "/health")
      return send(res, 200, { ok: true, did: ID.did, scheme: SCHEME });

    if (req.method === "POST" && req.url === "/sign") {
      const { report_b64, mandate } = await readBody(req);
      const bytes = Buffer.from(report_b64 || "", "base64");
      const signature = sign(bytes);
      return send(res, 200, {
        did: ID.did, report_hash: sha256(bytes), signature,
        verified: verify(bytes, signature), scheme: SCHEME, mandate: mandate || {},
      });
    }

    if (req.method === "POST" && req.url === "/verify") {
      const { report_b64, signature } = await readBody(req);
      return send(res, 200, { verified: verify(Buffer.from(report_b64 || "", "base64"), signature) });
    }

    if (req.method === "POST" && req.url === "/mandate/check") {
      const { mandate, action } = await readBody(req);
      return send(res, 200, checkMandate(mandate || {}, action || {}));
    }

    send(res, 404, { error: "not found" });
  } catch (e) {
    send(res, 500, { error: String(e) });
  }
});

server.listen(PORT, () => console.log(`▸ Terminal 3 notary sidecar on http://127.0.0.1:${PORT}  did=${ID.did}`));

/*
 * TODO — live Terminal 3 testnet (replace the built-in signer):
 *   import { T3nClient, setEnvironment, loadWasmComponent, eth_get_address,
 *            metamask_sign, createEthAuthInput, signCredential } from "@terminal3/t3n-sdk";
 *   setEnvironment("testnet");
 *   const t3n = new T3nClient({ wasmComponent: await loadWasmComponent(),
 *     handlers: { EthSign: metamask_sign(addr, undefined, process.env.T3N_API_KEY) } });
 *   await t3n.handshake();
 *   const did = (await t3n.authenticate(createEthAuthInput(addr))).value;   // did:t3n:0x...
 *   const { sig } = signCredential(reportHashBuffer, Buffer.from(process.env.T3N_API_KEY.slice(2), "hex"));
 * The HTTP surface above stays identical, so the Python side needs no change.
 */
