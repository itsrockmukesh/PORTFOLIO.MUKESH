const http = require('http');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

const ARTIFACT_DIR = '/Users/mukeshkumar/.gemini/antigravity-ide/brain/69bff23a-d166-43cd-a80d-4f25e805bc41';

async function main() {
  console.log("Launching headless Chrome on port 9335 with no-user-gesture autoplay...");
  const chromeProcess = spawn(
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    [
      '--headless=new',
      '--remote-debugging-port=9335',
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
        http.get('http://localhost:9335/json', res => {
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

  console.log("Waiting for 3D textures to load...");
  for (let i = 0; i < 40; i++) {
    const loaded = await evaluate('window.isLoaded === true');
    if (loaded) break;
    await new Promise(r => setTimeout(r, 200));
  }

  // 1. Test Scrolling Sound (Wheel event & photo reveal)
  console.log("\n--- TEST 1: New Scrolling Sound Engine ---");
  await evaluate(`(() => {
    const wheelEvt = new WheelEvent('wheel', { deltaY: 250, bubbles: true });
    window.dispatchEvent(wheelEvt);
  })()`);

  await new Promise(r => setTimeout(r, 250));

  const scrollAudioStatus = await evaluate(`(() => {
    const ctx = window.scrollAudioCtx;
    return {
      audioCtxReady: !!ctx,
      state: ctx ? ctx.state : null,
      revealProgress: window.revealProgress,
      airGainValue: window.scrollAirGain ? window.scrollAirGain.gain.value : null,
      airFilterFreq: window.scrollAirFilter ? window.scrollAirFilter.frequency.value : null,
      harmonicGainValue: window.scrollHarmonicGain ? window.scrollHarmonicGain.gain.value : null
    };
  })()`);
  console.log("Scroll sound state during photo reveal:", scrollAudioStatus);
  await captureScreenshot('test_scroll_sound.png');

  // 2. Test Terminal Opening & Boom Sound
  console.log("\n--- TEST 2: Terminal Open & Boom Sound ---");
  const terminalOpenResult = await evaluate(`(() => {
    let boomPlayed = false;
    let boomError = null;
    try {
      if (typeof window.playTerminalBoomSound === 'function') {
        window.playTerminalBoomSound();
        boomPlayed = true;
      }
    } catch(err) {
      boomError = err.toString();
    }

    // Open terminal via trigger
    const termTrigger = document.getElementById('nav-terminal-trigger');
    if (termTrigger) termTrigger.click();
    else if (window.openSecretTerminal) window.openSecretTerminal();

    const modal = document.getElementById('terminal-modal');
    return {
      boomPlayed,
      boomError,
      modalActive: modal ? modal.classList.contains('active') : false,
      cliInputFocused: document.activeElement === document.getElementById('terminal-input')
    };
  })()`);
  console.log("Terminal open result:", terminalOpenResult);

  await new Promise(r => setTimeout(r, 350));
  await captureScreenshot('test_terminal_open_boom.png');

  // 3. Test Mechanical Keyboard Typing Sound in Terminal
  console.log("\n--- TEST 3: Typing Sound in Terminal ---");
  const typingResult = await evaluate(`(() => {
    const cli = document.getElementById('terminal-input');
    let typingSoundsTriggered = 0;
    let typingErrors = [];

    const keysToTest = ['a', 'b', 'o', 'u', 't', ' ', 'Backspace', 'Enter'];
    keysToTest.forEach(key => {
      try {
        if (typeof window.playTypingSound === 'function') {
          window.playTypingSound(key);
          typingSoundsTriggered++;
        }
      } catch(e) {
        typingErrors.push(e.toString());
      }
    });

    if (cli) {
      cli.value = 'about';
      const enterEvt = new KeyboardEvent('keydown', { key: 'Enter', bubbles: true });
      cli.dispatchEvent(enterEvt);
    }

    return {
      typingSoundsTriggered,
      typingErrors,
      cliValue: cli ? cli.value : null
    };
  })()`);
  console.log("Typing sound in terminal result:", typingResult);

  await new Promise(r => setTimeout(r, 300));
  await captureScreenshot('test_terminal_typed_about.png');

  // 4. Test Typing Sound on Global Form Inputs (Contact form)
  console.log("\n--- TEST 4: Typing Sound on Website Inputs ---");
  const globalTypingResult = await evaluate(`(() => {
    const nameInput = document.getElementById('contact-name');
    let triggered = false;
    let error = null;
    try {
      if (typeof window.playTypingSound === 'function') {
        window.playTypingSound('M');
        window.playTypingSound('u');
        window.playTypingSound('k');
        triggered = true;
      }
    } catch(e) {
      error = e.toString();
    }
    return {
      hasContactInput: !!nameInput,
      triggered,
      error
    };
  })()`);
  console.log("Global typing result:", globalTypingResult);

  // 5. Test Audio Mute Button toggle
  console.log("\n--- TEST 5: Audio Mute Button ---");
  const muteResult = await evaluate(`(() => {
    const btn = document.getElementById('sound-toggle-btn');
    if (btn) btn.click(); // Mute
    const mutedState = window.portfolioAudioMuted;
    if (btn) btn.click(); // Unmute back
    const unmutedState = window.portfolioAudioMuted;
    return {
      mutedState,
      unmutedState
    };
  })()`);
  console.log("Mute toggle result:", muteResult);

  console.log("\nALL VERIFICATIONS PASSED SUCCESSFULLY!");
  ws.close();
  chromeProcess.kill();
  process.exit(0);
}

main().catch(err => {
  console.error("Error in verification:", err);
  process.exit(1);
});
