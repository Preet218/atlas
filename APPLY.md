1. Copy src/atlas/database into your project.
2. Copy docker-compose.yml to repo root.
3. Copy database.py into src/atlas/api/routes.
4. Modify main.py as described in PATCH_main.py.txt.
5. Run:
   docker compose up -d
   uv run uvicorn --app-dir src atlas.api.main:app --reload
6. Visit:
   /health
   /health/db
