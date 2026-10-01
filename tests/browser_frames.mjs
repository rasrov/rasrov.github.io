// Run a page's async frame checks with a real compositor clock, using CDP.
import fs from 'node:fs/promises';
import path from 'node:path';
import {spawn} from 'node:child_process';
import {once} from 'node:events';
const [url, profile] = process.argv.slice(2);
const child = spawn(process.env.BROWSER_BIN, ['--headless', '--disable-gpu', '--no-first-run', '--disable-extensions', '--disable-background-networking', '--remote-debugging-port=0', `--user-data-dir=${profile}`, 'about:blank'], {windowsHide: true, stdio: 'ignore'});
const exited = once(child, 'exit');
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
let ws, next = 0;
const waiting = new Map();
function call(method, params = {}) {
    const id = ++next;
    return new Promise((resolve, reject) => {
        waiting.set(id, {resolve, reject});
        ws.send(JSON.stringify({id, method, params}));
    });
}
async function evaluate(expression) {
    const result = await call('Runtime.evaluate', {expression, awaitPromise: true, returnByValue: true});
    if (result.exceptionDetails) throw new Error(JSON.stringify(result.exceptionDetails));
    return result.result.value;
}
try {
    let port;
    for (let i = 0; i < 100; i++) {
        try { port = (await fs.readFile(path.join(profile, 'DevToolsActivePort'), 'utf8')).split('\n')[0]; break; }
        catch { await sleep(50); }
    }
    if (!port) throw new Error('Browser did not start');
    const targets = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
    ws = new WebSocket(targets.find(target => target.type === 'page').webSocketDebuggerUrl);
    await new Promise((resolve, reject) => { ws.onopen = resolve; ws.onerror = reject; });
    ws.onmessage = event => {
        const message = JSON.parse(event.data);
        const pending = waiting.get(message.id);
        if (!pending) return;
        waiting.delete(message.id);
        if (message.error) pending.reject(new Error(JSON.stringify(message.error)));
        else pending.resolve(message.result);
    };
    await call('Page.enable');
    await call('Emulation.setDeviceMetricsOverride', {width: 390, height: 900, deviceScaleFactor: 1, mobile: false});
    await call('Page.navigate', {url});
    for (let i = 0; i < 100; i++) {
        if (await evaluate("document.readyState === 'complete' && typeof runFrameChecks === 'function'")) break;
        await sleep(50);
    }
    if (await evaluate('runFrameChecks()') !== true) throw new Error('Frame checks did not pass');
} finally {
    if (ws?.readyState === WebSocket.OPEN) {
        await call('Browser.close').catch(() => {});
        ws.close();
    } else child.kill();
    await exited;
}
