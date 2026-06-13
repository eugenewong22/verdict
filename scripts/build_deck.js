const pptxgen = require("pptxgenjs");
const p = new pptxgen();
p.defineLayout({ name: "W", width: 13.333, height: 7.5 });
p.layout = "W";
p.author = "Verdict"; p.title = "Verdict — Pitch";

const SANS = "Helvetica Neue", MONO = "Menlo";
const C = {
  bg:"0A0B0E", card:"11151F", line:"20242F",
  green:"35D07F", greenSoft:"7EE3AD", red:"EF5D5D", redSoft:"EF9D9D",
  amber:"E8B84B", blue:"5B9BFF", purple:"B794F6",
  text:"E8ECF2", body:"C9D1D9", muted:"9AA2B2", faint:"6B7385", ghost:"454B59",
};
const sh = () => ({ type:"outer", color:"000000", blur:16, offset:6, angle:135, opacity:0.5 });

function base(){ const s = p.addSlide(); s.background = { color:C.bg }; return s; }
function vmark(s, x, y, sz){
  s.addShape(p.shapes.ROUNDED_RECTANGLE, { x, y, w:sz, h:sz, fill:{color:C.green}, rectRadius:sz*0.22 });
  s.addText("V", { x, y, w:sz, h:sz, fontFace:MONO, fontSize:sz*30, bold:true, color:C.bg, align:"center", valign:"middle", margin:0 });
}
function eyebrow(s, t, x, y){ s.addText(t, { x, y, w:11.5, h:0.3, fontFace:MONO, fontSize:11, color:C.faint, charSpacing:3, bold:true, margin:0 }); }
function footer(s, n){
  s.addText("VERDICT · AGENT FORGE SG", { x:0.7, y:7.04, w:6, h:0.3, fontFace:MONO, fontSize:8.5, color:C.ghost, charSpacing:2, margin:0 });
  s.addText(String(n).padStart(2,"0")+" / 08", { x:11.6, y:7.04, w:1.03, h:0.3, fontFace:MONO, fontSize:8.5, color:C.ghost, align:"right", margin:0 });
}
function card(s, x, y, w, h, accent, fill){
  s.addShape(p.shapes.RECTANGLE, { x, y, w, h, fill:{color:fill||C.card}, line:{color:C.line, width:1}, shadow:sh() });
  if (accent) s.addShape(p.shapes.RECTANGLE, { x, y, w:0.06, h, fill:{color:accent} });
}

/* ---------- Slide 1 · title ---------- */
let s = base();
vmark(s, 0.7, 0.66, 0.62);
s.addText("VERDICT", { x:1.5, y:0.62, w:6, h:0.5, fontFace:SANS, fontSize:26, bold:true, color:C.text, charSpacing:1, valign:"middle", margin:0 });
s.addText("AUTONOMOUS DUE-DILIGENCE", { x:1.5, y:1.12, w:7, h:0.3, fontFace:MONO, fontSize:9.5, color:C.faint, charSpacing:3, margin:0 });
s.addText([
  { text:"An AI analyst that earns a", options:{ breakLine:true } },
  { text:"verifiable mandate to act.", options:{ color:C.green } },
], { x:0.68, y:2.45, w:12, h:1.9, fontFace:SANS, fontSize:42, bold:true, color:C.text, lineSpacingMultiple:1.06, margin:0 });
s.addText("Type a company. A crew of specialist agents researches the live web and earnings videos, reasons to a thesis, runs a valuation in a sandbox, and produces a memo, deck and model — then cryptographically signs the verdict and earns a revocable mandate to execute one authorized action. In ~90 seconds.",
  { x:0.72, y:4.55, w:10.8, h:1.5, fontFace:SANS, fontSize:15, color:C.muted, lineSpacingMultiple:1.32, margin:0 });
s.addShape(p.shapes.LINE, { x:0.72, y:6.45, w:11.9, h:0, line:{color:C.line, width:1} });
s.addText([
  { text:"5 STAGES", options:{ color:C.green } }, { text:"   ·   ", options:{ color:C.ghost } },
  { text:"8 PLATFORMS", options:{ color:C.green } }, { text:"   ·   ", options:{ color:C.ghost } },
  { text:"1 SIGNED DECISION", options:{ color:C.green } },
], { x:0.72, y:6.6, w:9, h:0.4, fontFace:MONO, fontSize:11, bold:true, charSpacing:2, valign:"middle", margin:0 });
s.addText("● SEALED", { x:10.8, y:6.6, w:1.85, h:0.4, fontFace:MONO, fontSize:11, bold:true, color:C.green, align:"right", charSpacing:2, valign:"middle", margin:0 });

/* ---------- Slide 2 · problem ---------- */
s = base(); footer(s, 2);
vmark(s, 0.7, 0.6, 0.4); eyebrow(s, "THE PROBLEM", 1.25, 0.66);
s.addText([
  { text:"Due diligence is slow —", options:{ breakLine:true } },
  { text:"and you can't audit the answer." },
], { x:0.7, y:1.25, w:11.9, h:1.3, fontFace:SANS, fontSize:34, bold:true, color:C.text, lineSpacingMultiple:1.05, margin:0 });
function statCard(x, big, bigColor, label){
  card(s, x, 3.0, 5.65, 2.6);
  s.addText(big, { x:x+0.32, y:3.25, w:5, h:1.1, fontFace:SANS, fontSize:60, bold:true, color:bigColor, margin:0 });
  s.addText(label, { x:x+0.34, y:4.45, w:5.0, h:1.0, fontFace:SANS, fontSize:14.5, color:C.muted, lineSpacingMultiple:1.3, valign:"top", margin:0 });
}
statCard(0.7, "Days", C.green, "per company — research scattered across filings, news, earnings calls and models.");
statCard(6.68, "Zero", C.red, "verifiable provenance. The deliverable is a PDF that says “trust me, I read everything.”");
s.addText("In a world of autonomous agents, an unauditable recommendation is a liability — not a deliverable.",
  { x:0.72, y:6.0, w:11.6, h:0.6, fontFace:SANS, fontSize:15, italic:true, color:C.body, margin:0 });

/* ---------- Slide 3 · solution ---------- */
s = base(); footer(s, 3);
vmark(s, 0.7, 0.6, 0.4); eyebrow(s, "THE SOLUTION", 1.25, 0.66);
s.addText("A signed, mandate-gated verdict — in ~90 seconds.", { x:0.7, y:1.25, w:11.9, h:0.8, fontFace:SANS, fontSize:30, bold:true, color:C.text, margin:0 });
s.addText("Verdict turns a company name into an audited investment decision. A crew of agents perceives, reasons, computes and produces — then a notary signs the report and gates the action behind a verifiable mandate. The whole run streams live in an “analyst war room.”",
  { x:0.72, y:2.2, w:11.5, h:1.1, fontFace:SANS, fontSize:15, color:C.muted, lineSpacingMultiple:1.32, margin:0 });
const stat3 = [["~90s","to a signed, auditable verdict",C.green],["5","specialist agents in one pipeline",C.text],["8","sponsor platforms — 5 already live",C.text]];
stat3.forEach((r,i)=>{ const x=0.7+i*4.0; card(s, x, 3.65, 3.75, 2.35, C.green);
  s.addText(r[0], { x:x+0.3, y:3.88, w:3.2, h:1.0, fontFace:SANS, fontSize:44, bold:true, color:r[2], margin:0 });
  s.addText(r[1], { x:x+0.32, y:4.95, w:3.15, h:0.9, fontFace:SANS, fontSize:13.5, color:C.muted, lineSpacingMultiple:1.2, valign:"top", margin:0 });
});

/* ---------- Slide 4 · spine ---------- */
s = base(); footer(s, 4);
vmark(s, 0.7, 0.6, 0.4); eyebrow(s, "HOW IT WORKS · THE AGENTIC SPINE", 1.25, 0.66);
s.addText("Five specialist agents, one pipeline.", { x:0.7, y:1.25, w:11.9, h:0.7, fontFace:SANS, fontSize:30, bold:true, color:C.text, margin:0 });
const stages = [
  ["01 · PERCEIVE","SCOUT","Bright Data · VideoDB"], ["02 · REASON","ANALYST","Kimi K2 · TokenRouter"],
  ["03 · COMPUTE","QUANT","Daytona"], ["04 · PRODUCE","PRODUCER","python-pptx · openpyxl"],
  ["05 · VERIFY · ACT","NOTARY","Terminal 3 · Nosana"],
];
{ const n=stages.length, gap=0.36, cw=(11.93-(n-1)*gap)/n, y=2.55, h=3.0;
  stages.forEach((st,i)=>{ const x=0.7+i*(cw+gap), accent=i===4?C.green:C.blue;
    card(s, x, y, cw, h, accent);
    s.addText(st[0], { x:x+0.18, y:y+0.22, w:cw-0.32, h:0.5, fontFace:MONO, fontSize:8, color:C.faint, charSpacing:1, bold:true, valign:"top", margin:0 });
    s.addText(st[1], { x:x+0.18, y:y+0.78, w:cw-0.32, h:0.5, fontFace:SANS, fontSize:18, bold:true, color:C.text, margin:0 });
    s.addText(st[2], { x:x+0.18, y:y+1.55, w:cw-0.32, h:1.2, fontFace:MONO, fontSize:9, color:C.muted, lineSpacingMultiple:1.35, valign:"top", margin:0 });
    if (i<n-1) s.addText("›", { x:x+cw-0.04, y:y+1.15, w:gap+0.08, h:0.5, fontFace:SANS, fontSize:20, color:C.faint, align:"center", valign:"middle", margin:0 });
  });
}
s.addText("Each agent owns its sponsor APIs. The thesis flows left to right; the Notary signs it and gates the action.",
  { x:0.72, y:5.9, w:11.6, h:0.5, fontFace:SANS, fontSize:14, color:C.muted, italic:true, margin:0 });

/* ---------- Slide 5 · differentiator ---------- */
s = base(); footer(s, 5);
vmark(s, 0.7, 0.6, 0.4); eyebrow(s, "THE DIFFERENTIATOR · INNOVATION", 1.25, 0.66);
s.addText("Identity that enforces execution.", { x:0.7, y:1.25, w:11.9, h:0.7, fontFace:SANS, fontSize:30, bold:true, color:C.text, margin:0 });
s.addText("Most agents treat identity as a login badge. Verdict makes it a gate.", { x:0.72, y:2.35, w:5.3, h:1.0, fontFace:SANS, fontSize:18, bold:true, color:C.text, lineSpacingMultiple:1.2, margin:0 });
s.addText("A Decentralized ID signs the report into a verifiable credential (Ed25519). A revocable mandate declares what the agent may do — and a cap on how much. The agent acts only inside that mandate.",
  { x:0.72, y:3.55, w:5.3, h:2.0, fontFace:SANS, fontSize:14.5, color:C.muted, lineSpacingMultiple:1.35, valign:"top", margin:0 });
function gate(x, y, accent, fill, reqRuns, badge, badgeColor, reason, reasonColor, landed){
  const h = landed ? 1.95 : 1.5;
  card(s, x, y, 5.83, h, accent, fill);
  s.addText("MANDATE GATE", { x:x+0.25, y:y+0.18, w:5.3, h:0.25, fontFace:MONO, fontSize:8, color:C.faint, charSpacing:2, bold:true, margin:0 });
  s.addText(reqRuns, { x:x+0.25, y:y+0.5, w:5.35, h:0.32, fontFace:MONO, fontSize:12.5, valign:"middle", margin:0 });
  s.addShape(p.shapes.RECTANGLE, { x:x+0.25, y:y+0.92, w:1.25, h:0.34, fill:{color:badgeColor} });
  s.addText(badge, { x:x+0.25, y:y+0.92, w:1.25, h:0.34, fontFace:MONO, fontSize:10, bold:true, color:C.bg, align:"center", valign:"middle", charSpacing:1, margin:0 });
  s.addText(reason, { x:x+1.62, y:y+0.92, w:4.0, h:0.34, fontFace:MONO, fontSize:11, color:reasonColor, valign:"middle", margin:0 });
  if (landed) s.addText(landed, { x:x+0.25, y:y+1.45, w:5.3, h:0.32, fontFace:MONO, fontSize:10.5, color:C.green, valign:"middle", margin:0 });
}
gate(6.5, 2.35, C.red, "140E10",
  [{text:"request: ",options:{color:C.muted}},{text:"open_position($50,000,000)",options:{color:C.redSoft}}],
  "DENIED", C.red, "mandate exceeded · cap $10M", C.redSoft);
gate(6.5, 4.05, C.green, "0C1611",
  [{text:"request: ",options:{color:C.muted}},{text:"commit_report + flag_ic_review",options:{color:C.body}}],
  "AUTHORIZED", C.green, "signature verified ✓", C.greenSoft, "↳ git commit 7e1d4a · verdict-reports@main ✓");
s.addText("We show it get denied, then authorized — live. No other team's agent can say that.",
  { x:0.72, y:6.35, w:11.6, h:0.5, fontFace:SANS, fontSize:14.5, italic:true, color:C.body, margin:0 });

/* ---------- Slide 6 · breadth ---------- */
s = base(); footer(s, 6);
vmark(s, 0.7, 0.6, 0.4); eyebrow(s, "BREADTH · EIGHT PLATFORMS, EACH LOAD-BEARING", 1.25, 0.66);
s.addText("One product that genuinely needs the whole stack.", { x:0.7, y:1.25, w:11.9, h:0.7, fontFace:SANS, fontSize:28, bold:true, color:C.text, margin:0 });
const sponsors = [
  ["Bright Data","live web · MCP",true],["Kimi K2","reasoning · 256K ctx",true],["Daytona","secure sandbox",true],["VideoDB","earnings-video search",true],
  ["Terminal 3","identity · mandate",true],["Nosana","decentralised GPU",false],["TokenRouter","model routing",false],["SenseNova","multimodal",false],
];
{ const cols=4, gx=0.3, gy=0.3, cw=(11.93-(cols-1)*gx)/cols, ch=1.7, y0=2.4;
  sponsors.forEach((sp,i)=>{ const r=Math.floor(i/cols), col=i%cols, x=0.7+col*(cw+gx), y=y0+r*(ch+gy);
    card(s, x, y, cw, ch, sp[2]?C.green:C.line);
    s.addText(sp[0], { x:x+0.22, y:y+0.26, w:cw-0.4, h:0.4, fontFace:SANS, fontSize:16, bold:true, color:C.text, margin:0 });
    s.addText(sp[1], { x:x+0.22, y:y+0.76, w:cw-0.4, h:0.35, fontFace:MONO, fontSize:9.5, color:C.muted, margin:0 });
    s.addText(sp[2]?"● LIVE":"○ READY", { x:x+0.22, y:y+1.22, w:cw-0.4, h:0.3, fontFace:MONO, fontSize:9, bold:true, color:sp[2]?C.green:C.faint, charSpacing:1, margin:0 });
  });
}
s.addText("Breadth is scored here — and it's honest: remove any one platform and the product visibly loses a capability.",
  { x:0.72, y:6.4, w:11.6, h:0.5, fontFace:SANS, fontSize:14, italic:true, color:C.body, margin:0 });

/* ---------- Slide 7 · real ---------- */
s = base(); footer(s, 7);
vmark(s, 0.7, 0.6, 0.4); eyebrow(s, "LIVE, NOT STAGED · COMPLETENESS", 1.25, 0.66);
s.addText("Everything is real — and nothing can break.", { x:0.7, y:1.25, w:11.9, h:0.7, fontFace:SANS, fontSize:30, bold:true, color:C.text, margin:0 });
const proofs = [
  ["Live web","Real Google SERP via Bright Data — fresh headlines for any company you type."],
  ["Live reasoning","Kimi K2 researches a company it has never seen and writes the thesis."],
  ["Real compute","The valuation model executes in a Daytona sandbox — not a hard-coded number."],
  ["Real perception","Earnings-call segments located by spoken-word search in VideoDB."],
  ["Real signature","Ed25519, DID-bound provenance via the Terminal 3 sidecar."],
];
proofs.forEach((pr,i)=>{ const y=2.3+i*0.72;
  s.addShape(p.shapes.OVAL, { x:0.74, y:y+0.06, w:0.15, h:0.15, fill:{color:C.green} });
  s.addText(pr[0], { x:1.08, y:y, w:2.9, h:0.4, fontFace:SANS, fontSize:15, bold:true, color:C.text, margin:0 });
  s.addText(pr[1], { x:4.0, y:y, w:8.4, h:0.5, fontFace:SANS, fontSize:14, color:C.muted, margin:0 });
});
s.addText([
  { text:"Degrade-and-continue:  ", options:{ color:C.green, bold:true } },
  { text:"if a key or the network fails, that stage falls back to cached data — so every run still reaches the signature.", options:{ color:C.body } },
], { x:0.72, y:6.15, w:11.7, h:0.6, fontFace:SANS, fontSize:14.5, italic:true, margin:0 });

/* ---------- Slide 8 · closing ---------- */
s = base();
vmark(s, 0.7, 0.66, 0.62);
s.addText("VERDICT", { x:1.5, y:0.62, w:6, h:0.5, fontFace:SANS, fontSize:24, bold:true, color:C.text, charSpacing:1, valign:"middle", margin:0 });
s.addText("● SEALED", { x:10.8, y:0.74, w:1.85, h:0.4, fontFace:MONO, fontSize:11, bold:true, color:C.green, align:"right", charSpacing:2, valign:"middle", margin:0 });
s.addText([
  { text:"Five stages. Eight platforms.", options:{ breakLine:true, color:C.text } },
  { text:"One signed, auditable decision —", options:{ breakLine:true, color:C.text } },
  { text:"in 90 seconds.", options:{ color:C.green } },
], { x:0.68, y:2.35, w:12, h:2.3, fontFace:SANS, fontSize:40, bold:true, lineSpacingMultiple:1.1, margin:0 });
s.addText("Verdict doesn't just read the web — it reasons, values, and then earns the right to act, with a signature you can take to your board.",
  { x:0.72, y:5.0, w:10.6, h:0.9, fontFace:SANS, fontSize:16, color:C.muted, lineSpacingMultiple:1.3, margin:0 });
s.addShape(p.shapes.LINE, { x:0.72, y:6.45, w:11.9, h:0, line:{color:C.line, width:1} });
s.addText("github.com/eugenewong22/verdict", { x:0.72, y:6.6, w:7, h:0.4, fontFace:MONO, fontSize:11, color:C.faint, valign:"middle", margin:0 });
s.addText("AGENT FORGE SG · 2026", { x:8.6, y:6.6, w:4, h:0.4, fontFace:MONO, fontSize:11, color:C.faint, align:"right", charSpacing:2, valign:"middle", margin:0 });

p.writeFile({ fileName: "/Users/eugene/verdict/Verdict_Pitch.pptx" }).then(f => console.log("WROTE", f));
