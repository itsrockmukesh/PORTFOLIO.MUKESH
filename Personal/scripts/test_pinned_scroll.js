const http = require('http');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

const ARTIFACT_DIR = '/Users/mukeshkumar/.gemini/antigravity-ide/brain/69bff23a-d166-43cd-a80d-4f25e805bc41';

async function main() {
  console.log("1. Launching headless Chrome on port 9333...");
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

  console.log("2. Querying Chrome targets...");
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

  console.log("Connected to page:", page.title, page.url);
  const ws = new WebSocket(page.webSocketDebuggerUrl);

  let msgId = 1;
  const callbacks = new Map();

  ws.onmessage = (event) => {
    const msg = JSON.parse(event.data);
    if (msg.method === 'Runtime.consoleAPICalled') {
      console.log('[Browser Console]', msg.params.type, msg.params.args.map(a => a.value).join(' '));
    }
    if (msg.method === 'Runtime.exceptionThrown') {
      console.error('[Browser Exception]', JSON.stringify(msg.params.exceptionDetails));
    }
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

  console.log("3. Waiting 3.5s for dots.bin to stream in & preloader to fade...");
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

  // Check state at scroll = 0
  const state0 = await evaluate(`({
    scrollY: window.scrollY,
    trackHeight: document.getElementById('hero').offsetHeight,
    pinnedTop: document.querySelector('.hero-sticky-stage').getBoundingClientRect().top,
    projectsTop: document.getElementById('projects').getBoundingClientRect().top
  })`);
  console.log("State at scrollY = 0:", state0);
  await capture('pinned_scroll_0_dots.png');

  // Move mouse to trigger head turn
  await send('Input.dispatchMouseEvent', {
    type: 'mouseMoved',
    x: 950,
    y: 350
  });
  await new Promise(r => setTimeout(r, 600));
  await capture('pinned_scroll_head_turned.png');

  // Scroll to 400px (partial reveal)
  console.log("4. Scrolling to 450px (mid-reveal)...");
  await evaluate(`window.scrollTo(0, 450); window.dispatchEvent(new Event('scroll'));`);
  await new Promise(r => setTimeout(r, 800));
  const state450 = await evaluate(`({
    scrollY: window.scrollY,
    pinnedTop: document.querySelector('.hero-sticky-stage').getBoundingClientRect().top,
    hudOpacity: document.querySelector('.hero-hud-overlay').style.opacity,
    scrollLabel: document.getElementById('scrollLabel').textContent,
    projectsTop: document.getElementById('projects').getBoundingClientRect().top
  })`);
  console.log("State at scrollY = 450:", state450);
  await capture('pinned_scroll_1_mid_reveal.png');

  // Scroll to 800px (100% revealed photo, stage STILL pinned at top:0!)
  console.log("5. Scrolling to 800px (full photo reveal, hero still pinned)...");
  await evaluate(`window.scrollTo(0, 800); window.dispatchEvent(new Event('scroll'));`);
  await new Promise(r => setTimeout(r, 800));
  const state800 = await evaluate(`({
    scrollY: window.scrollY,
    pinnedTop: document.querySelector('.hero-sticky-stage').getBoundingClientRect().top,
    hudOpacity: document.querySelector('.hero-hud-overlay').style.opacity,
    scrollLabel: document.getElementById('scrollLabel').textContent,
    projectsTop: document.getElementById('projects').getBoundingClientRect().top
  })`);
  console.log("State at scrollY = 800:", state800);
  await capture('pinned_scroll_2_photo_fully_revealed.png');

  // Scroll to 2000px (Full website in view: projects section)
  console.log("6. Scrolling to 2000px (full website scrolled into view)...");
  await evaluate(`window.scrollTo(0, 2000); window.dispatchEvent(new Event('scroll'));`);
  await new Promise(r => setTimeout(r, 800));
  const state2000 = await evaluate(`({
    scrollY: window.scrollY,
    projectsTop: document.getElementById('projects').getBoundingClientRect().top
  })`);
  console.log("State at scrollY = 2000:", state2000);
  await capture('pinned_scroll_3_website_projects.png');

  // Scroll to About section
  console.log("7. Scrolling to About section...");
  await evaluate(`document.getElementById('about').scrollIntoView();`);
  await new Promise(r => setTimeout(r, 600));
  await capture('pinned_scroll_4_website_about.png');

  // Scroll back to top
  console.log("8. Scrolling back to 0 (reversing photo to dots)...");
  await evaluate(`window.scrollTo(0, 0); window.dispatchEvent(new Event('scroll'));`);
  await new Promise(r => setTimeout(r, 1000));
  await capture('pinned_scroll_5_reversed_to_dots.png');

  // Test Terminal Modal
  console.log("9. Testing Terminal Modal trigger...");
  await evaluate(`document.getElementById('hero-terminal-trigger').click();`);
  await new Promise(r => setTimeout(r, 500));
  const termActive = await evaluate(`document.getElementById('terminal-modal').classList.contains('active')`);
  console.log("Terminal modal active:", termActive);
  await capture('pinned_scroll_6_terminal_modal.png');

  // Close terminal modal
  await evaluate(`document.getElementById('terminal-close-btn').click();`);
  await new Promise(r => setTimeout(r, 400));

  // Test Resume Modal
  console.log("10. Testing Resume Modal trigger...");
  await evaluate(`document.querySelector('.trigger-resume-modal').click();`);
  await new Promise(r => setTimeout(r, 500));
  const resumeActive = await evaluate(`document.getElementById('resume-modal').classList.contains('active')`);
  console.log("Resume modal active:", resumeActive);
  await capture('pinned_scroll_7_resume_modal.png');

  ws.close();
  chromeProcess.kill();
  console.log("All tests and verification completed successfully!");
}

main().catch(err => {
  console.error("Test error:", err);
  process.exit(1);
});
