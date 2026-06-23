#!/bin/sh
set -eu

RUNTIME_CONFIG_PATH="/usr/share/nginx/html/runtime-config.js"

cat > "${RUNTIME_CONFIG_PATH}" <<EOF
window.__RUNTIME_CONFIG__ = {
  backendUrl: '${BACKEND_URL:-}',
};
EOF

exec nginx -g 'daemon off;'
