// Helpers for the news section (tracker pattern, rules 4.10 to 4.16).
import { getCollection, type CollectionEntry } from 'astro:content';

export type Post = CollectionEntry<'news'>;

export const KIND_LABEL: Record<string, string> = {
  'start-here': 'start here',
  'rung-reached': 'a rung reached',
  'estimate-revised': 'an estimate revised',
  'flagged-item-ruled': 'a flagged item ruled',
  'claim': 'a claim added or settled',
  'headline-moved': 'the headline moved',
  'method-changed': 'the method changed',
};

export const postPath = (p: Post) => `/news/${p.id}/`;
export const cardPath = (p: Post) => `/news/${p.id}-card.png`;

/** Every post, newest first; the opener is excluded unless asked for. */
export async function allPosts(): Promise<Post[]> {
  const posts = await getCollection('news');
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
