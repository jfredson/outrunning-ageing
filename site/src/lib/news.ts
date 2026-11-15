// Helpers for the news section (tracker pattern, rules 4.10 to 4.16).
import { getCollection, type CollectionEntry } from 'astro:content';

export type Post = CollectionEntry<'news'>;

export const KIND_LABEL: Record<string, string> = {
  'start-here': 'start here',
  'rung-reached': 'a new stage reached',
  'estimate-revised': 'an estimate revised',
  'flagged-item-ruled': 'a flagged item ruled',
  'claim': 'a claim added or settled',
  'headline-moved': 'the headline moved',
  'method-changed': 'the method changed',
  'story': 'a story from the field',
  'year-in-review': 'the year in review',
};

export const postPath = (p: Post) => `/news/${p.id}/`;
export const cardPath = (p: Post) => `/news/${p.id}-card.png`;

/** The build's own date on the site's clock (Pacific), as YYYY-MM-DD; NEWS_BUILD_DATE overrides it, to preview a held post. */
export const BUILD_DATE = process.env.NEWS_BUILD_DATE || new Intl.DateTimeFormat('en-CA', { timeZone: 'America/Los_Angeles', year: 'numeric', month: '2-digit', day: '2-digit' }).format(new Date());

/** Every post dated on or before the build's date, newest first; the opener is excluded unless asked
 * for. A post dated later (a draft held for its publishing day, such as a year in review) is left out
 * of every page, list, feed and the sitemap until a build on or after its date. */
export async function allPosts(): Promise<Post[]> {
  const posts = (await getCollection('news')).filter((p) => p.data.date <= BUILD_DATE);
  return posts.sort((a, b) => (a.data.date < b.data.date ? 1 : a.data.date > b.data.date ? -1 : a.id < b.id ? 1 : -1));
}
export async function datedPosts(): Promise<Post[]> {
  return (await allPosts()).filter((p) => p.data.kind !== 'start-here');
}
export async function opener(): Promise<Post | null> {
  return (await allPosts()).find((p) => p.data.kind === 'start-here') ?? null;
}
/** The posts that name a record (rule 4.14: the back link is computed here, never written into the record). */
export async function postsAbout(recordId: string): Promise<Post[]> {
  return (await datedPosts()).filter((p) => p.data.records.includes(recordId));
}
/** The posts of one date, for the story page's day line and the reading's resolved items. */
export async function postsOn(date: string): Promise<Post[]> {
  return (await datedPosts()).filter((p) => p.data.date === date || p.data.reading === date);
}
export function wordCount(body: string | undefined): number {
  return (body ?? '').split(/\s+/).filter(Boolean).length;
}
