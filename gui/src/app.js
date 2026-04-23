const repoOutput = document.getElementById('repoOutput');
const logOutput = document.getElementById('logOutput');

function setStatus(message) {
  repoOutput.textContent = `${new Date().toISOString()} :: ${message}\n` + repoOutput.textContent;
}

async function runCommand(args) {
  if (window.Neutralino) {
    const cmd = ['assist-er', '--pro', ...args].join(' ');
    const result = await Neutralino.os.execCommand(cmd);
    return result.stdOut || result.stdErr;
  }
  return `Simulated: assist-er --pro ${args.join(' ')}`;
}

document.getElementById('saveToken').addEventListener('click', async () => {
  const token = document.getElementById('token').value.trim();
  if (!token) {
    setStatus('Token required.');
    return;
  }
  const out = await runCommand(['auth', 'login-pat', token]);
  setStatus(out);
});

document.querySelectorAll('button[data-action]').forEach((btn) => {
  btn.addEventListener('click', async () => {
    const action = btn.dataset.action;
    const map = {
      scan: ['work'],
      cycle: ['work'],
      fix: ['work'],
      merge: ['work'],
      close: ['work'],
      audit: ['work'],
      repair: ['work'],
      deps: ['work'],
      clean: ['work']
    };
    const out = await runCommand(map[action]);
    setStatus(out);
  });
});

document.getElementById('refreshLogs').addEventListener('click', async () => {
  if (window.Neutralino) {
    try {
      const content = await Neutralino.filesystem.readFile('.assist-er/pro/logs/live.ndjson');
      logOutput.textContent = content;
      return;
    } catch (e) {
      logOutput.textContent = String(e);
      return;
    }
  }
  logOutput.textContent = 'Run inside Neutralino desktop app to stream real logs.';
});
