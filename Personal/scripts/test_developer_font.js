const http = require('http');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

const ARTIFACT_DIR = '/Users/mukeshkumar/.gemini/antigravity-ide/brain/69bff23a-d166-43cd-a80d-4f25e805bc41/scratch';

async function main() {
  console.log("Launching headless Chrome on port 9333 to test DEVELOPER fonts...");
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

  await new Promise(r => setTimeout(r, 2500));

  const testFonts = [
    { name: 'sans_serif_900', font: '900 340px sans-serif' },
    { name: 'apple_system_900', font: '900 340px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif' },
    { name: 'inter_900', font: '900 340px "Inter", sans-serif' },
    { name: 'outfit_800', font: '800 340px "Outfit", sans-serif' },
    { name: 'impact_900', font: '900 340px Impact, sans-serif' },
    { name: 'anton_400', font: '400 340px Anton, sans-serif' }
  ];

  for (const item of testFonts) {
    console.log(`Testing font: ${item.name} (${item.font})...`);
    await evaluate(`(() => {
      const bannerCanvas = document.createElement('canvas');
      bannerCanvas.width = 2048;
      bannerCanvas.height = 420;
      const bCtx = bannerCanvas.getContext('2d');
      bCtx.clearRect(0, 0, bannerCanvas.width, bannerCanvas.height);
      bCtx.font = '${item.font}';
      bCtx.textAlign = 'center';
      bCtx.textBaseline = 'middle';
      bCtx.letterSpacing = '-0.02em';
      const grad = bCtx.createLinearGradient(0, 40, 0, 380);
      grad.addColorStop(0.0, 'rgba(160, 160, 170, 0.75)');
      grad.addColorStop(0.5, 'rgba(95, 95, 105, 0.40)');
      grad.addColorStop(1.0, 'rgba(15, 12, 18, 0.02)');
      bCtx.fillStyle = grad;
      bCtx.fillText('[DEVELOPER]', bannerCanvas.width / 2, bannerCanvas.height / 2 + 10);

      // Replace bannerTexture image
      if (window.bannerMesh && window.bannerMesh.material && window.bannerMesh.material.uniforms.uTexture) {
        window.bannerMesh.material.uniforms.uTexture.value.image = bannerCanvas;
        window.bannerMesh.material.uniforms.uTexture.value.needsUpdate = true;
      }
    })()`);

    await new Promise(r => setTimeout(r, 400));

    const res = await send('Page.captureScreenshot', { format: 'png' });
    const buf = Buffer.from(res.result.data, 'base64');
    fs.writeFileSync(path.join(ARTIFACT_DIR, `test_font_${item.name}.png`), buf);
    console.log(`Saved screenshot test_font_${item.name}.png`);
  }

  ws.close();
  chromeProcess.kill();
  process.exit(0);
}

main().catch(e => {
  console.error(e);
  process.exit(1);
});
