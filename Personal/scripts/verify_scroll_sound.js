const http = require('http');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

const ARTIFACT_DIR = '/Users/mukeshkumar/.gemini/antigravity-ide/brain/69bff23a-d166-43cd-a80d-4f25e805bc41';

async function main() {
  console.log("Launching headless Chrome on port 9333 with no autoplay restrictions...");
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

  console.log("Waiting for 3D dots & photo textures to load...");
  let loaded = false;
  for (let i = 0; i < 40; i++) {
    loaded = await evaluate('window.isLoaded === true');
    if (loaded) break;
    await new Promise(r => setTimeout(r, 200));
  }
  console.log("isLoaded state:", loaded);

  // 1. Check initial state at scrollY = 0
  const initialStatus = await evaluate(`(() => {
    const nav = document.getElementById('navbar');
    const cursorDot = document.getElementById('custom-cursor-dot');
    const cursorRing = document.getElementById('custom-cursor-ring');
    const hasHiddenClass = nav ? nav.classList.contains('navbar-hidden') : false;
    return {
      scrollY: window.scrollY,
      navbarHidden: hasHiddenClass,
      hasCustomCursor: !!(cursorDot && cursorRing),
      audioCtxReady: !!window.scrollAudioCtx
    };
  })()`);
  console.log("Initial state (top):", initialStatus);

  await captureScreenshot('scroll_sound_1_at_top.png');

  // 2. Dispatch wheel scroll event to trigger photo reveal and scroll sound
  console.log("Simulating wheel event to scroll photo...");
  await evaluate(`(() => {
    // Unlock AudioContext and trigger wheel event
    const wheelEvt = new WheelEvent('wheel', { deltaY: 300, bubbles: true });
    window.dispatchEvent(wheelEvt);
    window.scrollTo({ top: window.innerHeight * 0.45 });
  })()`);

  await new Promise(r => setTimeout(r, 350));

  // Inspect sound engine during photo scroll
  const scrollingAudioStatus = await evaluate(`(() => {
    const ctx = window.scrollAudioCtx;
    return {
      audioCtxExists: !!ctx,
      audioCtxState: ctx ? ctx.state : null,
      revealProgress: window.revealProgress,
      targetRevealProgress: window.targetRevealProgress,
      osc1Freq: window.scrollOsc1 ? window.scrollOsc1.frequency.value : null,
      osc2Freq: window.scrollOsc2 ? window.scrollOsc2.frequency.value : null,
      filterFreq: window.scrollFilter ? window.scrollFilter.frequency.value : null,
      gainValue: window.scrollDroneGain ? window.scrollDroneGain.gain.value : null,
      isChimePlayed: window.isChimePlayed
    };
  })()`);
  console.log("Scrolling photo audio state:", scrollingAudioStatus);

  await captureScreenshot('scroll_sound_2_scrolling_photo.png');

  // 3. Scroll to 100% photo reveal
  console.log("Scrolling to 100% photo reveal (1.0vh)...");
  await evaluate(`(() => {
    window.scrollTo({ top: window.innerHeight * 1.05 });
    const wheelEvt = new WheelEvent('wheel', { deltaY: 100, bubbles: true });
    window.dispatchEvent(wheelEvt);
  })()`);

  await new Promise(r => setTimeout(r, 500));

  const fullyRevealedStatus = await evaluate(`(() => {
    const nav = document.getElementById('navbar');
    const isNavHidden = nav ? nav.classList.contains('navbar-hidden') : false;
    return {
      scrollY: window.scrollY,
      revealProgress: window.revealProgress,
      isChimePlayed: window.isChimePlayed,
      navbarHidden: isNavHidden,
      gainValue: window.scrollDroneGain ? window.scrollDroneGain.gain.value : null
    };
  })()`);
  console.log("100% photo revealed state:", fullyRevealedStatus);

  await captureScreenshot('scroll_sound_3_photo_complete.png');

  // 4. Scroll further down into the website sections
  console.log("Scrolling down to Intro section...");
  await evaluate(`(() => {
    const intro = document.getElementById('intro');
    if (intro) intro.scrollIntoView();
    else window.scrollTo({ top: window.innerHeight * 2.5 });
  })()`);

  await new Promise(r => setTimeout(r, 400));

  const websiteScrolledStatus = await evaluate(`(() => {
    const nav = document.getElementById('navbar');
    const ui = document.getElementById('ui-container');
    return {
      scrollY: window.scrollY,
      navbarHidden: nav ? nav.classList.contains('navbar-hidden') : false,
      uiContainerOpacity: ui ? ui.style.opacity : null,
      gainValue: window.scrollDroneGain ? window.scrollDroneGain.gain.value : null
    };
  })()`);
  console.log("Website scrolled state:", websiteScrolledStatus);

  await captureScreenshot('scroll_sound_4_website_scrolled.png');

  // 5. Test Audio Mute button
  console.log("Testing audio mute button in navbar...");
  const muteTestResult = await evaluate(`(() => {
    const btn = document.getElementById('sound-toggle-btn');
    if (btn) btn.click();
    return {
      portfolioAudioMuted: window.portfolioAudioMuted,
      btnHasMutedClass: btn ? btn.classList.contains('muted') : false,
      gainValue: window.scrollDroneGain ? window.scrollDroneGain.gain.value : null
    };
  })()`);
  console.log("Audio mute test result:", muteTestResult);

  // Unmute back for user
  await evaluate(`(() => {
    const btn = document.getElementById('sound-toggle-btn');
    if (btn) btn.click();
  })()`);

  console.log("Verification finished successfully!");
  ws.close();
  chromeProcess.kill();
  process.exit(0);
}

main().catch(err => {
  console.error("Error in verification:", err);
  process.exit(1);
});
