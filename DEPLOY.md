# Deploying SetsOfLove on Cloudflare

Everything runs on Cloudflare's free tier: Pages (site and API), D1 (database) and R2 (photos).

## One-time setup

Run these on your computer (needs Node 20+). Log in once with `npx wrangler login`.

1. **Create the database.** `npx wrangler d1 create setsoflove`
   Copy the `database_id` it prints into `wrangler.toml` (replace `REPLACE_WITH_D1_ID`) and commit.
2. **Create the photo bucket.** `npx wrangler r2 bucket create setsoflove-photos`
3. **Create the tables.** `npm install` then `npm run migrate:remote`
4. **Connect the repo.** Cloudflare dashboard, Workers & Pages, Create, Pages, Connect to Git, choose `setsoflove`.
   - Framework preset: None
   - Build command: leave empty
   - Build output directory: `public`
5. **Sign-ups are open.** No invite code is needed. If an old `SIGNUP_CODE` secret is set, you can delete it.
6. **Check the bindings.** Pages project, Settings, Bindings should show `DB` (D1 `setsoflove`) and `PHOTOS` (R2 `setsoflove-photos`). They come from `wrangler.toml`.
7. **Add your domain.** Pages project, Custom domains.

## Contact form and email

All site email goes to `contact@setsoflove.com` (`CONTACT_EMAIL` in `wrangler.toml`). It's used in every footer, the "Report this profile" link and the legal pages.

1. **Receive mail.** Cloudflare dashboard, your domain, Email, Email Routing. Enable it, then add a rule that forwards `contact@setsoflove.com` to your own inbox.
2. **Send form messages to that address.** Create a free Resend account, verify `setsoflove.com`, and create an API key. In the Pages project, Settings, Variables and Secrets, add a secret named `RESEND_API_KEY`. Redeploy.
3. **Add the table.** Run `npm run migrate:remote` (migration 0003).

Every message is saved in D1 even if email delivery fails. Read them with:

```
npx wrangler d1 execute setsoflove --remote --command "SELECT created_at, name, email, message, emailed FROM contact_messages ORDER BY id DESC LIMIT 20"
```

## Make yourself the admin

Create your own account on the site first, then run:

```
npx wrangler d1 execute setsoflove --remote --command "UPDATE users SET is_admin = 1 WHERE email = 'you@example.com'"
```

Sign in and you'll land on `/admin`, where every profile waits for approval.

## Day to day

- Every push to the main branch redeploys the site.
- Schema changes go in a new file in `migrations/`, then `npm run migrate:remote`.
- Local test run: put `SIGNUP_CODE=anything` in `.dev.vars`, then `npm run migrate:local` and `npx wrangler pages dev`.

## Blog publishing

`.github/workflows/publish-blog.yml` runs every 15 minutes, builds any blog post whose time has passed and commits `public/`. In the GitHub repo, Settings, Actions, General, set Workflow permissions to Read and write. See `BLOG.md`. Submit `https://setsoflove.com/sitemap.xml` in Google Search Console after the first posts go live.

## How it works

- Profile links sit at the root (`yoursite.com/sam-t`). Only approved profiles are visible, and they're marked noindex so search engines skip them. The homepage and blog are indexable.
- Editing a live profile (including its photos) takes it offline until you approve it again.
- Passwords are hashed with PBKDF2. Sessions are random tokens stored hashed in D1. Five wrong passwords lock an email for 15 minutes.
- Members are not emailed. They see their status, and any contact requests waiting, when they sign in.
