// Exporte la vidéo : node tools/render.mjs [sortie.mp4]
// Nécessite playwright, ffmpeg, python3 + numpy, et les voix dans voices/.
import { chromium } from 'playwright';
import { execFileSync } from 'node:child_process';
import fs from 'node:fs'; import path from 'node:path'; import url from 'node:url';

const ROOT = path.resolve(path.dirname(url.fileURLToPath(import.meta.url)), '..');
const OUT = path.resolve(process.argv[2] || path.join(ROOT, 'pourquoi-tu-perds.mp4'));
const FPS = 30, LEAD = 0.45, TAIL = 0.75, MIN = 2.6, NSCENES = 17, LAST = 5.2;
const tmp = fs.mkdtempSync('/tmp/render-');

const dur = f => parseFloat(execFileSync('ffprobe', ['-v','error','-show_entries','format=duration','-of','csv=p=0', f]).toString());
const plan = []; let t = 0;
for (let i = 0; i < NSCENES; i++) {
  const f = path.join(ROOT, 'voices', `scene${String(i+1).padStart(2,'0')}.mp3`);
  const v = fs.existsSync(f) ? dur(f) : 0;
  const d = i === NSCENES-1 ? LAST : Math.max(MIN, LEAD + v + TAIL);
  plan.push({ i, start: t, dur: d, voice: v ? f : null, vlen: v }); t += d;
}
fs.writeFileSync(path.join(tmp, 'plan.json'), JSON.stringify(plan));
console.log(`durée totale ${t.toFixed(1)} s`);

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
await page.goto(url.pathToFileURL(path.join(ROOT, 'index.html')).href + '?render');
await page.evaluate(() => document.fonts.ready);
let n = 0;
for (const sc of plan) {
  await page.evaluate(i => window.__render.scene(i), sc.i);
  await page.waitForTimeout(60);
  const frames = Math.round(sc.dur * FPS);
  for (let k = 0; k < frames; k++) {
    const ms = k * 1000 / FPS;
    const frac = sc.vlen ? (ms/1000 - LEAD) / sc.vlen : 1;
    await page.evaluate(([ms, frac]) => window.__render.seek(ms, frac), [ms, frac]);
    await page.screenshot({ path: path.join(tmp, `f${String(n++).padStart(5,'0')}.jpg`), type: 'jpeg', quality: 92 });
  }
  process.stdout.write(`scène ${sc.i+1}/${NSCENES}\r`);
}
await browser.close();

execFileSync('python3', [path.join(ROOT, 'tools', 'audio.py'), path.join(tmp, 'plan.json'), path.join(tmp, 'mix.wav')], { stdio: 'inherit' });
execFileSync('ffmpeg', ['-loglevel','error','-y','-framerate', String(FPS), '-i', path.join(tmp, 'f%05d.jpg'), '-i', path.join(tmp, 'mix.wav'),
  '-c:v','libx264','-preset','medium','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-shortest','-movflags','+faststart', OUT], { stdio: 'inherit' });
fs.rmSync(tmp, { recursive: true });
console.log(`\nvidéo : ${OUT}`);
