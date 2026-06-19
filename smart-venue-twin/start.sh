#!/usr/bin/env bash
# ============================================================
# 智慧场馆数字孪生平台 - 一键启动脚本
# 功能：自动检查环境、安装依赖、生成数据、启动前后端服务
# ============================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # 无颜色

# 项目根目录
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="${PROJECT_DIR}/backend"
FRONTEND_DIR="${PROJECT_DIR}/frontend"
DATA_DIR="${PROJECT_DIR}/data"
VENV_DIR="${BACKEND_DIR}/venv"

# 后端和前端进程ID
BACKEND_PID=""
FRONTEND_PID=""

# 打印带颜色的信息
info()  { echo -e "${BLUE}[信息]${NC} $1"; }
ok()    { echo -e "${GREEN}[成功]${NC} $1"; }
warn()  { echo -e "${YELLOW}[警告]${NC} $1"; }
error() { echo -e "${RED}[错误]${NC} $1"; }

# ============================================================
# 清理函数：停止所有后台服务
# ============================================================
cleanup() {
    echo ""
    info "正在停止服务..."
    if [ -n "$BACKEND_PID" ] && kill -0 "$BACKEND_PID" 2>/dev/null; then
        kill "$BACKEND_PID" 2>/dev/null
        info "后端服务已停止 (PID: $BACKEND_PID)"
    fi
    if [ -n "$FRONTEND_PID" ] && kill -0 "$FRONTEND_PID" 2>/dev/null; then
        kill "$FRONTEND_PID" 2>/dev/null
        info "前端服务已停止 (PID: $FRONTEND_PID)"
    fi
    # 清理子进程
    jobs -p | xargs -r kill 2>/dev/null || true
    ok "所有服务已停止"
    exit 0
}

# 捕获 Ctrl+C 信号
trap cleanup SIGINT SIGTERM

# ============================================================
# 1. 检查 Python3 是否可用
# ============================================================
info "检查 Python3 环境..."
if ! command -v python3 &>/dev/null; then
    error "未找到 python3，请先安装 Python 3.9+"
    exit 1
fi
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
ok "Python3 版本: ${PYTHON_VERSION}"

# ============================================================
# 2. 检查 Node.js 是否可用
# ============================================================
info "检查 Node.js 环境..."
if ! command -v node &>/dev/null; then
    error "未找到 node，请先安装 Node.js 18+"
    exit 1
fi
NODE_VERSION=$(node -v)
ok "Node.js 版本: ${NODE_VERSION}"

# ============================================================
# 3. 创建 Python 虚拟环境（如不存在）
# ============================================================
if [ ! -d "${VENV_DIR}" ]; then
    info "正在创建 Python 虚拟环境..."
    python3 -m venv "${VENV_DIR}"
    ok "虚拟环境创建完成: ${VENV_DIR}"
else
    info "虚拟环境已存在，跳过创建"
fi

# 激活虚拟环境
source "${VENV_DIR}/bin/activate"

# ============================================================
# 4. 安装 Python 依赖
# ============================================================
info "正在安装后端 Python 依赖..."
pip install --quiet --upgrade pip
pip install --quiet -r "${BACKEND_DIR}/requirements.txt"
ok "Python 依赖安装完成"

# ============================================================
# 5. 生成数据（如 raw 目录为空或不存在）
# ============================================================
RAW_DATA_DIR="${DATA_DIR}/raw"
if [ ! -d "${RAW_DATA_DIR}" ] || [ -z "$(ls -A "${RAW_DATA_DIR}" 2>/dev/null)" ]; then
    info "数据目录为空，正在生成模拟数据..."
    python3 "${DATA_DIR}/generate_data.py"
    ok "模拟数据生成完成"
else
    info "数据文件已存在，跳过数据生成"
fi

# ============================================================
# 6. 清洗数据（如 clean_data.py 存在且清洗后数据不存在）
# ============================================================
CLEANED_DIR="${DATA_DIR}/cleaned"
if [ -f "${DATA_DIR}/clean_data.py" ]; then
    if [ ! -d "${CLEANED_DIR}" ] || [ -z "$(ls -A "${CLEANED_DIR}" 2>/dev/null)" ]; then
        info "正在执行数据清洗..."
        python3 "${DATA_DIR}/clean_data.py"
        ok "数据清洗完成"
    else
        info "清洗后数据已存在，跳过数据清洗"
    fi
else
    warn "未找到 clean_data.py，跳过数据清洗步骤"
fi

# ============================================================
# 7. 安装前端依赖
# ============================================================
info "正在安装前端依赖..."
cd "${FRONTEND_DIR}"
npm install --silent 2>/dev/null || npm install
ok "前端依赖安装完成"

# ============================================================
# 8. 启动后端服务（后台运行）
# ============================================================
info "正在启动后端服务..."
cd "${BACKEND_DIR}"
uvicorn main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
ok "后端服务已启动 (PID: ${BACKEND_PID})"

# 等待后端启动
sleep 3

# 检查后端是否正常运行
if ! kill -0 "$BACKEND_PID" 2>/dev/null; then
    error "后端服务启动失败，请检查日志"
    exit 1
fi

# ============================================================
# 9. 启动前端开发服务器（后台运行）
# ============================================================
info "正在启动前端开发服务器..."
cd "${FRONTEND_DIR}"
npm run dev -- --host 0.0.0.0 --port 3000 &
FRONTEND_PID=$!
ok "前端服务已启动 (PID: ${FRONTEND_PID})"

# ============================================================
# 10. 打印访问信息
# ============================================================
echo ""
echo "============================================================"
echo -e "${GREEN}  🏟️  智慧场馆数字孪生平台已启动！${NC}"
echo "============================================================"
echo -e "  ${BLUE}前端地址:${NC}  http://localhost:3000"
echo -e "  ${BLUE}后端API:${NC}   http://localhost:8000"
echo -e "  ${BLUE}API文档:${NC}   http://localhost:8000/docs"
echo -e "  ${BLUE}健康检查:${NC}  http://localhost:8000/health"
echo ""
echo -e "  ${YELLOW}按 Ctrl+C 停止所有服务${NC}"
echo "============================================================"
echo ""

# 等待任一进程退出
wait -n "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null || wait
