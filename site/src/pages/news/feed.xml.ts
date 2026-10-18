// The news feed (tracker pattern, rule 4.15): RSS, full text, the post's card as its picture.
import rss from '@astrojs/rss';
import MarkdownIt from 'markdown-it';
import type { APIContext } from 'astro';
import { allPosts, postPath, cardPath } from '../../lib/news';

const md = new MarkdownIt({ html: false, linkify: false });

export async function GET(context: APIContext) {
  const site = String(context.site).replace(/\/$/, '');
  const posts = await allPosts();
  return rss({
    title: 'Outrunning Ageing · News',
    description: 'What moved on the tree, and why: one post for each change a reader would want explained.',
    site: context.site!,
    items: posts.map((p) => ({
      title: p.data.title,
      pubDate: new Date(p.data.date + 'T12:00:00Z'),
      description: p.data.summary,
      link: postPath(p),
      content: md.render(p.body ?? ''),
      enclosure: { url: site + cardPath(p), type: 'image/png', length: 0 },
    })),
    customData: '<language>en-gb</language>',
  });
}
