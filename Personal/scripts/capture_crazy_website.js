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

  // 1. Hero stage
  console.log("1. Capturing Hero at scrollY = 0...");
  await capture('crazy_1_hero.png');

  // 2. Photo revealed state
  console.log("2. Scrolling to 800px (photo reveal)...");
  await evaluate(`window.scrollTo(0, 800); window.dispatchEvent(new Event('scroll'));`);
  await new Promise(r => setTimeout(r, 800));
  await capture('crazy_2_photo_revealed.png');

  // 3. Intro Command Center with Anton Watermark & Power Spec Matrix
  console.log("3. Scrolling to Intro Command Center...");
  await evaluate(`document.getElementById('intro').scrollIntoView();`);
  await new Promise(r => setTimeout(r, 800));
  await capture('crazy_3_intro_command_center.png');

  // 4. Projects Bento Grid with Anton [SELECTED WORKS] Watermark & 3D Cards
  console.log("4. Scrolling to Projects Bento Grid...");
  await evaluate(`document.getElementById('projects').scrollIntoView();`);
  await new Promise(r => setTimeout(r, 800));
  await capture('crazy_4_projects_bento.png');

  // 5. About Section with Anton [ARCHITECT] Watermark
  console.log("5. Scrolling to About Section...");
  await evaluate(`document.getElementById('about').scrollIntoView();`);
  await new Promise(r => setTimeout(r, 800));
  await capture('crazy_5_about_architect.png');

  // 6. Google Cloud Badges Trophy Vault with Anton [CREDENTIALS] Watermark
  console.log("6. Scrolling to Google Cloud Badges...");
  await evaluate(`document.getElementById('achievements').scrollIntoView();`);
  await new Promise(r => setTimeout(r, 800));
  await capture('crazy_6_badges_vault.png');

  // 7. AWS Cloud Pipeline Showcase with Anton [AWS CLOUD] Watermark
  console.log("7. Scrolling to AWS Showcase...");
  await evaluate(`document.getElementById('aws-showcase').scrollIntoView();`);
  await new Promise(r => setTimeout(r, 800));
  await capture('crazy_7_aws_showcase.png');

  // 8. Contact & Transmission with Anton [TRANSMISSION] Watermark
  console.log("8. Scrolling to Contact Section...");
  await evaluate(`document.getElementById('contact').scrollIntoView();`);
  await new Promise(r => setTimeout(r, 800));
  await capture('crazy_8_contact_transmission.png');

  ws.close();
  chromeProcess.kill();
  console.log("All crazy website screenshots captured successfully!");
}

main().catch(err => {
  console.error("Test error:", err);
  process.exit(1);
});
