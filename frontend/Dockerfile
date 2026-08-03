# Frontend image packages a host-built Next.js standalone output.
# Build steps (from repo root):
#   cd frontend && npm run build
#   docker compose build frontend
#
# In-container `next build` is skipped because Docker Desktop on Windows
# often crashes during "Collecting page data".
FROM node:22-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
ENV PORT=8911
ENV NEXT_TELEMETRY_DISABLED=1

COPY frontend/public ./public
COPY frontend/.next/standalone ./
COPY frontend/.next/static ./.next/static
COPY README.md /app/README.md

RUN printf '%s\n' \
      "AI Healthcare Assistant frontend image" \
      "Docs: /app/README.md" \
      "UI: http://localhost:8911" \
      > /app/IMAGE_INFO.txt

EXPOSE 8911
CMD ["node", "server.js"]
