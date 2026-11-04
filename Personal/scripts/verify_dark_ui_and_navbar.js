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

  // Move mouse to position (600, 400) to activate custom cursor
  await send('Input.dispatchMouseEvent', { type: 'mouseMoved', x: 600, y: 400 });
  await new Promise(r => setTimeout(r, 400));

  // 1. Verify at scrollY = 0: Navbar is HIDDEN, custom cursor is active
  console.log("1. Checking state at scrollY = 0 (Navbar should be HIDDEN)...");
  const navState0 = await evaluate(`({
    scrollY: window.scrollY,
    navbarHasHidden: document.getElementById('navbar').classList.contains('navbar-hidden'),
    navbarOpacity: window.getComputedStyle(document.getElementById('navbar')).opacity,
    cursorDotVisible: window.getComputedStyle(document.getElementById('custom-cursor-dot')).display !== 'none'
  })`);
  console.log("State at scrollY = 0:", navState0);
  await capture('dark_ui_1_hero_navbar_hidden.png');

  // 2. Scroll to 450px (mid-reveal): Navbar should STILL be HIDDEN
  console.log("2. Scrolling to 450px (mid-reveal, navbar should STILL be hidden)...");
  await evaluate(`window.scrollTo(0, 450); window.dispatchEvent(new Event('scroll'));`);
  await new Promise(r => setTimeout(r, 600));
  const navState450 = await evaluate(`({
    scrollY: window.scrollY,
    navbarHasHidden: document.getElementById('navbar').classList.contains('navbar-hidden'),
    navbarOpacity: window.getComputedStyle(document.getElementById('navbar')).opacity
  })`);
  console.log("State at scrollY = 450:", navState450);
  await capture('dark_ui_2_mid_reveal_navbar_hidden.png');

  // 3. Scroll to 800px (photo fully revealed): Still within hero track
  console.log("3. Scrolling to 800px (photo fully revealed)...");
  await evaluate(`window.scrollTo(0, 800); window.dispatchEvent(new Event('scroll'));`);
  await new Promise(r => setTimeout(r, 600));
  await capture('dark_ui_3_photo_revealed.png');

  // 4. Scroll down into Intro Command Center (AFTER photo is scrolled): Navbar should be VISIBLE!
  console.log("4. Scrolling to Intro Section (AFTER photo scrolled, navbar should become VISIBLE)...");
  await evaluate(`document.getElementById('intro').scrollIntoView(); window.dispatchEvent(new Event('scroll'));`);
  await new Promise(r => setTimeout(r, 800));
  const navStateIntro = await evaluate(`({
    scrollY: window.scrollY,
    navbarHasHidden: document.getElementById('navbar').classList.contains('navbar-hidden'),
    navbarOpacity: window.getComputedStyle(document.getElementById('navbar')).opacity
  })`);
  console.log("State at Intro:", navStateIntro);
  await capture('dark_ui_4_intro_navbar_visible.png');

  // 5. Scroll to Projects: check darker screenshots & no yellow/green
  console.log("5. Scrolling to Projects section...");
  await evaluate(`document.getElementById('projects').scrollIntoView();`);
  await new Promise(r => setTimeout(r, 800));
  await capture('dark_ui_5_projects_dark_ui.png');

  // 6. Scroll to Google Skills Badges: check white-greyish certificates
  console.log("6. Scrolling to Google Skills Badges (checking white-greyish certificates)...");
  await evaluate(`document.getElementById('achievements').scrollIntoView();`);
  await new Promise(r => setTimeout(r, 800));
  await capture('dark_ui_6_badges_white_greyish.png');

  // 7. Scroll to AWS Showcase: check no yellow/green
  console.log("7. Scrolling to AWS Showcase...");
  await evaluate(`document.getElementById('aws-showcase').scrollIntoView();`);
  await new Promise(r => setTimeout(r, 800));
  await capture('dark_ui_7_aws_showcase.png');

  // 8. Scroll back to top: Navbar should become HIDDEN again!
  console.log("8. Scrolling back to 0 (navbar should become HIDDEN again)...");
  await evaluate(`window.scrollTo(0, 0); window.dispatchEvent(new Event('scroll'));`);
  await new Promise(r => setTimeout(r, 1000));
  const navStateBack = await evaluate(`({
    scrollY: window.scrollY,
    navbarHasHidden: document.getElementById('navbar').classList.contains('navbar-hidden'),
    navbarOpacity: window.getComputedStyle(document.getElementById('navbar')).opacity
  })`);
  console.log("State back at 0:", navStateBack);
  await capture('dark_ui_8_back_to_top_navbar_hidden.png');

  ws.close();
  chromeProcess.kill();
  console.log("All dark UI, custom cursor, and dynamic navbar tests finished successfully!");
}

main().catch(err => {
  console.error("Test error:", err);
  process.exit(1);
});
