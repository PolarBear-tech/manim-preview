const player = document.getElementById("player");
const statusBar = document.getElementById("status-bar");
const logPanel = document.getElementById("log-panel");
const videoPlaceholder = document.getElementById("video-placeholder");

let lastVideoTs = 0;
let lastStatus = "";
let isVideoLoading = false;

// 日志追加工具
function appendLog(text) {
  logPanel.innerText += "\n" + text;
  logPanel.scrollTop = logPanel.scrollHeight;
}

// 【公共加载视频函数】页面初始化/渲染完成共用
function loadVideo() {
  if (isVideoLoading) return;
  isVideoLoading = true;
  lastVideoTs = Date.now();
  const videoUrl = `/output/tmp.mp4?t=${lastVideoTs}`;
  appendLog("[预览] 加载视频资源：" + videoUrl);
  player.pause();
  player.currentTime = 0;
  player.src = videoUrl;
  player.load();
  videoPlaceholder.textContent = "⏳ 正在加载视频...";
  videoPlaceholder.style.display = "block";
  player.style.display = "none";
}

// 视频加载完成
player.addEventListener("loadeddata", () => {
  videoPlaceholder.style.display = "none";
  player.style.display = "block";
  isVideoLoading = false;
  player.muted = true;
});

// 视频加载失败
player.addEventListener("error", (e) => {
  isVideoLoading = false;
  videoPlaceholder.style.display = "block";
  player.style.display = "none";
  videoPlaceholder.textContent = "❌ 视频加载失败，等待下次渲染";
  appendLog("[视频错误] 预览MP4加载失败，请确认后端 /output/tmp.mp4 文件存在");
  console.error("video load error", e);
});

// 轮询后端渲染状态
function pollState() {
  fetch("/status")
    .then(res => res.json())
    .then(state => {
      let statusText = "";
      statusBar.className = "status-bar " + state.status;
      switch (state.status) {
        case "idle": statusText = "✅ 空闲，修改代码即可渲染"; break;
        case "rendering": statusText = "⏳ 正在渲染中..."; break;
        case "done": statusText = "🎉 渲染完成"; break;
        case "error": statusText = "❌ 渲染出错"; break;
      }
      statusBar.innerText = statusText;

      logPanel.innerText = state.log;
      logPanel.scrollTop = logPanel.scrollHeight;

      if (state.status === "done" && lastStatus !== "done" && !isVideoLoading) {
        loadVideo();
      }
      lastStatus = state.status;
    })
    .catch(err => {
      statusBar.innerText = "⚠️ 服务连接失败，请检查后端服务";
      statusBar.className = "status-bar error";
      appendLog("[服务错误] 轮询 /status 接口失败：" + err.message);
      console.error("轮询错误：", err);
    });
}

setInterval(pollState, 100);
pollState();

// 页面打开预加载视频
window.addEventListener("DOMContentLoaded", () => {
  appendLog("[初始化] 页面加载完成，预加载已有视频文件");
  loadVideo();
});
