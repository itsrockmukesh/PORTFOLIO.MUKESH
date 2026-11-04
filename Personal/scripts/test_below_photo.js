const http = require('http');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

const ARTIFACT_DIR = '/Users/mukeshkumar/.gemini/antigravity-ide/brain/69bff23a-d166-43cd-a80d-4f25e805bc41';

async function main() {
  console.log("Launching headless Chrome on port 9333...");
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

  console.log("Waiting 3.5s for dots.bin & preloader...");
  await new Promise(r => setTimeout(r, 3500));

  async function capture(filename) {
    const res = await send('Page.captureScreenshot', { format: 'png' });
    const buf = Buffer.from(res.result.data, 'base64');
    const outPath = path.join(ARTIFACT_DIR, filename);
    fs.writeFileSync(outPath, buf);
    console.log(`Saved screenshot: ${outPath} (${buf.length} bytes)`);
  }

  async function evaluate(expression) {
    const res = await send('Runtime.evaluate', { expression, returnByValue: true });
    return res.result ? res.result.value : null;
  }

  // 1. Screenshot at scrollY = 0 (clean hero, no overlapping text!)
  console.log("1. Capturing clean hero at scrollY = 0...");
  await capture('below_photo_1_hero_clean.png');

  // 2. Head turn with mouse movement
  console.log("2. Testing cursor head turn...");
  await send('Input.dispatchMouseEvent', { type: 'mouseMoved', x: 920, y: 320 });
  await new Promise(r => setTimeout(r, 500));
  await capture('below_photo_2_head_turn.png');

  // 3. Scroll to 800px (fully revealed photo, still pinned)
  console.log("3. Scrolling to 800px (photo fully revealed)...");
  await evaluate(`window.scrollTo(0, 800); window.dispatchEvent(new Event('scroll'));`);
  await new Promise(r => setTimeout(r, 800));
  await capture('below_photo_3_photo_revealed_clean.png');

  // 4. Scroll down past hero into the intro section ("Hi, I'm Mukesh Kumar")
  console.log("4. Scrolling to Intro section ('Hi, I'm Mukesh Kumar' below photo)...");
  await evaluate(`document.getElementById('intro').scrollIntoView();`);
  await new Promise(r => setTimeout(r, 800));
  await capture('below_photo_4_intro_below_photo.png');

  // 5. Scroll down to projects
  console.log("5. Scrolling to Projects section...");
  await evaluate(`document.getElementById('projects').scrollIntoView();`);
  await new Promise(r => setTimeout(r, 700));
  await capture('below_photo_5_projects.png');

  // 6. Scroll back to top
  console.log("6. Scrolling back to top...");
  await evaluate(`window.scrollTo(0, 0); window.dispatchEvent(new Event('scroll'));`);
  await new Promise(r => setTimeout(r, 900));
  await capture('below_photo_6_back_to_top.png');

  ws.close();
  chromeProcess.kill();
  console.log("Test finished successfully!");
}

main().catch(err => {
  console.error("Test error:", err);
  process.exit(1);
});
