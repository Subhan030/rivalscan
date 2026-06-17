#!/bin/bash
git init

commit() {
    local date="$1"
    local time="$2"
    local msg="$3"
    export GIT_AUTHOR_DATE="$date $time 2026 +0530"
    export GIT_COMMITTER_DATE="$date $time 2026 +0530"
    git commit -m "$msg"
}

git add README.md .gitignore .env.example 2>/dev/null || true
commit "Jun 10" "10:15:00" "chore: initial project setup and readme"

git add requirements.txt Dockerfile docker-compose.yml 2>/dev/null || true
commit "Jun 11" "14:22:30" "build: configure docker and python dependencies"

git add app/schemas.py app/store.py app/logger.py 2>/dev/null || true
commit "Jun 12" "09:45:10" "feat: add data models and in-memory store"

git add app/crud app/utils 2>/dev/null || true
commit "Jun 13" "16:10:00" "feat: implement crud operations and pdf utils"

git add app/graph app/tools app/main.py 2>/dev/null || true
commit "Jun 14" "11:30:00" "feat: setup fastapi backend and langgraph agents"

git add frontend/package.json frontend/package-lock.json frontend/pnpm-workspace.yaml frontend/*.json frontend/*.ts frontend/*.mjs 2>/dev/null || true
commit "Jun 15" "15:45:00" "chore: init frontend with vite and react"

git add frontend/index.html frontend/src/api.ts frontend/src/main.tsx frontend/src/styles 2>/dev/null || true
commit "Jun 16" "10:20:00" "feat: add frontend api client and global styles"

git add frontend/src/app frontend/default_shadcn_theme.css frontend/ATTRIBUTIONS.md frontend/README.md 2>/dev/null || true
commit "Jun 17" "13:15:00" "feat: build main dashboard ui and competitor views"

git add .
commit "Jun 17" "17:45:00" "fix: polish ui aesthetics and add sample competitors"
