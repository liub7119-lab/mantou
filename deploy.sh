#!/usr/bin/env bash
set -euo pipefail

SERVER="${DEPLOY_SERVER:-134.175.189.40}"
USER="${DEPLOY_USER:-ubuntu}"
PASSWORD="${DEPLOY_PASSWORD:?请设置环境变量 DEPLOY_PASSWORD}"
APP_DIR="${APP_DIR:-/var/www/counselor-platform}"
WEB_ROOT="${WEB_ROOT:-/var/www/counselor-platform/frontend/dist}"

SSH_OPTS=(-o StrictHostKeyChecking=no -o PubkeyAuthentication=no -o PreferredAuthentications=password -o ConnectTimeout=20)

run_remote() {
  sshpass -p "${PASSWORD}" ssh "${SSH_OPTS[@]}" -p "${SSH_PORT:-22}" "${USER}@${SERVER}" "$@"
}

echo "==> 同步代码到服务器"
sshpass -p "${PASSWORD}" rsync -az --delete \
  --exclude node_modules --exclude .git --exclude backend/data --exclude backend/uploads \
  --exclude frontend/dist --exclude .env \
  -e "ssh ${SSH_OPTS[*]}" \
  ./ "${USER}@${SERVER}:${APP_DIR}/"

echo "==> 安装后端依赖"
run_remote "cd ${APP_DIR}/backend && source venv/bin/activate && pip install -r requirements.txt -q"

echo "==> 构建前端"
run_remote "cd ${APP_DIR}/frontend && npm install --silent && npm run build"

echo "==> 重启后端"
run_remote "sudo systemctl restart counselor-platform 2>/dev/null || \
  (pkill -f 'uvicorn app.main:app' || true; sleep 1; \
   cd ${APP_DIR}/backend && source venv/bin/activate && \
   nohup uvicorn app.main:app --host 127.0.0.1 --port 8000 > /tmp/counselor-api.log 2>&1 &)"

echo "==> 重载 Nginx"
run_remote "sudo nginx -t && sudo systemctl reload nginx"

echo "==> 验证"
curl -s "http://${SERVER}/api/v1/attendance/calendar" || true
echo
echo "部署完成"
