"""
FastAPI 主程序 - 所有路由和 WebSocket
"""
from fastapi import FastAPI, UploadFile, File, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
from pathlib import Path

import config
from services.video_service import VideoService
from services.note_service import NoteService
from services.ai_service import AIService

# 创建 FastAPI 应用
app = FastAPI(
    title="Video Learning Assistant API",
    description="视频学习辅助智能体后端 API",
    version="1.0.0"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Demo 环境允许所有来源
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化服务
video_service = VideoService()
note_service = NoteService()
ai_service = AIService()

# ===== Pydantic 数据模型 =====

class NoteCreate(BaseModel):
    video_id: str
    timestamp: float
    type: str
    content: str = ""
    frame: str = ""  # base64 截图（可选）

class NoteUpdate(BaseModel):
    video_id: str
    note_id: str
    content: str

class AIQuestion(BaseModel):
    video_id: str
    timestamp: float
    question: str
    frame: str  # base64

# ===== 根路由 =====

@app.get("/")
def root():
    """健康检查"""
    return {
        "status": "ok",
        "message": "Video Learning Assistant API",
        "version": "1.0.0"
    }

# ===== 视频相关路由 =====

@app.post("/api/videos/upload")
async def upload_video(file: UploadFile = File(...)):
    """
    上传视频
    自动处理：提取关键帧、生成字幕、AI 分析
    """
    print(f"\n收到视频上传请求: {file.filename}")

    # 检查文件类型
    if not file.filename.endswith(('.mp4', '.avi', '.mov')):
        raise HTTPException(400, "只支持 mp4, avi, mov 格式")

    # 读取文件内容
    content = await file.read()
    file_size = len(content)
    print(f"文件大小: {file_size / (1024*1024):.2f} MB")

    # 检查文件大小
    if file_size > config.MAX_FILE_SIZE:
        raise HTTPException(400, f"文件过大，最大支持 {config.MAX_FILE_SIZE/(1024*1024):.0f}MB")

    # 保存文件
    file_path = config.UPLOAD_DIR / file.filename
    with open(file_path, "wb") as f:
        f.write(content)

    print(f"文件已保存到: {file_path}")

    # 处理视频（异步）
    try:
        result = await video_service.process_upload(str(file_path), file.filename)
        return result
    except Exception as e:
        print(f"视频处理失败: {e}")
        raise HTTPException(500, f"视频处理失败: {str(e)}")

@app.get("/api/videos/{video_id}")
def get_video(video_id: str):
    """获取视频信息"""
    video = video_service.get_video(video_id)
    if not video:
        raise HTTPException(404, "视频不存在")
    return video

@app.get("/api/videos/{video_id}/stream")
def stream_video(video_id: str):
    """流式传输视频文件"""
    video = video_service.get_video(video_id)
    if not video:
        raise HTTPException(404, "视频不存在")

    video_path = Path(video["path"])
    if not video_path.exists():
        raise HTTPException(404, "视频文件不存在")

    return FileResponse(
        video_path,
        media_type="video/mp4",
        headers={
            "Accept-Ranges": "bytes",
            "Content-Disposition": f"inline; filename={video['filename']}"
        }
    )

@app.get("/api/videos/{video_id}/frame")
def get_frame(video_id: str, timestamp: float):
    """获取指定时间的帧"""
    try:
        frame_base64 = video_service.get_frame_at(video_id, timestamp)
        return {"frame": frame_base64}
    except Exception as e:
        raise HTTPException(500, f"获取帧失败: {str(e)}")

# ===== 笔记相关路由 =====

@app.post("/api/notes")
def create_note(note: NoteCreate):
    """创建笔记"""
    try:
        result = note_service.create_note(
            note.video_id,
            note.timestamp,
            note.type,
            note.content,
            note.frame
        )
        return result
    except Exception as e:
        raise HTTPException(500, f"创建笔记失败: {str(e)}")

@app.put("/api/notes")
def update_note(note: NoteUpdate):
    """更新笔记"""
    success = note_service.update_note(
        note.video_id,
        note.note_id,
        note.content
    )
    if not success:
        raise HTTPException(404, "笔记不存在")
    return {"success": True}

@app.get("/api/notes/{video_id}")
def get_notes(video_id: str):
    """获取所有笔记"""
    try:
        notes = note_service.get_notes(video_id)
        return {"notes": notes}
    except Exception as e:
        raise HTTPException(500, f"获取笔记失败: {str(e)}")

@app.delete("/api/notes/{video_id}/{note_id}")
def delete_note(video_id: str, note_id: str):
    """删除笔记"""
    success = note_service.delete_note(video_id, note_id)
    if not success:
        raise HTTPException(404, "笔记不存在")
    return {"success": True}

@app.get("/api/notes/export/{video_id}")
def export_notes(video_id: str):
    """导出笔记为 Markdown"""
    try:
        markdown = note_service.export_markdown(video_id)
        return {"markdown": markdown}
    except Exception as e:
        raise HTTPException(500, f"导出失败: {str(e)}")

# ===== AI 相关路由 =====

@app.websocket("/ws/ai/chat")
async def ai_chat(websocket: WebSocket):
    """
    AI 问答（WebSocket 流式）
    """
    await websocket.accept()
    print("[DEBUG] WebSocket 连接已建立")

    try:
        while True:
            # 接收消息
            data = await websocket.receive_json()
            print(f"[DEBUG] 收到 WebSocket 消息: {data.keys()}")
            print(f"[DEBUG] 问题: {data.get('question')}")
            print(f"[DEBUG] 视频ID: {data.get('video_id')}")
            print(f"[DEBUG] 时间戳: {data.get('timestamp')}")
            print(f"[DEBUG] Frame长度: {len(data.get('frame', ''))}")

            question = data.get("question")
            video_id = data.get("video_id")
            timestamp = data.get("timestamp")
            frame = data.get("frame", "")  # frame 可以为空

            # 检查必要参数（frame 可选）
            if not question or not video_id or timestamp is None:
                error_msg = "缺少必要参数"
                print(f"[ERROR] {error_msg}")
                await websocket.send_json({"error": error_msg})
                continue

            print(f"[DEBUG] 开始调用 AI 服务...")
            chunk_count = 0

            # 流式返回
            async for chunk in ai_service.answer_question(
                video_id, timestamp, question, frame
            ):
                chunk_count += 1
                print(f"[DEBUG] 发送 Chunk #{chunk_count}: {chunk[:50]}...")
                await websocket.send_text(chunk)

            # 发送结束标记
            print(f"[DEBUG] 发送结束标记，总共发送了 {chunk_count} 个 chunk")
            await websocket.send_text("[DONE]")
            print("[DEBUG] 回答完成")

    except Exception as e:
        print(f"[ERROR] WebSocket 错误: {e}")
        import traceback
        traceback.print_exc()
        await websocket.send_json({"error": str(e)})
        await websocket.close()

# ===== 启动服务 =====

if __name__ == "__main__":
    import uvicorn

    print("\n" + "="*60)
    print("🚀 视频学习辅助智能体后端服务启动中...")
    print("="*60)
    print(f"📁 上传目录: {config.UPLOAD_DIR}")
    print(f"📁 数据目录: {config.DATA_DIR}")
    print(f"🤖 AI 模型: {config.AI_MODEL}")
    print(f"🎬 Whisper 模型: {config.WHISPER_MODEL_SIZE}")
    print(f"🔑 API URL: {config.API_BASE_URL}")
    print("="*60 + "\n")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=False  # 改为 False 避免警告
    )
