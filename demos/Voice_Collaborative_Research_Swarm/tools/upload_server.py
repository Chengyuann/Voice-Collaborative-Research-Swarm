import os
import shutil
import httpx  # 需要安装: pip install httpx
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from datetime import datetime

# 🟢 配置：OpenAgents 的 API 地址 (根据你的日志是 8700)
OPENAGENTS_API_URL = "http://localhost:8700/api/send_event"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "/media/data3/macy/openagents/voice_service/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload")
async def upload_audio(file: UploadFile = File(...)):
    # 1. 保存文件
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"rec_{timestamp}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    print(f"🎤 音频已保存: {file_path}")

    # 2. 🟢 核心升级：自动发送给 Router
    try:
        print("🚀 正在转发给 Router...")
        async with httpx.AsyncClient() as client:
            # 构造一个伪造的消息事件，模仿用户(admin)发消息给(router)
            payload = {
                "event_name": "thread.direct_message.send",
                "source_id": "admin",  # 模仿管理员身份
                "destination_id": "agent:router", # 发送给 Router
                "payload": {
                    "content": {
                        "text": file_path  # 把路径作为消息内容发送
                    },
                    "message_type": "text"
                }
            }
            
            # 发送请求
            response = await client.post(OPENAGENTS_API_URL, json=payload, timeout=5.0)
            
            if response.status_code == 200:
                print("✅ 成功推送到 OpenAgents！Agent 应该开始工作了。")
                return {"status": "success", "path": file_path, "agent_response": "triggered"}
            else:
                print(f"❌ 推送失败: {response.status_code} - {response.text}")
                return {"status": "saved_but_failed_to_trigger", "path": file_path}

    except Exception as e:
        print(f"⚠️ 触发 Agent 异常: {e}")
        return {"status": "saved_but_error", "path": file_path}

if __name__ == "__main__":
    # 安装依赖：pip install fastapi uvicorn python-multipart httpx
    uvicorn.run(app, host="0.0.0.0", port=8081)