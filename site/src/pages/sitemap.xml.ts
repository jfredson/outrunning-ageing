// The sitemap at /sitemap.xml, built from the same export every page reads, the way the sister
// sites build theirs (upgrade-tree and quiet-galaxy, site/src/pages/sitemap.xml.ts). Every public
// page at its stable address, nothing else: the fixed pages, one page per branch, one per treatment
// or measuring tool (a leaf), one per news post. Left out: the not-found page (noindex), and
// /method/ and /story/, which have been redirects to /about/ since 2026-10-21 and carry noindex.
// Added 2026-10-31, when a search for the family's sites by name found this site missing from
// Google's first page for its own name and serving no sitemap.
import type { APIRoute } from 'astro';
import { records } from '../lib/records';
import { allPosts, postPath } from '../lib/news';

const FIXED = ['/', '/branches/', '/claims/', '/self-experiments/', '/reading/', '/news/', '/about/', '/disagree/'];

export const GET: APIRoute = async ({ site }) => {
  const posts = await allPosts();
  const urls: { loc: string; lastmod?: string }[] = [
    ...FIXED.map((p) => ({ loc: p })),
    ...records.branches.map((b) => ({ loc: b.path })),
    ...records.leaves.map((l) => ({ loc: l.path })),
    ...posts.map((p) => ({ loc: postPath(p), lastmod: p.data.date })),
  ];
  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urls
  .map((u) => `<url><loc>${new URL(u.loc, site).href}</loc>${u.lastmod ? `<lastmod>${u.lastmod}</lastmod>` : ''}</url>`)
  .join('\n')}
</urlset>
`;
  return new Response(xml, { headers: { 'Content-Type': 'application/xml; charset=utf-8' } });
};
