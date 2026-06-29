# Deploying Debear (API + bot) to Fly.io

This deploys ONE image as two process groups — `web` (FastAPI API) and `bot`
(Telegram bot) — plus a managed PostgreSQL database. Result: a stable public
URL like `https://<your-app>.fly.dev` that works 24/7, independent of your PC.

## Prerequisites
- A Fly.io account (sign up at https://fly.io — card required for verification,
  free allowance applies).
- `flyctl` installed (this repo installs it to `~/.fly/bin/flyctl.exe`; or get
  it from https://fly.io/docs/flyctl/install/).

> In the commands below, replace `debear-insurance` with YOUR unique app name
> (the name must be globally unique on Fly). Update the `app = "..."` line in
> `fly.toml` to match.

## Steps (run from the project root `UpWork_TG`)

```powershell
# 0. Make flyctl available in this shell
$env:Path += ";$env:USERPROFILE\.fly\bin"

# 1. Log in
fly auth login

# 2. Create the app (pick a unique name, then set the same name in fly.toml)
fly apps create debear-insurance

# 3. Create a managed Postgres and attach it (sets the DATABASE_URL secret)
fly postgres create --name debear-db --region fra --initial-cluster-size 1 --vm-size shared-cpu-1x --volume-size 1
fly postgres attach debear-db -a debear-insurance

# 4. Set the bot secrets
fly secrets set BOT_TOKEN="<your-bot-token-from-BotFather>" -a debear-insurance
fly secrets set ADMIN_IDS="<your-telegram-id>" -a debear-insurance

# 5. Deploy
fly deploy -a debear-insurance
```

## After deploy

1. Your API is at `https://debear-insurance.fly.dev`
   - check: open `https://debear-insurance.fly.dev/docs`
2. **Point the mobile app at it** (stable, no more tunnel):
   - edit `mobile/app.json` → `expo.extra.apiUrl` =
     `https://debear-insurance.fly.dev`
   - rebuild the APK: `cd mobile && eas build -p android --profile preview`
3. You can now **stop the local stuff** on your PC — it's no longer needed:
   - the local bot (`run.py`), the local API (`uvicorn`), and `cloudflared`.

## ⚠️ Only one bot can poll a token at a time
The Telegram token can be polled by exactly one process. Before/while the Fly
bot runs, **stop the local `run.py`** or Telegram will return HTTP 409
(conflict). Use the Fly bot OR the local one — not both.

## Useful commands
```powershell
fly logs -a debear-insurance              # live logs (both processes)
fly status -a debear-insurance            # machines / health
fly secrets list -a debear-insurance
fly deploy -a debear-insurance            # redeploy after code changes
```

## Notes
- Tables are created automatically on first boot (`init_models`).
- The bot uses long polling (no webhook needed). The `bot` process group keeps
  one machine always running.
- For lowest latency to Russia/CIS users, `primary_region = "fra"` (Frankfurt)
  is a good default; change it in `fly.toml` if you prefer another region.
