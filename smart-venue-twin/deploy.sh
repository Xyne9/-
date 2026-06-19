#!/usr/bin/env bash
# ============================================================
# 智慧场馆数字孪生平台 - 生产部署脚本
# 功能：构建前端、配置Nginx、启动Gunicorn后端、创建systemd服务
# ============================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 项目配置
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_NAME="smart-venue-twin"
BACKEND_DIR="${PROJECT_DIR}/backend"
FRONTEND_DIR="${PROJECT_DIR}/frontend"
DATA_DIR="${PROJECT_DIR}/data"
VENV_DIR="${BACKEND_DIR}/venv"

# 部署配置
DEPLOY_USER="${DEPLOY_USER:-www-data}"
DEPLOY_DIR="${DEPLOY_DIR:-/opt/${PROJECT_NAME}}"
NGINX_CONF_DIR="/etc/nginx/sites-available"
NGINX_ENABLED_DIR="/etc/nginx/sites-enabled"
SYSTEMD_DIR="/etc/systemd/system"

# 服务器域名（可通过环境变量覆盖）
SERVER_NAME="${SERVER_NAME:-localhost}"
BACKEND_PORT="${BACKEND_PORT:-8000}"
FRONTEND_PORT="${FRONTEND_PORT:-80}"

info()  { echo -e "${BLUE}[信息]${NC} $1"; }
ok()    { echo -e "${GREEN}[成功]${NC} $1"; }
warn()  { echo -e "${YELLOW}[警告]${NC} $1"; }
error() { echo -e "${RED}[错误]${NC} $1"; }

# ============================================================
# 1. 检查运行环境
# ============================================================
info "检查部署环境..."

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
    warn "部分操作需要root权限，将使用sudo执行"
    SUDO="sudo"
else
    SUDO=""
fi

# 检查必要工具
for cmd in python3 node npm nginx; do
    if ! command -v "$cmd" &>/dev/null; then
        error "未找到 ${cmd}，请先安装"
        exit 1
    fi
done
ok "环境检查通过"

# ============================================================
# 2. 安装 gunicorn
# ============================================================
info "检查 gunicorn..."
if [ ! -d "${VENV_DIR}" ]; then
    python3 -m venv "${VENV_DIR}"
fi
source "${VENV_DIR}/bin/activate"
pip install --quiet --upgrade pip
pip install --quiet -r "${BACKEND_DIR}/requirements.txt"
pip install --quiet gunicorn
ok "gunicorn 安装完成"

# ============================================================
# 3. 生成和清洗数据
# ============================================================
RAW_DATA_DIR="${DATA_DIR}/raw"
if [ ! -d "${RAW_DATA_DIR}" ] || [ -z "$(ls -A "${RAW_DATA_DIR}" 2>/dev/null)" ]; then
    info "正在生成模拟数据..."
    python3 "${DATA_DIR}/generate_data.py"
    ok "数据生成完成"
fi

if [ -f "${DATA_DIR}/clean_data.py" ]; then
    info "正在清洗数据..."
    python3 "${DATA_DIR}/clean_data.py"
    ok "数据清洗完成"
fi

# ============================================================
# 4. 构建前端
# ============================================================
info "正在构建前端生产版本..."
cd "${FRONTEND_DIR}"
npm install --silent 2>/dev/null || npm install
npm run build
ok "前端构建完成: ${FRONTEND_DIR}/dist"

# ============================================================
# 5. 部署文件到目标目录
# ============================================================
info "正在部署文件到 ${DEPLOY_DIR}..."
${SUDO} mkdir -p "${DEPLOY_DIR}"

# 复制后端代码
${SUDO} rsync -a --exclude='__pycache__' --exclude='venv' "${BACKEND_DIR}/" "${DEPLOY_DIR}/backend/"

# 复制前端构建产物
${SUDO} mkdir -p "${DEPLOY_DIR}/frontend/dist"
${SUDO} rsync -a "${FRONTEND_DIR}/dist/" "${DEPLOY_DIR}/frontend/dist/"

# 复制数据文件
${SUDO} mkdir -p "${DEPLOY_DIR}/data"
${SUDO} rsync -a "${DATA_DIR}/" "${DEPLOY_DIR}/data/"

# 设置权限
${SUDO} chown -R "${DEPLOY_USER}:${DEPLOY_USER}" "${DEPLOY_DIR}"
ok "文件部署完成"

# ============================================================
# 6. 配置 Nginx
# ============================================================
info "正在配置 Nginx..."

${SUDO} mkdir -p "${NGINX_CONF_DIR}" "${NGINX_ENABLED_DIR}"

# 生成 Nginx 站点配置
${SUDO} tee "${NGINX_CONF_DIR}/${PROJECT_NAME}" > /dev/null <<NGINX_EOF
# 智慧场馆数字孪生平台 - Nginx 站点配置
server {
    listen ${FRONTEND_PORT};
    server_name ${SERVER_NAME};

    # 前端静态文件
    root ${DEPLOY_DIR}/frontend/dist;
    index index.html;

    # Gzip 压缩
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_min_length 256;
    gzip_types text/plain text/css text/xml text/javascript
               application/json application/javascript application/xml
               image/svg+xml font/opentype font/ttf font/woff font/woff2;

    # API 反向代理
    location /api/ {
        proxy_pass http://127.0.0.1:${BACKEND_PORT}/api/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # WebSocket 代理
    location /ws {
        proxy_pass http://127.0.0.1:${BACKEND_PORT}/ws;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_connect_timeout 7d;
        proxy_send_timeout 7d;
        proxy_read_timeout 7d;
    }

    # 健康检查
    location /health {
        proxy_pass http://127.0.0.1:${BACKEND_PORT}/health;
    }

    # API 文档
    location /docs {
        proxy_pass http://127.0.0.1:${BACKEND_PORT}/docs;
    }

    location /openapi.json {
        proxy_pass http://127.0.0.1:${BACKEND_PORT}/openapi.json;
    }

    # Vue SPA 路由
    location / {
        try_files \$uri \$uri/ /index.html;
    }

    # 静态资源缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
NGINX_EOF

# 启用站点配置
${SUDO} ln -sf "${NGINX_CONF_DIR}/${PROJECT_NAME}" "${NGINX_ENABLED_DIR}/${PROJECT_NAME}"

# 测试 Nginx 配置
${SUDO} nginx -t
ok "Nginx 配置完成"

# ============================================================
# 7. 创建 systemd 服务文件（可选）
# ============================================================
info "正在创建 systemd 服务文件..."

${SUDO} tee "${SYSTEMD_DIR}/${PROJECT_NAME}-backend.service" > /dev/null <<SYSTEMD_EOF
# 智慧场馆数字孪生平台 - 后端服务
[Unit]
Description=Smart Venue Twin Backend (FastAPI + Gunicorn)
After=network.target

[Service]
Type=notify
User=${DEPLOY_USER}
Group=${DEPLOY_USER}
WorkingDirectory=${DEPLOY_DIR}/backend
Environment="PATH=${VENV_DIR}/bin:/usr/local/bin:/usr/bin:/bin"
Environment="DATA_DIR=${DEPLOY_DIR}/data/raw"
ExecStart=${VENV_DIR}/bin/gunicorn main:app \\
    --workers 4 \\
    --worker-class uvicorn.workers.UvicornWorker \\
    --bind 0.0.0.0:${BACKEND_PORT} \\
    --timeout 120 \\
    --access-logfile /var/log/${PROJECT_NAME}-access.log \\
    --error-logfile /var/log/${PROJECT_NAME}-error.log
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
SYSTEMD_EOF

${SUDO} tee "${SYSTEMD_DIR}/${PROJECT_NAME}-nginx.service" > /dev/null <<'SYSTEMD_NGINX_EOF'
# 智慧场馆数字孪生平台 - Nginx 服务（覆盖默认）
[Unit]
Description=Smart Venue Twin Nginx
After=network.target smart-venue-twin-backend.service

[Service]
Type=forking
ExecStart=/usr/sbin/nginx
ExecReload=/usr/sbin/nginx -s reload
ExecStop=/usr/sbin/nginx -s quit
PIDFile=/run/nginx.pid
Restart=always

[Install]
WantedBy=multi-user.target
SYSTEMD_NGINX_EOF

ok "systemd 服务文件创建完成"

# ============================================================
# 8. 启动服务
# ============================================================
info "正在启动服务..."

# 重载 systemd
${SUDO} systemctl daemon-reload

# 启动后端服务
${SUDO} systemctl enable "${PROJECT_NAME}-backend"
${SUDO} systemctl restart "${PROJECT_NAME}-backend"

# 重启 Nginx
${SUDO} systemctl restart nginx

ok "服务启动完成"

# ============================================================
# 9. 验证部署
# ============================================================
echo ""
info "正在验证部署..."

sleep 3

# 检查后端健康
if curl -sf "http://localhost:${BACKEND_PORT}/health" > /dev/null 2>&1; then
    ok "后端服务运行正常"
else
    warn "后端服务可能未完全启动，请稍后检查"
fi

# 检查 Nginx
if curl -sf "http://localhost:${FRONTEND_PORT}/" > /dev/null 2>&1; then
    ok "Nginx 前端服务运行正常"
else
    warn "Nginx 前端服务可能未完全启动，请稍后检查"
fi

# ============================================================
# 10. 输出部署信息
# ============================================================
echo ""
echo "============================================================"
echo -e "${GREEN}  🏟️  智慧场馆数字孪生平台部署完成！${NC}"
echo "============================================================"
echo -e "  ${BLUE}前端地址:${NC}    http://${SERVER_NAME}:${FRONTEND_PORT}"
echo -e "  ${BLUE}后端API:${NC}     http://127.0.0.1:${BACKEND_PORT}"
echo -e "  ${BLUE}API文档:${NC}     http://${SERVER_NAME}:${FRONTEND_PORT}/docs"
echo ""
echo -e "  ${YELLOW}服务管理命令:${NC}"
echo "    systemctl status ${PROJECT_NAME}-backend  # 查看后端状态"
echo "    systemctl restart ${PROJECT_NAME}-backend # 重启后端"
echo "    sudo nginx -s reload                      # 重载Nginx配置"
echo "    journalctl -u ${PROJECT_NAME}-backend -f  # 查看后端日志"
echo "============================================================"
