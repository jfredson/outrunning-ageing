#!/usr/bin/env node
// Renders the site's icon set from the one source, site/public/favicon.svg, the way the parent does
// (sentient-horizons/site/scripts/icons.mjs; the design standard's shell rule, 2026-10-18). Writes favicon-16.png, favicon-32.png,
// apple-touch-icon.png (180), icon-192.png, icon-512.png and favicon.ico (16, 32 and 48, PNG-encoded
// inside the .ico container, which every current browser reads). Run from the repository root after changing the SVG:
//   node scripts/icons.mjs
// The fonts are this Mac's , so the set is rendered here and committed, never at deploy.
import { createRequire } from 'node:module';
import { readFile, writeFile } from 'node:fs/promises';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
const sharp = createRequire(new URL('../site/', import.meta.url))('sharp');
// With no arguments it renders this site's set from site/public/favicon.svg. With two, it renders any
// site's: node scripts/icons.mjs <favicon.svg> <output folder>  (the trackers' sets were first rendered
// this way on 2026-10-18; each Astro tracker also carries a copy of this script beside its own).
const [argSvg, argOut] = process.argv.slice(2);
const pub = argOut ? argOut : join(dirname(fileURLToPath(import.meta.url)), '..', 'site', 'public');
const svg = await readFile(argSvg ? argSvg : join(pub, 'favicon.svg'));
const render = (size) => sharp(svg, { density: 72 * (size / 64) }).resize(size, size).png({ compressionLevel: 9 }).toBuffer();
for (const [name, size] of [['favicon-16.png', 16], ['favicon-32.png', 32], ['apple-touch-icon.png', 180], ['icon-192.png', 192], ['icon-512.png', 512]]) {
  await writeFile(join(pub, name), await render(size));
}
// favicon.ico: an ICO directory whose entries are PNG images.
const sizes = [16, 32, 48];
const pngs = await Promise.all(sizes.map(render));
const header = Buffer.alloc(6); header.writeUInt16LE(0, 0); header.writeUInt16LE(1, 2); header.writeUInt16LE(sizes.length, 4);
const dir = Buffer.alloc(16 * sizes.length);
let offset = 6 + dir.length;
sizes.forEach((s, i) => {
  const e = i * 16;
  dir.writeUInt8(s === 256 ? 0 : s, e); dir.writeUInt8(s === 256 ? 0 : s, e + 1); dir.writeUInt8(0, e + 2); dir.writeUInt8(0, e + 3);
  dir.writeUInt16LE(1, e + 4); dir.writeUInt16LE(32, e + 6); dir.writeUInt32LE(pngs[i].length, e + 8); dir.writeUInt32LE(offset, e + 12);
  offset += pngs[i].length;
});
await writeFile(join(pub, 'favicon.ico'), Buffer.concat([header, dir, ...pngs]));
console.log(`icon set rendered into ${pub}: 16, 32, 180, 192, 512 and favicon.ico (16, 32, 48)`);
