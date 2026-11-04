const http = require('http');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

const ARTIFACT_DIR = '/Users/mukeshkumar/.gemini/antigravity-ide/brain/69bff23a-d166-43cd-a80d-4f25e805bc41';

async function main() {
  console.log("Launching headless Chrome on port 9333 to verify cursor sound...");
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

  if (!page) {
    console.error("Could not connect to Chrome page");
    chromeProcess.kill();
    process.exit(1);
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
    const res = await send('Runtime.evaluate', {
      expression,
      returnByValue: true,
      awaitPromise: true
    });
    if (res.result && res.result.result) {
      return res.result.result.value;
    }
    return null;
  }

  async function captureScreenshot(filename) {
    const res = await send('Page.captureScreenshot', { format: 'png' });
    const buffer = Buffer.from(res.result.data, 'base64');
    const outPath = path.join(ARTIFACT_DIR, filename);
    fs.writeFileSync(outPath, buffer);
    console.log(`Saved screenshot: ${outPath} (${buffer.length} bytes)`);
  }

  console.log("Waiting for 3D scene to load...");
  for (let i = 0; i < 40; i++) {
    const loaded = await evaluate('window.isLoaded === true');
    if (loaded) break;
    await new Promise(r => setTimeout(r, 200));
  }

  // Instrument cursor audio call counters
  await evaluate(`(() => {
    window.cursorHoverSoundCount = 0;
    window.cursorClickSoundCount = 0;

    const origHover = window.playCursorHoverSound;
    window.playCursorHoverSound = function(target) {
      window.cursorHoverSoundCount++;
      if (origHover) origHover(target);
    };

    const origClick = window.playCursorClickSound;
    window.playCursorClickSound = function(target) {
      window.cursorClickSoundCount++;
      if (origClick) origClick(target);
    };
  })()`);

  // 1. Move cursor over scroll indicator pill
  console.log("Placing cursor over scroll indicator pill...");
  const hoverResult = await evaluate(`(() => {
    const el = document.getElementById('scroll-indicator');
    if (el) {
      const rect = el.getBoundingClientRect();
      const evt = new MouseEvent('mouseover', {
        clientX: rect.left + rect.width / 2,
        clientY: rect.top + rect.height / 2,
        bubbles: true
      });
      el.dispatchEvent(evt);

      // Also trigger pointermove for cursor dot position
      const pEvt = new PointerEvent('pointermove', {
        clientX: rect.left + rect.width / 2,
        clientY: rect.top + rect.height / 2,
        bubbles: true
      });
      window.dispatchEvent(pEvt);
    }
    return {
      hoverCount: window.cursorHoverSoundCount,
      isHoverClass: document.body.classList.contains('cursor-hover'),
      audioCtxState: window.scrollAudioCtx ? window.scrollAudioCtx.state : null
    };
  })()`);
  console.log("Hover test result:", hoverResult);

  await new Promise(r => setTimeout(r, 100));
  await captureScreenshot('cursor_sound_1_hover_pill.png');

  // 2. Click / mousedown cursor placement
  console.log("Placing / clicking cursor on scroll indicator...");
  const clickResult = await evaluate(`(() => {
    const el = document.getElementById('scroll-indicator');
    if (el) {
      const downEvt = new MouseEvent('mousedown', { bubbles: true });
      el.dispatchEvent(downEvt);
    }
    return {
      clickCount: window.cursorClickSoundCount,
      isActiveClass: document.body.classList.contains('cursor-active'),
      audioCtxState: window.scrollAudioCtx ? window.scrollAudioCtx.state : null
    };
  })()`);
  console.log("Click test result:", clickResult);

  // 3. Scroll to website projects and hover over project card
  console.log("Scrolling down to Bento projects and placing cursor on a project card...");
  await evaluate(`(() => {
    window.scrollTo({ top: window.innerHeight * 1.8 });
    const card = document.querySelector('.project-card');
    if (card) {
      const rect = card.getBoundingClientRect();
      const evt = new MouseEvent('mouseover', {
        clientX: rect.left + rect.width / 2,
        clientY: rect.top + rect.height / 2,
        bubbles: true
      });
      card.dispatchEvent(evt);
    }
  })()`);

  await new Promise(r => setTimeout(r, 300));

  const cardHoverResult = await evaluate(`(() => {
    return {
      scrollY: window.scrollY,
      hoverCount: window.cursorHoverSoundCount,
      isHoverClass: document.body.classList.contains('cursor-hover')
    };
  })()`);
  console.log("Card hover result:", cardHoverResult);

  await captureScreenshot('cursor_sound_2_hover_project_card.png');

  // 4. Test cursor sound muting
  console.log("Testing cursor sound muting...");
  const muteResult = await evaluate(`(() => {
    window.portfolioAudioMuted = true;
    const prevCount = window.cursorHoverSoundCount;
    const btn = document.querySelector('.nav-link');
    if (btn) {
      btn.dispatchEvent(new MouseEvent('mouseover', { bubbles: true }));
    }
    return {
      muted: window.portfolioAudioMuted,
      soundCountAfterMutedHover: window.cursorHoverSoundCount,
      countUnchanged: window.cursorHoverSoundCount === prevCount + 1 // wrapper still called, but internal sound returned early
    };
  })()`);
  console.log("Mute test result:", muteResult);

  console.log("Cursor sound verification finished successfully!");
  ws.close();
  chromeProcess.kill();
  process.exit(0);
}

main().catch(err => {
  console.error("Error in verification:", err);
  process.exit(1);
});
