# Instagram auto-posting (free)

Posts are scheduled in `social/queue.json`. A free GitHub job (`.github/workflows/instagram.yml`) runs
every 15 minutes and publishes whatever is due through Instagram's official API, then records it in
`social/posted.json` with its Instagram link. Media files live in `site/social/` so they're public on
theartfulproducts.com (Instagram downloads them from there). That folder is hidden from Google.

## A queue entry
```json
{ "id": "himalayan-frames-1", "type": "carousel", "publish_at": "2026-11-25 18:30",
  "media": ["social/2026-11/himalayan-1.jpg", "social/2026-11/himalayan-2.jpg"],
  "caption": "Podium frames for The Great Himalayan…\n\n#3dprinting #cycling" }
```
- `type`: `image` (1 JPEG) · `carousel` (2–10 JPEGs/MP4s) · `reel` (1 MP4, vertical 9:16). Optional `cover_at_ms` for a reel cover.
- `publish_at`: India time. GitHub's schedule can run up to ~15–30 minutes late.
- `"hold": true` keeps a post queued without publishing.
- Images: JPEG, aspect between 4:5 (portrait) and 1.91:1. Captions ≤ 2,200 characters, ≤ 30 hashtags.
- Stories can't be posted through the API.

Commands: `python tools/ig_publish.py --check` (validate) · `--dry-run` (preview what's due) ·
tests: `python tools/test_ig_publish.py` (fake Instagram, never the real account).
After changing the queue: commit and `python tools/publish.py` (media goes live with the website deploy).

## One-time setup (Meta side)
1. **Instagram → Professional account**: Instagram app → Settings → *Account type and tools* → *Switch to professional account* → Business.
2. **Facebook Page linked to it**: create a Page "The Artful Products" (facebook.com/pages/create) and link the
   Instagram account (Page → Settings → *Linked accounts* → Instagram, or in Instagram: Edit profile → Page).
3. **Meta developer app**: developers.facebook.com (same Facebook login) → *My Apps* → *Create App* → a Business-type
   app, e.g. "Artful Poster". It stays in development mode; that's fine for posting to your own account.
4. **Token**: *Tools → Graph API Explorer* → choose the app → *Get User Access Token* with permissions
   `pages_show_list`, `pages_read_engagement`, `instagram_basic`, `instagram_content_publish`, `business_management`
   → allow your Page and Instagram account.
5. **Make it long-lived**: *Tools → Access Token Debugger* → paste the token → *Debug* → *Extend Access Token* → copy it.
6. **Page token (doesn't expire)**: back in Graph API Explorer, paste the long-lived token, run `me/accounts`, and copy
   your Page's `access_token`. Check it in the Access Token Debugger: *Expires: Never*.
7. **GitHub**: repo → *Settings → Secrets and variables → Actions* → *New repository secret* → name `IG_PAGE_TOKEN`,
   value = that Page token. Never paste it in chat or files.
8. Test: GitHub → *Actions* → *Instagram posts* → *Run workflow* with *dry run* ticked.

If the token stops working (password change, removed permissions, Page unlinked), repeat steps 4–7.
Note: GitHub pauses scheduled jobs in a repository with no activity for 60 days; any push re-enables them.
