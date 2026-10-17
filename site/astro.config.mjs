import { defineConfig } from 'astro/config';

// Same generator and settings as the sister sites (The Quiet Galaxy, The Upgrade Tree, The Belt
// Equation): a fully static build in dist/, served from Cloudflare Workers static assets.
export default defineConfig({
  site: 'https://outrunningageing.com',
  trailingSlash: 'always',
});
