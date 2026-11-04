const http = require('http');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

const ARTIFACT_DIR = '/Users/mukeshkumar/.gemini/antigravity-ide/brain/69bff23a-d166-43cd-a80d-4f25e805bc41';

async function main() {
  console.log("Launching headless Chrome on port 9333 to verify restored DEVELOPER font...");
  const chromeProcess = spawn(
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    [
      '--headless=new',
      '--remote-debugging-port=9333',
      '--window-size=1280,800',
      '--autoplay-policy=no-user-gesture-required',
      'http://localhost:8080/index.html'
    ]
  );

  await new Promise(r => setTimeout(r, 2200));

  let page;
  for (let i = 0; i < 10; i++) {
    try {
      page = await new Promise((resolve, reject) => {
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
      if (page) break;
    } catch (e) {
      await new Promise(r => setTimeout(r, 500));
    }
  }

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

  await new Promise(r => ws.onopen = r);

  function send(method, params = {}) {
    return new Promise(resolve => {
      const id = msgId++;
      callbacks.set(id, resolve);
      ws.send(JSON.stringify({ id, method, params }));
    });
  }

  await send('Page.enable');
  await send('Runtime.enable');

  async function evaluate(expression) {
    const res = await send('Runtime.evaluate', { expression, returnByValue: true });
    return res.result ? res.result.value : null;
  }

  async function capture(filename) {
    const res = await send('Page.captureScreenshot', { format: 'png' });
    const buf = Buffer.from(res.result.data, 'base64');
    const outPath = path.join(ARTIFACT_DIR, filename);
    fs.writeFileSync(outPath, buf);
    console.log(`Saved screenshot: ${outPath} (${buf.length} bytes)`);
  }

  console.log("Waiting for dots.bin and textures to load...");
  for (let i = 0; i < 40; i++) {
    const loaded = await evaluate('window.isLoaded === true');
    if (loaded) break;
    await new Promise(r => setTimeout(r, 200));
  }

  // 1. Capture clean hero with restored previous DEVELOPER font
  console.log("Capturing restored hero at scrollY = 0...");
  await capture('developer_font_restored_hero.png');

  // 2. Dispatch wheel scroll to reveal photo halfway
  console.log("Scrolling photo halfway...");
  await evaluate(`(() => {
    window.scrollTo({ top: window.innerHeight * 0.45 });
    window.dispatchEvent(new WheelEvent('wheel', { deltaY: 250, bubbles: true }));
  })()`);

  await new Promise(r => setTimeout(r, 400));
  await capture('developer_font_restored_reveal.png');

  console.log("Verification finished successfully!");
  ws.close();
  chromeProcess.kill();
  process.exit(0);
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});
