const http = require('http');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

const ARTIFACT_DIR = '/Users/mukeshkumar/.gemini/antigravity-ide/brain/69bff23a-d166-43cd-a80d-4f25e805bc41';

async function main() {
  console.log("Launching headless Chrome on port 9333 to verify gated reveal & Anton font...");
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

  console.log("Waiting for scene and textures to load...");
  for (let i = 0; i < 40; i++) {
    const loaded = await evaluate('window.isLoaded === true');
    if (loaded) break;
    await new Promise(r => setTimeout(r, 200));
  }

  // 1. Initial State (scrollY = 0, locked, navbar hidden, Anton font visible)
  const initState = await evaluate(`(() => {
    return {
      scrollY: window.scrollY,
      isHeroLocked: document.body.classList.contains('hero-locked'),
      navbarHidden: document.getElementById('navbar').classList.contains('navbar-hidden'),
      targetRevealProgress: window.targetRevealProgress
    };
  })()`);
  console.log("1. Initial Hero State:", initState);
  await capture('user_font_1_hero_check.png');

  // 2. Dispatch wheel scroll down to reveal photo partially
  console.log("2. Scrolling down partially...");
  await evaluate(`(() => {
    for (let i = 0; i < 3; i++) {
      window.dispatchEvent(new WheelEvent('wheel', { deltaY: 100, bubbles: true }));
    }
  })()`);

  await new Promise(r => setTimeout(r, 350));

  const partialState = await evaluate(`(() => {
    return {
      scrollY: window.scrollY,
      targetRevealProgress: window.targetRevealProgress,
      revealProgress: window.revealProgress,
      isHeroLocked: document.body.classList.contains('hero-locked'),
      nextPageScrolled: window.scrollY > 0
    };
  })()`);
  console.log("2. Partial Reveal State:", partialState);
  await capture('user_font_2_reveal_in_progress.png');

  // 3. Complete the photo reveal to 100%
  console.log("3. Scrolling to 100% photo reveal...");
  await evaluate(`(() => {
    for (let i = 0; i < 6; i++) {
      window.dispatchEvent(new WheelEvent('wheel', { deltaY: 120, bubbles: true }));
    }
  })()`);

  // Allow lerp to settle to >= 0.98
  await new Promise(r => setTimeout(r, 650));

  const fullyRevealedState = await evaluate(`(() => {
    return {
      scrollY: window.scrollY,
      targetRevealProgress: window.targetRevealProgress,
      revealProgress: window.revealProgress,
      isHeroLocked: document.body.classList.contains('hero-locked'),
      navbarHidden: document.getElementById('navbar').classList.contains('navbar-hidden')
    };
  })()`);
  console.log("3. Photo 100% Revealed State:", fullyRevealedState);
  await capture('user_font_3_photo_fully_revealed.png');

  // 4. Now that photo is 100% revealed, scroll down into the next page
  console.log("4. Scrolling down into next page...");
  await evaluate(`(() => {
    window.scrollTo({ top: 600 });
    window.dispatchEvent(new Event('scroll'));
  })()`);

  await new Promise(r => setTimeout(r, 400));

  const websiteScrolledState = await evaluate(`(() => {
    const intro = document.getElementById('intro');
    const rect = intro ? intro.getBoundingClientRect() : null;
    return {
      scrollY: window.scrollY,
      navbarHidden: document.getElementById('navbar').classList.contains('navbar-hidden'),
      introVisible: rect ? (rect.top < window.innerHeight && rect.bottom > 0) : false
    };
  })()`);
  console.log("4. Website Scrolled State:", websiteScrolledState);
  await capture('user_font_4_website_scrolled.png');

  console.log("Gated reveal verification finished successfully!");
  ws.close();
  chromeProcess.kill();
  process.exit(0);
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});
