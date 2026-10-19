#!/usr/bin/env bash
# Loads the 20 made-up sample profiles into the LOCAL database and local photo storage.
# Never run this against the live site: there is no --remote here on purpose.
# Then start the app with: npm run dev:samples
set -euo pipefail
cd "$(dirname "$0")/.."
python3 scripts/build_avatars.py
python3 scripts/build_sample_seed.py
npx wrangler d1 migrations apply setsoflove --local
npx wrangler d1 execute setsoflove --local --file seed/sample-profiles.sql
for f in public/img/avatars/*.svg; do
  id="sample-$(basename "$f" .svg)"
  npx wrangler r2 object put "setsoflove-photos/photos/$id" --file "$f" --content-type image/svg+xml --local
done
echo "Done. Run: npm run dev:samples"
