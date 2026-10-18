// Makes the social preview image, site/public/social-preview.png (1200 by 630): what link previews
// on iMessage, Slack, X, Reddit and the rest show when Outrunning Ageing is shared. Drawn in the "Ledger" skin's own
// tokens (site/src/styles/skin.css), carrying the site's name, the question from its home page and its
// address; no stock picture. The proposed rule is design/tracker-pattern.md in sentient-horizons.
//
// Run from the repository root after changing the skin or the home-page question:
//   node scripts/social-image.mjs
// It needs `sharp`, which Astro already installs in site/node_modules (run `npm ci` in site/ first).
// The picture is the same every time it is made; the only inputs are the values written below.
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';

const require = createRequire(new URL('../site/', import.meta.url));
const sharp = require('sharp');

const W = 1200;
const H = 630;
const SANS = "'Helvetica Neue', Helvetica, Arial, sans-serif";
const MONO = "Menlo, 'SF Mono', Consolas, monospace";

// A small deterministic generator, so the picture is the same every time it is made.
function rng(seed) {
  let s = seed >>> 0;
  return () => {
    s = (Math.imul(s, 1664525) + 1013904223) >>> 0;
    return s / 4294967296;
  };
}

function textBlock({ lines, x, y, size, lead, fill, weight = 600, spacing = -1 }) {
  return lines
    .map(
      (t, i) =>
        `<text x="${x}" y="${y + i * lead}" font-family="${SANS}" font-size="${size}" font-weight="${weight}" letter-spacing="${spacing}" fill="${fill}">${t}</text>`,
    )
    .join('\n');
}

function nameLine({ name, x, y, fill }) {
  return `<text x="${x}" y="${y}" font-family="${SANS}" font-size="28" font-weight="600" letter-spacing="5" fill="${fill}">${name.toUpperCase()}</text>`;
}

function domainLine({ domain, x, y, fill }) {
  return `<text x="${x}" y="${y}" font-family="${MONO}" font-size="26" fill="${fill}">${domain}</text>`;
}

function wrap(body) {
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">\n${body}\n</svg>\n`;
}

function buildLedger() {
  const bg = '#f3eee3', text = '#1c1a16', soft = '#3a362f', muted = '#6e675b', accent = '#2b5c8a', sepia = '#8a5a2b', lineStrong = 'rgba(28,26,22,0.24)';
  // The chart's axis, the way Spread.astro draws it: years 2040 to 2100 along a rule, and the
  // dashed rule in the second mark at 2050, the year the loudest promises name. No bars are drawn
  // and no figure is claimed; the live chart is on the site.
  const L = 72, R = W - 72, base = 520;
  const X = (y) => L + ((y - 2040) / 60) * (R - L);
  let ticks = '';
  for (let y = 2040; y <= 2100; y += 10) {
    ticks += `<line x1="${X(y)}" x2="${X(y)}" y1="${base}" y2="${base + 8}" stroke="${muted}" stroke-width="1.4"/><text x="${X(y)}" y="${base + 34}" text-anchor="middle" font-family="${SANS}" font-size="20" fill="${muted}">${y}</text>`;
  }
  return wrap(`<rect width="${W}" height="${H}" fill="${bg}"/>
<g stroke="${lineStrong}" stroke-width="1"><line x1="72" x2="${W - 72}" y1="40" y2="40"/><line x1="72" x2="${W - 72}" y1="45" y2="45"/><line x1="72" x2="${W - 72}" y1="${H - 45}" y2="${H - 45}"/><line x1="72" x2="${W - 72}" y1="${H - 40}" y2="${H - 40}"/></g>
<line x1="${X(2050)}" x2="${X(2050)}" y1="390" y2="${base}" stroke="${sepia}" stroke-width="2.5" stroke-dasharray="7 7"/>
<line x1="${L}" x2="${R}" y1="${base}" y2="${base}" stroke="${soft}" stroke-width="1.6"/>
${ticks}
${nameLine({ name: 'Outrunning Ageing', x: 72, y: 116, fill: accent })}
${textBlock({ lines: ['When do we start', 'outrunning ageing?'], x: 72, y: 232, size: 84, lead: 98, fill: text, spacing: -1.5 })}
<text x="${W - 72}" y="116" text-anchor="end" font-family="${MONO}" font-size="26" fill="${muted}">outrunningageing.com</text>`);
}

// ---- the news posts' cards (tracker pattern, rule 4.15; John 2026-10-18) ----------------------------
// `node scripts/social-image.mjs --posts [file ...]` draws one card per post in site/src/content/news/
// (or the files named) to site/public/news/<slug>-card.png: the site's name line, the post's title as
// the statement, a kicker of News · the date · the kind, and the `before` and `after` lines from the
// frontmatter as the numbers that moved. Drawn here and committed, never at deploy.
import { readdirSync, readFileSync, mkdirSync } from 'node:fs';
import { basename, join, dirname } from 'node:path';

const KIND_LABEL = { 'start-here': 'start here', 'rung-reached': 'a rung reached', 'estimate-revised': 'an estimate revised', 'flagged-item-ruled': 'a flagged item ruled', 'claim': 'a claim added or settled', 'headline-moved': 'the headline moved', 'method-changed': 'the method changed' };
function fm(text) { const m = text.match(/^---\n([\s\S]*?)\n---/); const d = {}; if (!m) return d; for (const line of m[1].split('\n')) { const k = line.match(/^([a-z_]+):\s*(.*)$/); if (k) d[k[1]] = k[2].trim().replace(/^"|"$/g, ''); } return d; }
function longDate(iso) { const d = new Date(iso + 'T12:00:00Z'); return `${d.getUTCDate()} ${d.toLocaleString('en-GB', { month: 'long', timeZone: 'UTC' })} ${d.getUTCFullYear()}`; }
function wrapWords(text, max) { const lines = []; let cur = ''; for (const w of text.split(/\s+/)) { const t = (cur + ' ' + w).trim(); if (t.length <= max) cur = t; else { lines.push(cur); cur = w; } } if (cur) lines.push(cur); return lines; }
function buildPostCard(post) {
  const bg = '#f3eee3', text = '#1c1a16', soft = '#3a362f', muted = '#6e675b', accent = '#2b5c8a', sepia = '#8a5a2b', lineStrong = 'rgba(28,26,22,0.24)';
  let lines = wrapWords(post.title, 30); let size = 56, lead = 68;
  if (lines.length > 3) { lines = wrapWords(post.title, 38); size = 46; lead = 56; }
  lines = lines.slice(0, 4);
  const kicker = `NEWS · ${longDate(post.date).toUpperCase()} · ${(KIND_LABEL[post.kind] || post.kind).toUpperCase()}`;
  const numbersText = post.before && post.after ? `${post.before} to ${post.after}` : (post.after || '');
  const numbers = wrapWords(numbersText, 74).slice(0, 2);
  const esc = (t) => t.replace(/&/g, '&amp;').replace(/</g, '&lt;');
  return wrap(`<rect width="${W}" height="${H}" fill="${bg}"/>
<g stroke="${lineStrong}" stroke-width="1"><line x1="72" x2="${W - 72}" y1="40" y2="40"/><line x1="72" x2="${W - 72}" y1="45" y2="45"/><line x1="72" x2="${W - 72}" y1="${H - 45}" y2="${H - 45}"/><line x1="72" x2="${W - 72}" y1="${H - 40}" y2="${H - 40}"/></g>
${nameLine({ name: 'Outrunning Ageing', x: 72, y: 116, fill: accent })}
<text x="${W - 72}" y="116" text-anchor="end" font-family="${MONO}" font-size="26" fill="${muted}">outrunningageing.com</text>
${textBlock({ lines: lines.map(esc), x: 72, y: 232, size, lead, fill: text, spacing: -1 })}
<text x="72" y="${H - 132}" font-family="${SANS}" font-size="20" font-weight="600" letter-spacing="2" fill="${sepia}">${esc(kicker)}</text>
${numbers.map((ln, i) => `<text x="72" y="${H - 96 + i * 32}" font-family="${SANS}" font-size="24" fill="${soft}">${esc(ln)}</text>`).join('')}`);
}
const argv = process.argv.slice(2);
if (argv[0] === '--posts') {
  const dir = fileURLToPath(new URL('../site/src/content/news/', import.meta.url));
  const outDir = fileURLToPath(new URL('../site/public/news/', import.meta.url)); mkdirSync(outDir, { recursive: true });
  const files = argv.length > 1 ? argv.slice(1).map((f) => basename(f)) : readdirSync(dir).filter((f) => f.endsWith('.md'));
  for (const f of files) {
    const post = fm(readFileSync(join(dir, f), 'utf8')); const slug = f.replace(/\.md$/, '');
    await sharp(Buffer.from(buildPostCard(post))).png({ compressionLevel: 9 }).toFile(join(outDir, `${slug}-card.png`));
    console.log('wrote', join(outDir, `${slug}-card.png`));
  }
} else {
  const out = fileURLToPath(new URL('../site/public/social-preview.png', import.meta.url));
  await sharp(Buffer.from(buildLedger())).png({ compressionLevel: 9 }).toFile(out);
  console.log('wrote', out);
}
