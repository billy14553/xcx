 import os
 
 html = r'''<!DOCTYPE html>
 <html lang="zh-CN">
 <head>
 <meta charset="UTF-8">
 <meta name="viewport" content="width=device-width, initial-scale=1.0">
 <title>小魔鬼闯关 - Kids Edition</title>
 <style>
   * { margin: 0; padding: 0; box-sizing: border-box; }
   body { background: #1a1a2e; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 100vh; font-family: Segoe UI, sans-serif; overflow: hidden; }
   #header { color: #eee; margin-bottom: 12px; text-align: center; }
   #header h1 { font-size: 24px; color: #ff6b6b; }
   #header .level-info { font-size: 16px; color: #ffd93d; margin-top: 4px; }
   canvas { border: 3px solid #4a4a6a; border-radius: 8px; background: #16213e; display: block; }
   #footer { color: #aaa; font-size: 13px; margin-top: 10px; text-align: center; }
   #win-screen { display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.85); flex-direction: column; align-items: center; justify-content: center; z-index: 10; }
   #win-screen.show { display: flex; }
   #win-screen h2 { font-size: 48px; color: #ffd93d; margin-bottom: 20px; }
   #win-screen button { padding: 12px 32px; font-size: 20px; background: #ff6b6b; color: white; border: none; border-radius: 8px; cursor: pointer; margin: 8px; }
  #win-screen button:hover { background: #ff8787; }
  #timer { position: absolute; left: 20px; top: 20px; color: #ffd93d; font-size: 18px; font-weight: 600; background: rgba(0,0,0,0.35); padding: 8px 16px; border-radius: 20px; pointer-events: none; }
</style>
 </head>
 <body>
<div id="header"><h1>小魔鬼闯关</h1><div class="level-info" id="level-info">第 1 关 / 共 5 关</div></div>
<div id="timer">时间：0.00 秒</div>
<canvas id="game" width="800" height="500"></canvas>
 <div id="footer">方向键/WASD 移动，空格/↑ 跳跃<button id="music-btn" style="margin-left:14px;padding:4px 12px;border:1px solid #ffd93d;background:rgba(255,217,61,0.15);color:#ffd93d;border-radius:14px;cursor:pointer;font-size:13px;">🔊 音乐</button></div>
 <div id="win-screen"><h2 id="win-text">🎉 通关成功！</h2><div id="win-time" style="font-size:24px;color:#fff;margin-bottom:8px;">通关时间：0.00 秒</div><div id="win-best" style="font-size:20px;color:#ffd93d;margin-bottom:8px;">最快成绩：--</div><div id="win-compare" style="font-size:18px;color:#7ec8e3;margin-bottom:12px;"></div><div id="win-deaths" style="font-size:20px;color:#ff6b6b;margin-bottom:8px;">死亡次数：0 次</div><div id="win-best-deaths" style="font-size:18px;color:#ffd93d;margin-bottom:8px;">最少死亡：--</div><div id="win-deaths-compare" style="font-size:16px;color:#7ec8e3;margin-bottom:16px;"></div><button id="restart-btn">重新开始</button></div>
 <script>
 const canvas = document.getElementById("game");
 const ctx = canvas.getContext("2d");
 const W = canvas.width, H = canvas.height;
 const GRAVITY = 0.6;
 let currentLevel = 0, deathCount = 0, gameWon = false;
 let keys = {}, player, platforms, spikes, movingPlatforms, door;
let startTime = Date.now(), totalTime = 0, timerRunning = true, pauseStartedAt = 0;
const FIXED_DT = 1/60; let lastTime = performance.now(); let accumulator = 0; const MAX_DT = 0.1;
let bestTime = parseFloat(localStorage.getItem("levelDevilBestTime")) || Infinity;
let bestDeaths = parseInt(localStorage.getItem("levelDevilBestDeaths")) || Infinity;
const PHANTOM = { enabled: true, interval: 1, maxCount: 28, fadeStep: 0.05, minAlpha: 0.05, startAlpha: 0.85, moveThreshold: 0.2, jumpThreshold: 0.3 };
let phantomTrail = []; let phantomFrame = 0;
let audioCtx = null, musicEnabled = true, musicTimer = null, musicStep = 0; const MASTER_GAIN = 0.12;
const NOTE = { C4: 261.63, D4: 293.66, E4: 329.63, F4: 349.23, G4: 392.00, A4: 440.00, B4: 493.88, C5: 523.25, D5: 587.33, E5: 659.25, F5: 698.46, G5: 783.99, A5: 880.00, C3: 130.81, D3: 146.83, E3: 164.81, F3: 174.61, G3: 196.00, A3: 220.00, REST: 0 };
const MELODY = [
  [NOTE.E5,8],[NOTE.E5,8],[NOTE.REST,8],[NOTE.E5,8],[NOTE.REST,8],[NOTE.C5,8],[NOTE.E5,8],[NOTE.REST,8],
  [NOTE.G5,16],[NOTE.REST,16],[NOTE.G4,16],[NOTE.REST,16],
  [NOTE.C5,16],[NOTE.REST,8],[NOTE.G4,16],[NOTE.REST,8],[NOTE.E4,16],[NOTE.REST,8],
  [NOTE.A4,8],[NOTE.B4,8],[NOTE.REST,8],[NOTE.A4,8],[NOTE.REST,8],[NOTE.A4*Math.pow(2,1/12),8],[NOTE.A4,8],
  [NOTE.G4,12],[NOTE.E5,12],[NOTE.G5,12],[NOTE.A5,4],[NOTE.REST,4],
  [NOTE.F5,8],[NOTE.G5,8],[NOTE.REST,8],[NOTE.E5,8],[NOTE.REST,8],[NOTE.C5,8],[NOTE.D5,8],[NOTE.B4,8],
  [NOTE.C5,8],[NOTE.REST,8],[NOTE.G4,8],[NOTE.REST,8],[NOTE.E4,8],[NOTE.REST,8],
  [NOTE.A4,8],[NOTE.B4,8],[NOTE.REST,8],[NOTE.A4,8],[NOTE.REST,8],[NOTE.G4,8],[NOTE.E5,8],
  [NOTE.G5,8],[NOTE.A5,4],[NOTE.REST,4],[NOTE.F5,8],[NOTE.G5,8],[NOTE.REST,8],[NOTE.E5,8],[NOTE.REST,8],
  [NOTE.C5,8],[NOTE.D5,8],[NOTE.B4,8],[NOTE.REST,8],
  [NOTE.C5,8],[NOTE.REST,8],[NOTE.G4,8],[NOTE.REST,8],[NOTE.E4,8],[NOTE.REST,8],
  [NOTE.A4,8],[NOTE.B4,8],[NOTE.REST,8],[NOTE.A4,8],[NOTE.REST,8],[NOTE.G4,8],[NOTE.E5,8],
  [NOTE.G5,8],[NOTE.A5,4],[NOTE.REST,4],[NOTE.F5,8],[NOTE.G5,8],[NOTE.REST,8],[NOTE.E5,8],[NOTE.REST,8],
  [NOTE.C5,8],[NOTE.D5,8],[NOTE.B4,8],[NOTE.REST,8]
];
const BASS = [
  [NOTE.C3,16],[NOTE.REST,16],[NOTE.G3,16],[NOTE.REST,16],[NOTE.C3,16],[NOTE.REST,16],[NOTE.G3,16],[NOTE.REST,16],
  [NOTE.A3,16],[NOTE.REST,16],[NOTE.E3,16],[NOTE.REST,16],[NOTE.A3,16],[NOTE.REST,16],[NOTE.E3,16],[NOTE.REST,16],
  [NOTE.F3,16],[NOTE.REST,16],[NOTE.C3,16],[NOTE.REST,16],[NOTE.F3,16],[NOTE.REST,16],[NOTE.C3,16],[NOTE.REST,16],
  [NOTE.G3,16],[NOTE.REST,16],[NOTE.D3,16],[NOTE.REST,16],[NOTE.G3,16],[NOTE.REST,16],[NOTE.D3,16],[NOTE.REST,16]
];
function initAudio() { if (audioCtx) return; try { audioCtx = new (window.AudioContext || window.webkitAudioContext)(); } catch (e) { musicEnabled = false; } }
function playNote(freq, durationMs, type, gain) { if (!audioCtx || !musicEnabled || freq === NOTE.REST) return; const osc = audioCtx.createOscillator(); const g = audioCtx.createGain(); osc.type = type || "square"; osc.frequency.setValueAtTime(freq, audioCtx.currentTime); g.gain.setValueAtTime(0, audioCtx.currentTime); g.gain.linearRampToValueAtTime((gain || 0.18) * MASTER_GAIN, audioCtx.currentTime + 0.01); g.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + durationMs / 1000); osc.connect(g).connect(audioCtx.destination); osc.start(); osc.stop(audioCtx.currentTime + durationMs / 1000 + 0.05); }
function sfxJump() { if (!audioCtx) return; const t = audioCtx.currentTime; const osc = audioCtx.createOscillator(); const g = audioCtx.createGain(); osc.type = "square"; osc.frequency.setValueAtTime(520, t); osc.frequency.exponentialRampToValueAtTime(1200, t + 0.12); g.gain.setValueAtTime(0, t); g.gain.linearRampToValueAtTime(0.22 * MASTER_GAIN, t + 0.01); g.gain.exponentialRampToValueAtTime(0.001, t + 0.18); osc.connect(g).connect(audioCtx.destination); osc.start(t); osc.stop(t + 0.2); }
function sfxDeath() { if (!audioCtx) return; const t = audioCtx.currentTime; [0, 0.18].forEach((delay, i) => { const osc = audioCtx.createOscillator(); const g = audioCtx.createGain(); osc.type = "square"; osc.frequency.setValueAtTime(i === 0 ? 440 : 330, t + delay); osc.frequency.exponentialRampToValueAtTime(i === 0 ? 220 : 110, t + delay + 0.18); g.gain.setValueAtTime(0, t + delay); g.gain.linearRampToValueAtTime(0.28 * MASTER_GAIN, t + delay + 0.01); g.gain.exponentialRampToValueAtTime(0.001, t + delay + 0.2); osc.connect(g).connect(audioCtx.destination); osc.start(t + delay); osc.stop(t + delay + 0.22); }); }
function sfxWin() { if (!audioCtx) return; const t = audioCtx.currentTime; const notes = [523.25, 659.25, 783.99, 1046.5]; notes.forEach((freq, i) => { const osc = audioCtx.createOscillator(); const g = audioCtx.createGain(); osc.type = "square"; osc.frequency.setValueAtTime(freq, t + i * 0.1); g.gain.setValueAtTime(0, t + i * 0.1); g.gain.linearRampToValueAtTime(0.25 * MASTER_GAIN, t + i * 0.1 + 0.01); g.gain.exponentialRampToValueAtTime(0.001, t + i * 0.1 + 0.18); osc.connect(g).connect(audioCtx.destination); osc.start(t + i * 0.1); osc.stop(t + i * 0.1 + 0.2); }); const lastOsc = audioCtx.createOscillator(); const lastG = audioCtx.createGain(); lastOsc.type = "square"; lastOsc.frequency.setValueAtTime(1046.5, t + 0.4); lastG.gain.setValueAtTime(0, t + 0.4); lastG.gain.linearRampToValueAtTime(0.25 * MASTER_GAIN, t + 0.42); lastG.gain.exponentialRampToValueAtTime(0.001, t + 0.95); lastOsc.connect(lastG).connect(audioCtx.destination); lastOsc.start(t + 0.4); lastOsc.stop(t + 1.0); }
function musicStepRunner() { if (!musicEnabled || !audioCtx) return; const m = MELODY[musicStep % MELODY.length]; playNote(m[0], (m[1]/16)*480, "square", 0.22); const b = BASS[musicStep % BASS.length]; playNote(b[0], (b[1]/16)*480, "triangle", 0.35); musicStep++; }
function startMusic() { initAudio(); if (!audioCtx) return; if (audioCtx.state === "suspended") audioCtx.resume(); if (musicTimer) return; musicTimer = setInterval(musicStepRunner, 120); }
function stopMusic() { if (musicTimer) { clearInterval(musicTimer); musicTimer = null; } }
function toggleMusic() { musicEnabled = !musicEnabled; const btn = document.getElementById("music-btn"); if (btn) btn.textContent = musicEnabled ? "🔊 音乐" : "🔇 静音"; if (musicEnabled) startMusic(); else stopMusic(); }
function updatePhantoms() { if (!PHANTOM.enabled || !player.alive) { phantomTrail.length = 0; return; } for (const p of phantomTrail) p.alpha -= PHANTOM.fadeStep; phantomTrail = phantomTrail.filter(p => p.alpha > PHANTOM.minAlpha); while (phantomTrail.length > PHANTOM.maxCount) phantomTrail.shift(); phantomFrame++; const moving = Math.abs(player.vx) > PHANTOM.moveThreshold; const inAir = Math.abs(player.vy) > PHANTOM.jumpThreshold; if ((moving || inAir) && phantomFrame >= PHANTOM.interval) { phantomFrame = 0; phantomTrail.push({ x: player.x, y: player.y, w: player.w, h: player.h, facing: player.facing, alpha: PHANTOM.startAlpha }); } }
function drawPhantoms() { if (!PHANTOM.enabled || phantomTrail.length === 0) return; for (const p of phantomTrail) { const a = Math.max(p.alpha, 0); ctx.fillStyle = "rgba(230,57,70," + a.toFixed(3) + ")"; ctx.fillRect(p.x, p.y, p.w, p.h); ctx.fillStyle = "rgba(255,217,61," + (a * 0.6).toFixed(3) + ")"; ctx.beginPath(); ctx.moveTo(p.x + 5, p.y); ctx.lineTo(p.x + 10, p.y - 10); ctx.lineTo(p.x + 15, p.y); ctx.fill(); ctx.beginPath(); ctx.moveTo(p.x + p.w - 15, p.y); ctx.lineTo(p.x + p.w - 10, p.y - 10); ctx.lineTo(p.x + p.w - 5, p.y); ctx.fill(); } }
 
 document.addEventListener("keydown", e => { keys[e.code] = true; if(["Space","ArrowUp","ArrowDown","ArrowLeft","ArrowRight"].includes(e.code)) e.preventDefault(); });
 document.addEventListener("keyup", e => { keys[e.code] = false; });
 
 const levels = [
   { platforms:[{x:0,y:460,w:800,h:40},{x:200,y:370,w:120,h:20},{x:400,y:290,w:120,h:20},{x:600,y:210,w:120,h:20}], spikes:[{x:350,y:440,w:60,h:20}], movingPlatforms:[], door:{x:680,y:160,w:40,h:50}, start:{x:80,y:400} },
   { platforms:[{x:0,y:460,w:200,h:40},{x:250,y:460,w:150,h:40},{x:500,y:460,w:300,h:40},{x:150,y:370,w:80,h:11},{x:350,y:310,w:100,h:11},{x:550,y:220,w:100,h:11}], spikes:[{x:200,y:440,w:50,h:20},{x:400,y:440,w:50,h:20},{x:550,y:440,w:50,h:20}], movingPlatforms:[], door:{x:680,y:150,w:40,h:50}, start:{x:50,y:400} },
   { platforms:[{x:0,y:460,w:150,h:40},{x:650,y:460,w:150,h:40},{x:300,y:150,w:120,h:20}], spikes:[{x:180,y:440,w:470,h:20}], movingPlatforms:[{x:150,y:380,w:80,h:20,dx:2,minX:150,maxX:350},{x:400,y:300,w:80,h:20,dy:1.5,minY:200,maxY:350}], door:{x:560,y:110,w:40,h:50}, start:{x:50,y:400} },
   { platforms:[{x:0,y:460,w:120,h:40},{x:150,y:460,w:100,h:20},{x:280,y:460,w:100,h:20},{x:410,y:460,w:100,h:20},{x:540,y:460,w:100,h:20},{x:670,y:460,w:130,h:40},{x:200,y:360,w:100,h:20},{x:400,y:280,w:100,h:20}], spikes:[{x:150,y:440,w:530,h:20}], movingPlatforms:[], door:{x:560,y:260,w:40,h:50}, start:{x:40,y:400} },
   { platforms:[{x:0,y:460,w:100,h:40},{x:120,y:380,w:80,h:20},{x:250,y:300,w:80,h:20},{x:310,y:380,w:75,h:20},{x:550,y:280,w:80,h:20},{x:680,y:200,w:120,h:20},{x:300,y:150,w:100,h:20}], spikes:[{x:130,y:440,w:90,h:20},{x:320,y:440,w:80,h:20},{x:500,y:440,w:80,h:20}], movingPlatforms:[{x:450,y:350,w:70,h:20,dy:1.5,minY:250,maxY:430}], door:{x:58,y:66,w:40,h:75}, start:{x:30,y:400} }
 ];
 
 function loadLevel(n) {
   if (n >= levels.length) { showWin(); return; }
   currentLevel = n;
   const L = levels[n];
   player = { x: L.start.x, y: L.start.y, w: 30, h: 30, vx: 0, vy: 0, onGround: false, facing: 1, alive: true, onMoving: null };
   platforms = L.platforms.map((plat,i) => ({...plat, disappeared: false, disappearTimer: 0, trigger: (plat.y >= 440 && i > 0)}));
   spikes = L.spikes.map(s => ({...s}));
   movingPlatforms = L.movingPlatforms.map(mp => ({...mp, currentX: mp.x, currentY: mp.y, dir: 1}));
   door = {...L.door};
   gameWon = false;
   document.getElementById("level-info").textContent = "第 " + (n+1) + " 关 / 共 " + levels.length + " 关";
 }
 
function showWin() {
 gameWon = true; timerRunning = false; totalTime = (Date.now() - startTime) / 1000; sfxWin();
  let bestText = "最快成绩："; let compareText = "";
  if (bestTime === Infinity) {
    bestTime = totalTime; localStorage.setItem("levelDevilBestTime", bestTime.toFixed(2));
    bestText += bestTime.toFixed(2) + " 秒 🎉 新纪录！"; compareText = "这是你的第一次通关！";
  } else if (totalTime < bestTime) {
    const diff = (bestTime - totalTime).toFixed(2);
    bestTime = totalTime; localStorage.setItem("levelDevilBestTime", bestTime.toFixed(2));
    bestText += bestTime.toFixed(2) + " 秒 🎉 新纪录！"; compareText = "比原纪录快 " + diff + " 秒";
  } else if (totalTime > bestTime) {
    const diff = (totalTime - bestTime).toFixed(2);
    bestText += bestTime.toFixed(2) + " 秒"; compareText = "比最快成绩慢 " + diff + " 秒";
  } else {
    bestText += bestTime.toFixed(2) + " 秒"; compareText = "平最快纪录！";
  }
  let deathsText = "死亡次数：" + deathCount + " 次";
  let bestDeathsText = "最少死亡："; let deathsCompareText = "";
  if (bestDeaths === Infinity) {
    bestDeaths = deathCount; localStorage.setItem("levelDevilBestDeaths", bestDeaths);
    bestDeathsText += bestDeaths + " 次 🎉 新纪录！"; deathsCompareText = "第一次通关，少死为赢！";
  } else if (deathCount < bestDeaths) {
    const diff = bestDeaths - deathCount;
    bestDeaths = deathCount; localStorage.setItem("levelDevilBestDeaths", bestDeaths);
    bestDeathsText += bestDeaths + " 次 🎉 新纪录！"; deathsCompareText = "比原纪录少死 " + diff + " 次";
  } else if (deathCount > bestDeaths) {
    const diff = deathCount - bestDeaths;
    bestDeathsText += bestDeaths + " 次"; deathsCompareText = "比最少死亡多 " + diff + " 次";
  } else {
    bestDeathsText += bestDeaths + " 次"; deathsCompareText = "平最少死亡纪录！";
  }
  document.getElementById("win-text").textContent = "🎉 全部通关！你真棒！";
  document.getElementById("win-time").textContent = "通关时间：" + totalTime.toFixed(2) + " 秒";
  document.getElementById("win-best").textContent = bestText;
  document.getElementById("win-compare").textContent = compareText;
  document.getElementById("win-deaths").textContent = deathsText;
  document.getElementById("win-best-deaths").textContent = bestDeathsText;
  document.getElementById("win-deaths-compare").textContent = deathsCompareText;
  document.getElementById("win-screen").classList.add("show");
}
 function updateTimerDisplay() { const bestLabel = bestTime === Infinity ? "--" : bestTime.toFixed(2); document.getElementById("timer").textContent = "时间：" + totalTime.toFixed(2) + " 秒 | 最快：" + bestLabel + " 秒 | 死亡：" + deathCount + " 次"; }
let respawnTimer = 0; const RESPAWN_DELAY_FRAMES = 60; let countdownTimer = 0; const COUNTDOWN_FRAMES = 180;
function respawn() { if (!player.alive) return; pauseStartedAt = Date.now(); sfxDeath(); player.alive = false; respawnTimer = RESPAWN_DELAY_FRAMES; countdownTimer = 0; }
function performRespawn() { if (pauseStartedAt > 0) { startTime += Date.now() - pauseStartedAt; pauseStartedAt = 0; } const L = levels[currentLevel]; player.x = L.start.x; player.y = L.start.y; player.vx = 0; player.vy = 0; player.alive = true; player.onGround = false; player.onMoving = null; deathCount++; updateTimerDisplay(); platforms.forEach(pl => { if(pl.disappeared) { pl.disappeared = false; pl.disappearTimer = 0; }}); }
 function collides(a, b) { return a.x < b.x+b.w && a.x+a.w > b.x && a.y < b.y+b.h && a.y+a.h > b.y; }
 
function update(dt) {
  if (gameWon) return;
  const dtScale = dt * 60;
  if (timerRunning && player.alive) { totalTime = (Date.now() - startTime) / 1000; updateTimerDisplay(); }
updatePhantoms();
  const ml = keys["ArrowLeft"]||keys["KeyA"], mr = keys["ArrowRight"]||keys["KeyD"], jk = keys["Space"]||keys["ArrowUp"]||keys["KeyW"];
  if (ml) { player.vx = -4; player.facing = -1; } else if (mr) { player.vx = 4; player.facing = 1; } else { player.vx *= 0.7; }

  const mpOldX = movingPlatforms.map(mp => mp.currentX);
  const mpOldY = movingPlatforms.map(mp => mp.currentY);

  for (const mp of movingPlatforms) {
    if (mp.dx) { mp.currentX += mp.dx * mp.dir * dtScale; mp.x = mp.currentX; if (mp.currentX <= mp.minX || mp.currentX >= mp.maxX) mp.dir *= -1; }
    if (mp.dy) { mp.currentY += mp.dy * mp.dir * dtScale; mp.y = mp.currentY; if (mp.currentY <= mp.minY || mp.currentY >= mp.maxY) mp.dir *= -1; }
  }

  // 先让玩家跟随当前站立的移动平台移动
  if (player.onMoving !== null) {
    const mp = movingPlatforms[player.onMoving];
    player.x += mp.currentX - mpOldX[player.onMoving];
    player.y += mp.currentY - mpOldY[player.onMoving];
  }

  if (jk && player.onGround) { player.vy = -12; player.onGround = false; player.onMoving = null; sfxJump(); }
  player.vy += GRAVITY * dtScale; if (player.vy > 12) player.vy = 12;

  player.x += player.vx * dtScale;
  if (player.x < 0) player.x = 0;
  if (player.x + player.w > W) player.x = W - player.w;

  // X轴只与静态平台碰撞，避免移动平台把玩家顶下去
  for (const pl of platforms) {
    if (pl.disappeared) continue;
    if (collides(player, pl)) {
      if (player.vx > 0) player.x = pl.x - player.w;
      else if (player.vx < 0) player.x = pl.x + pl.w;
      player.vx = 0;
    }
  }

  player.y += player.vy * dtScale;
  player.onGround = false;
  player.onMoving = null;
  const allP = [...platforms, ...movingPlatforms];
  for (const pl of allP) {
    if (pl.disappeared) continue;
    if (collides(player, pl)) {
      if (player.vy > 0) {
        player.y = pl.y - player.h;
        player.vy = 0;
        player.onGround = true;
        const mpIdx = movingPlatforms.indexOf(pl);
        if (mpIdx >= 0) player.onMoving = mpIdx;
        if (pl.trigger && !pl.disappeared) {
          pl.disappearTimer++;
          if (pl.disappearTimer > 40) pl.disappeared = true;
        }
      } else if (player.vy < 0) {
        player.y = pl.y + pl.h;
        player.vy = 0;
      }
    }
  }
 
  if (player.alive && (player.y > H || spikes.some(s => collides(player, s)))) { respawn(); return; }
  if (!player.alive) { if (respawnTimer > 0) { respawnTimer--; return; } if (countdownTimer === 0) countdownTimer = COUNTDOWN_FRAMES; countdownTimer--; if (countdownTimer > 0) return; performRespawn(); countdownTimer = 0; }
  if (collides(player, door)) { loadLevel(currentLevel + 1); return; }
 }
 
 function draw() {
   const grad = ctx.createLinearGradient(0,0,0,H);
   grad.addColorStop(0,"#16213e"); grad.addColorStop(1,"#0f3460");
   ctx.fillStyle = grad; ctx.fillRect(0,0,W,H);
   for (const p of platforms) {
     if (p.disappeared) continue;
     ctx.globalAlpha = p.disappearTimer > 0 ? 1 - p.disappearTimer/40 : 1;
     ctx.fillStyle = "#537b95"; ctx.fillRect(p.x,p.y,p.w,p.h);
     ctx.fillStyle = "#7ec8e3"; ctx.fillRect(p.x,p.y,p.w,4);
     ctx.globalAlpha = 1;
   }
   for (const mp of movingPlatforms) {
     ctx.fillStyle = "#ffd93d"; ctx.fillRect(mp.currentX,mp.currentY,mp.w,mp.h);
     ctx.fillStyle = "#ff9f1a"; ctx.fillRect(mp.currentX,mp.currentY,mp.w,4);
   }
   for (const s of spikes) {
     ctx.fillStyle = "#ff6b6b";
     const cnt = Math.floor(s.w/15);
     for (let i=0;i<cnt;i++) { const tx=s.x+i*15; ctx.beginPath(); ctx.moveTo(tx,s.y+s.h); ctx.lineTo(tx+7.5,s.y); ctx.lineTo(tx+15,s.y+s.h); ctx.closePath(); ctx.fill(); }
   }
   ctx.fillStyle = "#8b5e3c"; ctx.fillRect(door.x,door.y,door.w,door.h);
   ctx.fillStyle = "#ffd93d"; ctx.fillRect(door.x+5,door.y+5,door.w-10,door.h-10);
  ctx.fillStyle = "#ff6b6b"; ctx.beginPath(); ctx.arc(door.x+door.w-12,door.y+door.h/2,4,0,Math.PI*2); ctx.fill();
  drawPhantoms();
  if (player.alive || respawnTimer > 0) {
    const px=player.x, py=player.y;
    if (!player.alive) ctx.globalAlpha = 0.35;
    ctx.fillStyle = "#ff6b6b"; ctx.fillRect(px,py,player.w,player.h);
     ctx.fillStyle = "white";
     const ex = player.facing > 0 ? px+18 : px+4;
     ctx.beginPath(); ctx.arc(ex,py+10,5,0,Math.PI*2); ctx.arc(ex+(player.facing>0?8:-8),py+10,5,0,Math.PI*2); ctx.fill();
     ctx.fillStyle = "#1a1a2e";
     ctx.beginPath(); ctx.arc(ex+player.facing*2,py+10,2,0,Math.PI*2); ctx.arc(ex+(player.facing>0?8:-8)+player.facing*2,py+10,2,0,Math.PI*2); ctx.fill();
     ctx.fillStyle = "#ffd93d";
    ctx.beginPath(); ctx.moveTo(px+5,py); ctx.lineTo(px+10,py-8); ctx.lineTo(px+15,py); ctx.fill();
    ctx.beginPath(); ctx.moveTo(px+player.w-15,py); ctx.lineTo(px+player.w-10,py-8); ctx.lineTo(px+player.w-5,py); ctx.fill();
    ctx.globalAlpha = 1;
  }
  if (countdownTimer > 0) {
    const sec = Math.ceil(countdownTimer / 60);
    ctx.fillStyle = "rgba(0,0,0,0.55)"; ctx.fillRect(0,0,W,H);
    const cx = W/2, cy = H/2, r = 90;
    ctx.fillStyle = "rgba(26,26,46,0.95)"; ctx.beginPath(); ctx.arc(cx,cy,r,0,Math.PI*2); ctx.fill();
    ctx.strokeStyle = "#ffd93d"; ctx.lineWidth = 5; ctx.stroke();
    ctx.fillStyle = "#ffd93d"; ctx.font = "bold 22px Segoe UI, sans-serif"; ctx.textAlign = "center"; ctx.textBaseline = "middle";
    ctx.fillText("即将重生", cx, cy - 50);
    ctx.fillStyle = "#ffffff"; ctx.font = "bold 80px Segoe UI, sans-serif"; ctx.fillText(sec.toString(), cx, cy + 5);
    ctx.fillStyle = "#9a9ab0"; ctx.font = "16px Segoe UI, sans-serif"; ctx.fillText("请稍候...", cx, cy + 60);
  }
 }
 
 function loop(currentTime) { if (currentTime === undefined) currentTime = performance.now(); let frameDt = (currentTime - lastTime) / 1000; lastTime = currentTime; if (frameDt > MAX_DT) frameDt = MAX_DT; accumulator += frameDt; while (accumulator >= FIXED_DT) { update(FIXED_DT); accumulator -= FIXED_DT; } draw(); requestAnimationFrame(loop); }
 document.getElementById("music-btn").addEventListener("click", toggleMusic);
function tryStartMusic() { startMusic(); window.removeEventListener("keydown", tryStartMusic); document.removeEventListener("click", tryStartMusic); }
window.addEventListener("keydown", tryStartMusic, { once: true });
document.addEventListener("click", tryStartMusic, { once: true });
document.getElementById("restart-btn").addEventListener("click", () => { document.getElementById("win-screen").classList.remove("show"); deathCount=0; startTime = Date.now(); totalTime = 0; timerRunning = true; countdownTimer = 0; pauseStartedAt = 0; loadLevel(0); });
 loadLevel(0); loop();
 </script>
 </body>
 </html>'''
 
 with open(r'e:\ball\xcx games\level-devil-kids\index.html', 'w', encoding='utf8') as f:
     f.write(html)
 print('Written', len(html), 'bytes')
