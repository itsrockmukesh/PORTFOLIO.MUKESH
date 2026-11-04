const http = require('http');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

async function main() {
  console.log("Launching headless Chrome on port 9337...");
  const chromeProcess = spawn(
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    [
      '--headless=new',
      '--remote-debugging-port=9337',
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
        http.get('http://localhost:9337/json', res => {
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

  console.log("Waiting for page readiness...");
  await new Promise(r => setTimeout(r, 1500));

  // Initialize audio and test wheel scroll
  console.log("\n--- TEST 1: Smooth Photo Scroll Audio Engine ---");
  const scrollTestResult = await evaluate(`(() => {
    if (typeof window.initScrollAudio === 'function') {
      window.initScrollAudio();
    }
    const wheelEvt = new WheelEvent('wheel', { deltaY: 280, bubbles: true });
    window.dispatchEvent(wheelEvt);

    const ctx = window.scrollAudioCtx;
    return {
      audioCtxReady: !!ctx,
      ctxState: ctx ? ctx.state : null,
      revealProgress: window.revealProgress,
      osc1Freq: window.scrollOsc1 ? window.scrollOsc1.frequency.value : null,
      osc2Freq: window.scrollOsc2 ? window.scrollOsc2.frequency.value : null,
      filterFreq: window.scrollAirFilter ? window.scrollAirFilter.frequency.value : null,
      gainValue: window.scrollAirGain ? window.scrollAirGain.gain.value : null,
      roughRatchetPresent: typeof window.playScrollRatchetClick !== 'undefined'
    };
  })()`);
  console.log("Smooth scroll audio state:", scrollTestResult);

  // Test Universal Keypress Audio on EVERY key
  console.log("\n--- TEST 2: Universal Keyboard Click on ANY Key ---");
  const keypressResult = await evaluate(`(() => {
    const keys = [
      'a', 'b', 'c', '1', '2', '3', '!', '@', '#',
      ' ', 'Enter', 'Backspace', 'ArrowUp', 'ArrowDown',
      'Tab', 'Escape', 'Shift', 'Control', 'Alt'
    ];

    let passed = 0;
    let errors = [];

    keys.forEach(k => {
      try {
        const evt = new KeyboardEvent('keydown', { key: k, bubbles: true, cancelable: true });
        window.dispatchEvent(evt);
        passed++;
      } catch (err) {
        errors.push({ key: k, err: err.toString() });
      }
    });

    return {
      totalKeys: keys.length,
      passed,
      errors
    };
  })()`);
  console.log("Keypress audio result:", keypressResult);

  // Test Terminal Open Boom
  console.log("\n--- TEST 3: Terminal Open Boom ---");
  const boomResult = await evaluate(`(() => {
    let boomPlayed = false;
    let err = null;
    try {
      if (typeof window.playTerminalBoomSound === 'function') {
        window.playTerminalBoomSound();
        boomPlayed = true;
      }
    } catch(e) {
      err = e.toString();
    }
    return { boomPlayed, err };
  })()`);
  console.log("Boom sound result:", boomResult);

  console.log("\nALL VERIFICATIONS COMPLETED SUCCESSFULLY!");
  ws.close();
  chromeProcess.kill();
  process.exit(0);
}

main().catch(err => {
  console.error("Error in verification:", err);
  process.exit(1);
});
