import os
import shutil
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# ================= 配置区 =================
# 音频保存路径
UPLOAD_DIR = "/media/data3/macy/openagents/voice_service/uploads"
# =========================================

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs(UPLOAD_DIR, exist_ok=True)

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NEON VOICE LINK v2.0</title>
    <link href="https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap" rel="stylesheet">
    <style>
        :root {
            --neon-cyan: #00f3ff;
            --neon-red: #ff003c;
            --bg-dark: #020508;
        }
        * { box-sizing: border-box; }
        body {
            font-family: 'Share Tech Mono', monospace;
            display: flex; flex-direction: column; align-items: center; justify-content: center;
            min-height: 100vh; margin: 0;
            background-color: var(--bg-dark);
            background-image: 
                radial-gradient(circle at center, rgba(0, 243, 255, 0.1) 0%, transparent 70%),
                linear-gradient(rgba(0, 243, 255, 0.02) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0, 243, 255, 0.02) 1px, transparent 1px);
            background-size: 100% 100%, 20px 20px, 20px 20px;
            color: var(--neon-cyan);
            overflow: hidden; position: relative;
        }
        /* 屏幕扫描线 */
        body::after {
            content: ""; position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            background: linear-gradient(transparent 50%, rgba(0, 243, 255, 0.03) 50%);
            background-size: 100% 3px; z-index: 1; pointer-events: none;
        }

        /* === 四角装饰 HUD === */
        .hud-corner { position: fixed; width: 100px; height: 100px; border: 2px solid var(--neon-cyan); z-index: 0; opacity: 0.5; }
        .tl { top: 20px; left: 20px; border-right: none; border-bottom: none; }
        .tr { top: 20px; right: 20px; border-left: none; border-bottom: none; }
        .bl { bottom: 20px; left: 20px; border-right: none; border-top: none; }
        .br { bottom: 20px; right: 20px; border-left: none; border-top: none; }
        .hud-corner::before { content: ''; position: absolute; width: 10px; height: 10px; background: var(--neon-cyan); }
        .tl::before { top: -6px; left: -6px; } .tr::before { top: -6px; right: -6px; }
        .bl::before { bottom: -6px; left: -6px; } .br::before { bottom: -6px; right: -6px; }

        /* === 主容器 === */
        .container {
            position: relative; z-index: 2;
            padding: 30px 40px;
            background: rgba(2, 5, 8, 0.85);
            border: 1px solid var(--neon-cyan);
            box-shadow: 0 0 25px rgba(0, 243, 255, 0.15), inset 0 0 15px rgba(0, 243, 255, 0.05);
            border-radius: 4px;
            text-align: center; width: 420px;
            backdrop-filter: blur(8px);
        }
        .container::before, .container::after { content: ""; position: absolute; width: 20px; height: 2px; background: var(--neon-cyan); }
        .container::before { top: -1px; left: 10px; } .container::after { bottom: -1px; right: 10px; }

        h2 { margin: 0 0 20px 0; letter-spacing: 3px; text-transform: uppercase; font-size: 24px; text-shadow: 0 0 8px var(--neon-cyan); }
        
        /* 音频可视化 Canvas */
        #visualizer {
            width: 100%; height: 50px; background: rgba(0,0,0,0.3);
            border-top: 1px dashed rgba(0, 243, 255, 0.5);
            border-bottom: 1px dashed rgba(0, 243, 255, 0.5);
            margin: 15px 0; display: none;
        }

        /* 核心按钮区域 */
        .control-panel { display: flex; align-items: center; justify-content: space-around; margin: 30px 0; }
        
        /* 麦克风按钮 */
        .mic-wrapper { position: relative; width: 90px; height: 90px; }
        .mic-btn {
            width: 100%; height: 100%; border-radius: 50%; border: 2px solid var(--neon-cyan);
            background: rgba(0,0,0,0.6); color: var(--neon-cyan); font-size: 36px;
            cursor: pointer; outline: none; transition: all 0.3s;
            box-shadow: 0 0 15px rgba(0, 243, 255, 0.3), inset 0 0 10px rgba(0, 243, 255, 0.2);
            display: flex; align-items: center; justify-content: center;
        }
        .mic-btn:hover { box-shadow: 0 0 25px rgba(0, 243, 255, 0.5), inset 0 0 20px rgba(0, 243, 255, 0.3); transform: scale(1.05); }
        .mic-btn.recording {
            color: var(--neon-red); border-color: var(--neon-red);
            box-shadow: 0 0 25px rgba(255, 0, 60, 0.5), inset 0 0 20px rgba(255, 0, 60, 0.3);
            animation: pulse-red 1.5s infinite ease-in-out;
        }

        /* 上传按钮 */
        .upload-btn-wrapper { position: relative; overflow: hidden; display: inline-block; }
        .cyber-btn {
            border: 1px solid var(--neon-cyan); background: transparent; color: var(--neon-cyan);
            padding: 12px 20px; font-family: 'Share Tech Mono', monospace; font-size: 14px;
            cursor: pointer; transition: all 0.3s; text-transform: uppercase; letter-spacing: 1px;
            box-shadow: 0 0 5px rgba(0, 243, 255, 0.2); position: relative; overflow: hidden;
        }
        .cyber-btn::before { content:''; position: absolute; top:0; left:-100%; width:100%; height:100%; background: linear-gradient(90deg, transparent, rgba(0,243,255,0.4), transparent); transition: 0.5s; }
        .cyber-btn:hover::before { left: 100%; }
        .cyber-btn:hover { background: rgba(0, 243, 255, 0.1); box-shadow: 0 0 15px rgba(0, 243, 255, 0.4); }
        .upload-btn-wrapper input[type=file] { font-size: 100px; position: absolute; left: 0; top: 0; opacity: 0; cursor: pointer; height: 100%; width: 100%; }

        .status { min-height: 20px; font-size: 13px; margin-bottom: 15px; text-transform: uppercase; letter-spacing: 1px; color: rgba(0, 243, 255, 0.7); }
        .blink { animation: blinker 0.8s linear infinite; color: var(--neon-red); }
        
        /* 结果区域 */
        .result-area { display: none; margin-top: 25px; text-align: left; border-top: 2px solid rgba(0,243,255,0.2); padding-top: 20px; }
        .path-box {
            background: rgba(0, 0, 0, 0.3); padding: 10px; border: 1px solid var(--neon-cyan);
            font-size: 11px; color: #fff; word-break: break-all; user-select: all; margin-bottom: 10px;
            box-shadow: inset 0 0 10px rgba(0, 243, 255, 0.1);
        }
        .copy-btn-full { width: 100%; padding: 12px; font-size: 16px; font-weight: bold; }

        /* === 新增：用户指南区域 === */
        .hints-section {
            margin-top: 30px; text-align: left; border-top: 2px solid rgba(0,243,255,0.2); padding-top: 20px;
        }
        .hints-title { font-size: 14px; margin-bottom: 10px; color: rgba(0, 243, 255, 0.8); text-transform: uppercase; }
        .hints-list { list-style: none; padding: 0; margin: 0; font-size: 12px; color: rgba(255,255,255,0.7); }
        .hints-list li { margin-bottom: 8px; position: relative; padding-left: 15px; }
        .hints-list li::before { content: ">"; position: absolute; left: 0; color: var(--neon-red); }
        .highlight { color: var(--neon-cyan); }

        @keyframes pulse-red { 0%, 100% { transform: scale(1); opacity: 1; } 50% { transform: scale(1.08); opacity: 0.7; } }
        @keyframes blinker { 50% { opacity: 0.3; } }
    </style>
</head>
<body>

<div class="hud-corner tl"></div>
<div class="hud-corner tr"></div>
<div class="hud-corner bl"></div>
<div class="hud-corner br"></div>

<div class="container">
    <h2>>> AUDIO UPLINK V2 <<</h2>
    
    <canvas id="visualizer"></canvas>

    <div class="control-panel">
        <div class="mic-wrapper">
            <button id="mainBtn" class="mic-btn" title="点击开始/停止录音">🎤</button>
        </div>
        
        <div class="upload-btn-wrapper">
            <button class="cyber-btn">[ UPLOAD FILE ]</button>
            <input type="file" id="fileInput" accept="audio/*">
        </div>
    </div>
    
    <div id="status" class="status">SYSTEM READY // AWAITING INPUT</div>

    <div id="resultArea" class="result-area">
        <div style="font-size:12px; color:var(--neon-cyan); margin-bottom:5px;">[DATA_PACKET_SAVED]</div>
        <div id="pathDisplay" class="path-box"></div>
        <button class="cyber-btn copy-btn-full" onclick="copyPath()">>> COPY PATH TO CLIPBOARD</button>
    </div>

    <div class="hints-section">
        <div class="hints-title">COMMAND PROTOCOLS // EXAMPLES</div>
        <ul class="hints-list">
            <li>"Research <span class="highlight">iPhone 16 specs</span> and create a report."</li>
            <li>"Compare <span class="highlight">Python vs Java</span> performance."</li>
            <li>"Analyze the document at <span class="highlight">[Paste Path Here]</span>."</li>
            <li>"Find latest news about <span class="highlight">OpenAI</span>."</li>
        </ul>
    </div>
</div>

<script>
    const UPLOAD_API = "/upload"; 
    let mediaRecorder = null;
    let audioChunks = [];
    const btn = document.getElementById('mainBtn');
    const fileInput = document.getElementById('fileInput');
    const status = document.getElementById('status');
    const resultArea = document.getElementById('resultArea');
    const pathDisplay = document.getElementById('pathDisplay');
    const canvas = document.getElementById('visualizer');
    const canvasCtx = canvas.getContext("2d");
    let isRecording = false;

    // Web Audio API
    let audioCtx, analyser, dataArray, source, drawVisual;

    // --- 核心逻辑：统一处理文件上传 ---
    async function handleFileUpload(fileObj, fileName) {
        status.innerText = "UPLOADING DATA PACKET...";
        const formData = new FormData();
        formData.append("file", fileObj, fileName);

        try {
            const res = await fetch(UPLOAD_API, { method: "POST", body: formData });
            const data = await res.json();
            if (data.path) {
                status.innerText = "UPLOAD COMPLETE // READY FOR TRANSFER";
                pathDisplay.innerText = data.path;
                resultArea.style.display = 'block';
                copyPath();
            } else {
                status.innerText = "ERROR: SAVE FAILED ON SERVER";
            }
        } catch (e) {
            status.innerText = "ERROR: CONNECTION LOST";
        }
    }

    // --- 事件监听：文件选择 ---
    fileInput.addEventListener('change', function() {
        if (this.files.length > 0) {
            stopVisualizer();
            resultArea.style.display = 'none';
            handleFileUpload(this.files[0], this.files[0].name);
        }
    });

    // --- 事件监听：录音按钮点击 ---
    btn.onclick = async () => {
        if (!mediaRecorder) {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                mediaRecorder = new MediaRecorder(stream);
                
                // 初始化可视化
                audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                analyser = audioCtx.createAnalyser();
                source = audioCtx.createMediaStreamSource(stream);
                source.connect(analyser);
                analyser.fftSize = 256; 
                const bufferLength = analyser.frequencyBinCount;
                dataArray = new Uint8Array(bufferLength);
                canvas.width = canvas.clientWidth;
                canvas.height = canvas.clientHeight;

                mediaRecorder.ondataavailable = e => { if(e.data.size > 0) audioChunks.push(e.data); };
                mediaRecorder.onstop = () => {
                    stopVisualizer();
                    const blob = new Blob(audioChunks, { type: 'audio/wav' });
                    if (blob.size < 500) { status.innerText = "WARNING: INPUT TOO SHORT"; return; }
                    handleFileUpload(blob, "voice_command.wav");
                };
                startRec();
            } catch (err) {
                console.error(err);
                status.innerHTML = "<span style='color:var(--neon-red)'>ERROR: MIC ACCESS DENIED</span>";
            }
        } else {
            if (isRecording) stopRec(); else startRec();
        }
    };

    function startRec() {
        audioChunks = []; mediaRecorder.start(); isRecording = true;
        btn.classList.add('recording'); btn.innerHTML = "■";
        status.innerHTML = "<span class='blink'>RECORDING IN PROGRESS...</span>";
        resultArea.style.display = 'none';
        canvas.style.display = 'block';
        drawVisualizer();
    }

    function stopRec() {
        mediaRecorder.stop(); isRecording = false;
        btn.classList.remove('recording'); btn.innerHTML = "🎤";
        status.innerText = "PROCESSING AUDIO DATA...";
    }

    function drawVisualizer() {
        drawVisual = requestAnimationFrame(drawVisualizer);
        analyser.getByteFrequencyData(dataArray);
        canvasCtx.fillStyle = 'rgba(0, 0, 0, 0.2)'; //比起纯黑，用半透明黑色制造拖影效果
        canvasCtx.fillRect(0, 0, canvas.width, canvas.height);
        const barWidth = (canvas.width / dataArray.length) * 2;
        let x = 0;
        for(let i = 0; i < dataArray.length; i++) {
            const barHeight = dataArray[i] / 2.5;
            // 颜色基于高度变化：青色 -> 亮白
            const r = 0; const g = 243 + (barHeight); const b = 255;
            canvasCtx.fillStyle = `rgb(${r},${g},${b})`;
            canvasCtx.fillRect(x, canvas.height - barHeight, barWidth, barHeight);
            x += barWidth + 1;
        }
    }

    function stopVisualizer() {
        if (drawVisual) { cancelAnimationFrame(drawVisual); canvas.style.display = 'none'; }
    }

    window.copyPath = function() {
        const text = pathDisplay.innerText;
        navigator.clipboard.writeText(text).then(() => {
            status.innerHTML = "✅ <span style='color:#fff'>PATH COPIED // PASTE TO AGENT</span>";
        }).catch(() => {});
    }
</script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    return HTML_CONTENT

@app.post("/upload")
async def upload_audio(file: UploadFile = File(...)):
    try:
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        # 获取原始后缀或默认为 .wav
        ext = os.path.splitext(file.filename)[1]
        if not ext: ext = ".wav"
        
        filename = f"rec_{timestamp_str}{ext}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        print(f"💾 [AUTO-SAVE] File stored: {file_path}")
        return {"path": file_path}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    print("🌐 CYBER-LINK V2 INITIALIZED: http://localhost:8081")
    uvicorn.run(app, host="0.0.0.0", port=8081)