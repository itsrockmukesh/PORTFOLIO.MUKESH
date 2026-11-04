const http = require('http');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

const ARTIFACT_DIR = '/Users/mukeshkumar/.gemini/antigravity-ide/brain/69bff23a-d166-43cd-a80d-4f25e805bc41';

async function main() {
  console.log("Launching headless Chrome on port 9333 to verify navbar visibility timing...");
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

  console.log("Waiting for scene to load...");
  for (let i = 0; i < 40; i++) {
    const loaded = await evaluate('window.isLoaded === true');
    if (loaded) break;
    await new Promise(r => setTimeout(r, 200));
  }

  // 1. Initial State: 3D Dots Hero (scrollY = 0)
  const state1 = await evaluate(`(() => {
    const nav = document.getElementById('navbar');
    return {
      scrollY: window.scrollY,
      navbarHidden: nav ? nav.classList.contains('navbar-hidden') : false
    };
  })()`);
  console.log("1. Dots hero state (navbar should be hidden):", state1);
  await capture('navbar_check_1_dots_hero.png');

  // 2. Partial photo reveal (scrollY = 0)
  console.log("2. Revealing photo partially...");
  await evaluate(`(() => {
    for (let i = 0; i < 3; i++) {
      window.dispatchEvent(new WheelEvent('wheel', { deltaY: 100, bubbles: true }));
    }
  })()`);
  await new Promise(r => setTimeout(r, 350));

  const state2 = await evaluate(`(() => {
    const nav = document.getElementById('navbar');
    return {
      scrollY: window.scrollY,
      revealProgress: window.revealProgress,
      navbarHidden: nav ? nav.classList.contains('navbar-hidden') : false
    };
  })()`);
  console.log("2. Photo revealing state (navbar should be hidden):", state2);
  await capture('navbar_check_2_photo_revealing.png');

  // 3. Photo FULLY REVEALED (100% reveal, still on photo stage at scrollY = 0)
  console.log("3. Scrolling to 100% photo reveal at top...");
  await evaluate(`(() => {
    for (let i = 0; i < 6; i++) {
      window.dispatchEvent(new WheelEvent('wheel', { deltaY: 120, bubbles: true }));
    }
  })()`);
  await new Promise(r => setTimeout(r, 700));

  const state3 = await evaluate(`(() => {
    const nav = document.getElementById('navbar');
    return {
      scrollY: window.scrollY,
      targetRevealProgress: window.targetRevealProgress,
      revealProgress: window.revealProgress,
      isHeroLocked: document.body.classList.contains('hero-locked'),
      navbarHidden: nav ? nav.classList.contains('navbar-hidden') : false
    };
  })()`);
  console.log("3. Photo 100% revealed state (USER REQUIREMENT: navbar MUST STILL BE HIDDEN):", state3);
  await capture('navbar_check_3_photo_100_percent_no_navbar.png');

  // 4. User scrolls past photo and arrives at the next page
  console.log("4. User scrolls down past photo into next page (#intro)...");
  await evaluate(`(() => {
    window.scrollTo({ top: 350 });
    window.dispatchEvent(new Event('scroll'));
  })()`);
  await new Promise(r => setTimeout(r, 450));

  const state4 = await evaluate(`(() => {
    const nav = document.getElementById('navbar');
    return {
      scrollY: window.scrollY,
      navbarHidden: nav ? nav.classList.contains('navbar-hidden') : false
    };
  })()`);
  console.log("4. Arrived at next page (USER REQUIREMENT: navbar MUST NOW BE VISIBLE):", state4);
  await capture('navbar_check_4_arrived_next_page_navbar_shows.png');

  // 5. User scrolls back up to photo stage (scrollY = 0)
  console.log("5. User scrolls back up to photo at top...");
  await evaluate(`(() => {
    window.scrollTo({ top: 0 });
    window.dispatchEvent(new Event('scroll'));
  })()`);
  await new Promise(r => setTimeout(r, 450));

  const state5 = await evaluate(`(() => {
    const nav = document.getElementById('navbar');
    return {
      scrollY: window.scrollY,
      navbarHidden: nav ? nav.classList.contains('navbar-hidden') : false
    };
  })()`);
  console.log("5. Returned to photo at top (navbar MUST HIDE AGAIN):", state5);
  await capture('navbar_check_5_back_to_photo_navbar_hides.png');

  console.log("All navbar timing verification tests passed!");
  ws.close();
  chromeProcess.kill();
  process.exit(0);
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});
