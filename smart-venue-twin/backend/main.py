"""
智慧场馆数字孪生平台 - FastAPI后端主入口
提供REST API和WebSocket实时数据推送
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from data_loader import load_all_data
from routers import overview, revenue, traffic, equipment, economic, websocket

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理 - 启动时加载数据"""
    logger.info("🚀 智慧场馆数字孪生平台启动中...")
    # 启动时加载CSV数据到内存
    load_all_data()
    logger.info("✅ 数据加载完成，服务就绪")
    yield
    logger.info("👋 服务关闭")


# 创建FastAPI应用实例
app = FastAPI(
    title="智慧场馆数字孪生平台",
    description="提供场馆运营数据API和实时WebSocket推送",
    version="1.0.0",
    lifespan=lifespan,
)

# 配置CORS中间件（开发环境允许所有来源）
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发环境允许所有来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(overview.router)
app.include_router(revenue.router)
app.include_router(traffic.router)
app.include_router(equipment.router)
app.include_router(economic.router)
app.include_router(websocket.router)


@app.get("/", tags=["健康检查"])
async def root():
    """根路径健康检查"""
    return {
        "service": "智慧场馆数字孪生平台",
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/health", tags=["健康检查"])
async def health_check():
    """服务健康检查端点"""
    return {"status": "healthy"}
