// The one piece of code that runs in front of the static site (2026-10-16, copied from The Quiet
// Galaxy's site/worker/redirect.js). Every request passes through here first. If it arrived at an
// address other than outrunningageing.com (www, or the American-spelled forwarding address
// outrunningaging.com), it is sent to the same page at outrunningageing.com with a permanent
// redirect. The workers.dev preview address is left alone so a preview can be looked at before
// the domain shows it. Everything else is served from the built site in dist/ as it is.
const CANONICAL = 'outrunningageing.com';

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const host = url.hostname;
    if (host !== CANONICAL && !host.endsWith('.workers.dev') && host !== 'localhost') {
      url.hostname = CANONICAL;
      url.protocol = 'https:';
      url.port = '';
      return Response.redirect(url.toString(), 301);
    }
    return env.ASSETS.fetch(request);
  },
};
