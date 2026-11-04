const http = require('http');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

const ARTIFACT_DIR = '/Users/mukeshkumar/.gemini/antigravity-ide/brain/69bff23a-d166-43cd-a80d-4f25e805bc41';

async function main() {
  console.log("Launching Chrome with remote debugging on port 9333...");
  const chromeProcess = spawn(
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    [
      '--headless=new',
      '--remote-debugging-port=9333',
      '--window-size=1280,800',
      'http://localhost:8080/index.html'
    ]
  );

  // Wait 2 seconds for Chrome to bind
  await new Promise(r => setTimeout(r, 2000));

  // Query /json/version or /json to find page target
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

  console.log("Found page target:", page.title, page.webSocketDebuggerUrl);
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
  console.log("WebSocket connected to CDP");

  await sendCommand('Page.enable');
  await sendCommand('Runtime.enable');

  // Wait 4 seconds for dots to load, fly into place from preloader ring, and sweep
  console.log("Waiting 4.5 seconds for dots entrance & sweep...");
  await new Promise(r => setTimeout(r, 4500));

  // Capture hero state screenshot
  console.log("Capturing 3D dots hero screenshot...");
  let res = await sendCommand('Page.captureScreenshot', { format: 'png' });
  if (res.result && res.result.data) {
    const buf = Buffer.from(res.result.data, 'base64');
    fs.writeFileSync(path.join(ARTIFACT_DIR, 'step6_webgl_dots_hero.png'), buf);
    console.log("Saved step6_webgl_dots_hero.png");
  }

  // Move cursor to upper right to trigger head swivel (up to 30 deg) and cursor lighting
  console.log("Simulating cursor move to upper right (head turn & cursor light)...");
  await sendCommand('Runtime.evaluate', {
    expression: `
      window.dispatchEvent(new MouseEvent('mousemove', {
        clientX: 1050,
        clientY: 220
      }));
    `
  });
  await new Promise(r => setTimeout(r, 1200));

  res = await sendCommand('Page.captureScreenshot', { format: 'png' });
  if (res.result && res.result.data) {
    const buf = Buffer.from(res.result.data, 'base64');
    fs.writeFileSync(path.join(ARTIFACT_DIR, 'step6_head_turn_cursor.png'), buf);
    console.log("Saved step6_head_turn_cursor.png");
  }

  // Scroll down halfway to trigger active scroll reveal transition
  console.log("Simulating wheel scroll down halfway...");
  await sendCommand('Runtime.evaluate', {
    expression: `
      window.dispatchEvent(new WheelEvent('wheel', { deltaY: 420 }));
    `
  });

  // Wait 1.0s for smooth scroll easing
  console.log("Waiting 1.0s for scroll transition easing...");
  await new Promise(r => setTimeout(r, 1000));

  res = await sendCommand('Page.captureScreenshot', { format: 'png' });
  if (res.result && res.result.data) {
    const buf = Buffer.from(res.result.data, 'base64');
    fs.writeFileSync(path.join(ARTIFACT_DIR, 'step7_reveal_transition.png'), buf);
    console.log("Saved step7_reveal_transition.png");
  }

  // Scroll down fully to complete photo reveal
  console.log("Simulating wheel scroll to 100% reveal...");
  await sendCommand('Runtime.evaluate', {
    expression: `
      window.dispatchEvent(new WheelEvent('wheel', { deltaY: 550 }));
    `
  });
  await new Promise(r => setTimeout(r, 1200));

  res = await sendCommand('Page.captureScreenshot', { format: 'png' });
  if (res.result && res.result.data) {
    const buf = Buffer.from(res.result.data, 'base64');
    fs.writeFileSync(path.join(ARTIFACT_DIR, 'step7_reveal_photo.png'), buf);
    console.log("Saved step7_reveal_photo.png");
  }

  // Scroll back up to reverse to 3D dots
  console.log("Simulating wheel scroll back up to reverse...");
  await sendCommand('Runtime.evaluate', {
    expression: `
      window.dispatchEvent(new WheelEvent('wheel', { deltaY: -1200 }));
    `
  });
  await new Promise(r => setTimeout(r, 1200));

  res = await sendCommand('Page.captureScreenshot', { format: 'png' });
  if (res.result && res.result.data) {
    const buf = Buffer.from(res.result.data, 'base64');
    fs.writeFileSync(path.join(ARTIFACT_DIR, 'step7_reversed_dots.png'), buf);
    console.log("Saved step7_reversed_dots.png");
  }

  ws.close();
  chromeProcess.kill();
  console.log("All browser screenshots captured successfully!");
  process.exit(0);
}

main().catch(err => {
  console.error("CDP automation error:", err);
  process.exit(1);
});
