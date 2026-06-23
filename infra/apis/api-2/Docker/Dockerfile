FROM node:20-alpine AS builder

WORKDIR /app
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ ./
ARG VITE_BACKEND_URL=
ARG VITE_GOOGLE_CLIENT_ID=
ARG VITE_GOOGLE_API_KEY=
ENV VITE_BACKEND_URL=${VITE_BACKEND_URL} \
    VITE_GOOGLE_CLIENT_ID=${VITE_GOOGLE_CLIENT_ID} \
    VITE_GOOGLE_API_KEY=${VITE_GOOGLE_API_KEY}

RUN npm run build

FROM nginx:1.27-alpine AS runtime

COPY infra/apis/api-2/Docker/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /app/dist /usr/share/nginx/html
COPY infra/apis/api-2/Docker/docker-entrypoint.sh /docker-entrypoint.sh

RUN sed -i 's/\r$//' /docker-entrypoint.sh && chmod +x /docker-entrypoint.sh

ENV BACKEND_URL=

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget -qO- http://127.0.0.1/ >/dev/null || exit 1

ENTRYPOINT ["/docker-entrypoint.sh"]
