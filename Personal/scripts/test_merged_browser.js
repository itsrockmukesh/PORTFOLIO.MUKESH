const http = require('http');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

const ARTIFACT_DIR = '/Users/mukeshkumar/.gemini/antigravity-ide/brain/69bff23a-d166-43cd-a80d-4f25e805bc41';

async function main() {
  console.log("Launching Chrome headless=new on port 9333...");
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

  console.log("Found page target:", page.title, page.webSocketDebuggerUrl);
  const ws = new WebSocket(page.webSocketDebuggerUrl);

  let msgId = 1;
  const callbacks = new Map();

  ws.onmessage = (event) => {
    const msg = JSON.parse(event.data);
    if (msg.method === 'Runtime.consoleAPICalled') {
      console.log(`[Browser Console ${msg.params.type}]:`, msg.params.args.map(a => a.value || a.description).join(' '));
    }
    if (msg.method === 'Runtime.exceptionThrown') {
      console.error('[Browser Exception]:', msg.params.exceptionDetails.text, msg.params.exceptionDetails.exception?.description);
    }
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

  // Wait 4.5s for dots to fly from preloader ring and sweep
  console.log("Waiting 4.5s for preloader and dots entrance...");
  await new Promise(r => setTimeout(r, 4500));

  // Capture Hero State with 3D dots
  console.log("Capturing 3D dots hero state...");
  let res = await sendCommand('Page.captureScreenshot', { format: 'png' });
  if (res.result && res.result.data) {
    fs.writeFileSync(path.join(ARTIFACT_DIR, 'merged_hero_3d_dots.png'), Buffer.from(res.result.data, 'base64'));
    console.log("Saved merged_hero_3d_dots.png");
  }

  // Scroll down halfway to trigger reveal
  console.log("Scrolling down 650px to trigger photo reveal...");
  await sendCommand('Runtime.evaluate', {
    expression: "window.scrollTo({ top: 650, behavior: 'smooth' });"
  });
  await new Promise(r => setTimeout(r, 1200));

  res = await sendCommand('Page.captureScreenshot', { format: 'png' });
  if (res.result && res.result.data) {
    fs.writeFileSync(path.join(ARTIFACT_DIR, 'merged_hero_photo_revealed.png'), Buffer.from(res.result.data, 'base64'));
    console.log("Saved merged_hero_photo_revealed.png");
  }

  // Scroll further down into About & Skills sections
  console.log("Scrolling down to About Me section (1450px)...");
  await sendCommand('Runtime.evaluate', {
    expression: "window.scrollTo({ top: 1450, behavior: 'smooth' });"
  });
  await new Promise(r => setTimeout(r, 1200));

  res = await sendCommand('Page.captureScreenshot', { format: 'png' });
  if (res.result && res.result.data) {
    fs.writeFileSync(path.join(ARTIFACT_DIR, 'merged_about_section.png'), Buffer.from(res.result.data, 'base64'));
    console.log("Saved merged_about_section.png");
  }

  // Scroll further down to Projects Bento Grid (2500px)
  console.log("Scrolling down to Projects section (2500px)...");
  await sendCommand('Runtime.evaluate', {
    expression: "window.scrollTo({ top: 2500, behavior: 'smooth' });"
  });
  await new Promise(r => setTimeout(r, 1200));

  res = await sendCommand('Page.captureScreenshot', { format: 'png' });
  if (res.result && res.result.data) {
    fs.writeFileSync(path.join(ARTIFACT_DIR, 'merged_projects_section.png'), Buffer.from(res.result.data, 'base64'));
    console.log("Saved merged_projects_section.png");
  }

  ws.close();
  chromeProcess.kill();
  console.log("All merged screenshots captured successfully!");
  process.exit(0);
}

main().catch(err => {
  console.error("Test error:", err);
  process.exit(1);
});
