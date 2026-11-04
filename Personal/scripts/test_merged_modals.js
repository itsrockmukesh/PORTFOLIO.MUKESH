const http = require('http');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

const ARTIFACT_DIR = '/Users/mukeshkumar/.gemini/antigravity-ide/brain/69bff23a-d166-43cd-a80d-4f25e805bc41';

async function main() {
  const chromeProcess = spawn(
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    [
      '--headless=new',
      '--remote-debugging-port=9333',
      '--window-size=1280,850',
      'http://localhost:8080/index.html'
    ]
  );

  await new Promise(r => setTimeout(r, 2000));

  const page = await new Promise((resolve, reject) => {
    http.get('http://localhost:9333/json', res => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        const list = JSON.parse(data);
        const p = list.find(x => x.type === 'page');
        resolve(p);
      });
    }).on('error', reject);
  });

  const ws = new WebSocket(page.webSocketDebuggerUrl);
  let msgId = 1;
  const callbacks = new Map();

  ws.onmessage = (event) => {
    const msg = JSON.parse(event.data);
    if (msg.id && callbacks.has(msg.id)) {
      const cb = callbacks.get(msg.id);
      callbacks.delete(msg.id);
      cb(msg);
    }
  };

  function sendCommand(method, params = {}) {
    return new Promise((resolve) => {
      const id = msgId++;
      callbacks.set(id, resolve);
      ws.send(JSON.stringify({ id, method, params }));
    });
  }

  await new Promise(r => ws.onopen = r);
  await sendCommand('Page.enable');
  await sendCommand('Runtime.enable');

  await new Promise(r => setTimeout(r, 4500));

  // 1. Open Cyber Hack modal via button
  console.log("Opening Cyber Hack modal...");
  await sendCommand('Runtime.evaluate', {
    expression: "document.getElementById('hero-hack-trigger').click();"
  });
  await new Promise(r => setTimeout(r, 800));

  let res = await sendCommand('Page.captureScreenshot', { format: 'png' });
  if (res.result && res.result.data) {
    fs.writeFileSync(path.join(ARTIFACT_DIR, 'merged_cyber_hack_modal.png'), Buffer.from(res.result.data, 'base64'));
    console.log("Saved merged_cyber_hack_modal.png");
  }

  // 2. Click Secret Bypass Tool to unlock Terminal
  console.log("Equipping Secret Bypass Tool to unlock terminal...");
  await sendCommand('Runtime.evaluate', {
    expression: "document.getElementById('equip-secret-tool-btn').click();"
  });
  await new Promise(r => setTimeout(r, 1400));

  res = await sendCommand('Page.captureScreenshot', { format: 'png' });
  if (res.result && res.result.data) {
    fs.writeFileSync(path.join(ARTIFACT_DIR, 'merged_terminal_modal.png'), Buffer.from(res.result.data, 'base64'));
    console.log("Saved merged_terminal_modal.png");
  }

  ws.close();
  chromeProcess.kill();
  console.log("Modal checks complete!");
  process.exit(0);
}

main().catch(err => {
  console.error("Modal test error:", err);
  process.exit(1);
});
