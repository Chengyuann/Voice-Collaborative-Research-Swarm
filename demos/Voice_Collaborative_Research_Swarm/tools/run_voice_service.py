import os
import shutil
import httpx
import uuid
import time
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from datetime import datetime

# ================= 配置区 =================
OPENAGENTS_API_URL = "http://localhost:8700/api/send_event"
UPLOAD_DIR = "/media/data3/macy/openagents/voice_service/uploads"

# 🟢 这里填入 router.yaml 注释里提到的密码明文
# 对应 password_hash: "bf2438... (coordinator)"
ROUTER_PASSWORD = "coordinator" 
# =========================================

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs(UPLOAD_DIR, exist_ok=True)

# 🟢 前端页面 (保持你的“点击交互”习惯)
HTML_CONTENT = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenAgents 语音控制台</title>
    <style>
        body { font-family: 'Segoe UI', system-ui, sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; background: linear-gradient(135deg, #2c3e50 0%, #4ca1af 100%); color: white; margin: 0; }
        .card { background: rgba(255, 255, 255, 0.15); backdrop-filter: blur(12px); padding: 40px; border-radius: 20px; box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2); text-align: center; border: 1px solid rgba(255, 255, 255, 0.1); width: 300px; }
        h2 { margin-bottom: 30px; font-weight: 300; letter-spacing: 1px; }
        .mic-btn {
            width: 100px; height: 100px; border-radius: 50%; border: none; cursor: pointer; outline: none;
            background: #e74c3c; box-shadow: 0 0 0 0 rgba(231, 76, 60, 0.7);
            font-size: 40px; color: white; transition: all 0.3s; display: flex; align-items: center; justify-content: center; margin: 0 auto;
            -webkit-tap-highlight-color: transparent; user-select: none;
        }
        .mic-btn.recording { animation: pulse 1.5s infinite; background: #2ecc71; box-shadow: 0 0 0 0 rgba(46, 204, 113, 0.7); transform: scale(1.1); }
        .mic-btn:active { transform: scale(0.95); }
        .status { margin-top: 25px; font-size: 16px; color: #ecf0f1; min-height: 24px; font-weight: 500;}
        .tips { margin-top: 15px; font-size: 12px; color: #bdc3c7; }
        
        @keyframes pulse {
            0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(46, 204, 113, 0.7); }
            70% { transform: scale(1.1); box-shadow: 0 0 0 15px rgba(46, 204, 113, 0); }
            100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(46, 204, 113, 0); }
        }
    </style>
</head>
<body>
    <div class="card">
        <h2>🎙️ 语音指令台</h2>
        <button id="recordBtn" class="mic-btn">🎤</button>
        <div id="status" class="status">点击麦克风开始</div>
        <div class="tips">录音将发送给 Research Team</div>
    </div>

<script>
    const UPLOAD_API = "/upload"; 
    let mediaRecorder;
    let audioChunks = [];
    const btn = document.getElementById('recordBtn');
    const status = document.getElementById('status');
    let isRecording = false;

    async function initAudio() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            
            mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
            mediaRecorder.onstop = uploadAudio;
            
            btn.onclick = toggleRecording;
            
        } catch (err) {
            status.innerText = "❌ 无法访问麦克风";
            btn.style.background = "#95a5a6";
            console.error(err);
        }
    }

    function toggleRecording() {
        if (!isRecording) {
            audioChunks = [];
            mediaRecorder.start();
            isRecording = true;
            btn.classList.add('recording');
            btn.innerHTML = "⬛"; 
            status.innerText = "🔴 正在录音... (点击发送)";
        } else {
            mediaRecorder.stop();
            isRecording = false;
            btn.classList.remove('recording');
            btn.innerHTML = "🎤";
            status.innerText = "⏳ 正在发送...";
        }
    }

    async function uploadAudio() {
        const blob = new Blob(audioChunks, { type: 'audio/wav' });
        const formData = new FormData();
        formData.append("file", blob, "voice_cmd.wav");

        try {
            const res = await fetch(UPLOAD_API, { method: "POST", body: formData });
            const data = await res.json();
            
            // 只要 status 是 success，或者 agent_response 里的 success 是 true
            if (data.status === "success" && data.agent_response && data.agent_response.success !== false) {
                status.innerHTML = "✅ <b>指令已送达！</b>";
                setTimeout(() => status.innerText = "点击麦克风开始", 2500);
            } else {
                let errMsg = "发送失败";
                if(data.agent_response && data.agent_response.message) {
                    errMsg = data.agent_response.message;
                }
                status.innerText = "⚠️ " + errMsg;
            }
        } catch (e) {
            console.error(e);
            status.innerText = "❌ 网络错误";
        }
    }

    initAudio();
</script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    return HTML_CONTENT

@app.post("/upload")
async def upload_audio(file: UploadFile = File(...)):
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"rec_{timestamp_str}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    print(f"🎤 收到音频: {file_path}")

    # 2. 转发给 Agent Router
    try:
        print("🚀 正在触发 Agent Router...")
        async with httpx.AsyncClient() as client:
            payload = {
                "event_id": str(uuid.uuid4()),
                "timestamp": int(time.time()),
                "event_name": "thread.direct_message.send",
                "source_id": "voice_assistant", # 换个更好听的名字
                "destination_id": "agent:router",
                "payload": {
                    "content": {
                        "text": file_path
                    },
                    "message_type": "text"
                }
            }
            
            # 🟢 关键修正：同时尝试两种常见的鉴权头，确保万无一失
            headers = {
                "Authorization": f"Bearer {ROUTER_PASSWORD}",  # 标准 JWT/Token 格式
                "X-Agent-Secret": ROUTER_PASSWORD,             # OpenAgents 自定义格式
                "Content-Type": "application/json"
            }
            
            response = await client.post(OPENAGENTS_API_URL, json=payload, headers=headers, timeout=10.0)
            api_resp = response.json()
            
            if response.status_code == 200:
                if api_resp.get("success") is False:
                    print(f"❌ API 拒绝: {api_resp}")
                else:
                    print(f"✅ API 接受: {api_resp}")
                return {"status": "success", "agent_response": api_resp, "path": file_path}
            else:
                print(f"❌ HTTP 错误: {response.status_code} - {response.text}")
                return {"status": "error", "detail": f"HTTP {response.status_code}"}

    except Exception as e:
        print(f"⚠️ 异常: {e}")
        return {"status": "error", "detail": str(e)}

if __name__ == "__main__":
    print("🌐 语音服务启动中...")
    print("👉 请在浏览器打开: http://localhost:8081")
    uvicorn.run(app, host="0.0.0.0", port=8081)