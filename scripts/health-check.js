#!/usr/bin/env node

/**
 * AI Teaching Assistant - 服务健康检查脚本
 *
 * 功能：
 *   - 定期 HTTP ping 前端（3000）和后端（8000）服务
 *   - 累计失败次数，超过阈值时发出告警
 *   - 可选 --restart 标志：失败时自动尝试重启对应服务
 *   - 彩色控制台输出，与 dev-start.js 风格一致
 *
 * 用法：
 *   node scripts/health-check.js              # 仅监控
 *   node scripts/health-check.js --restart    # 监控 + 自动重启
 *   node scripts/health-check.js --interval 15 --threshold 3
 */

'use strict';

const http = require('http');
const { spawn } = require('child_process');
const path = require('path');

// ─── CLI 参数解析 ─────────────────────────────────────────────────────────────

const argv = process.argv.slice(2);
const autoRestart  = argv.includes('--restart');
const intervalSec  = Number(argv[argv.indexOf('--interval')  + 1] || 10);
const threshold    = Number(argv[argv.indexOf('--threshold') + 1] || 3);

// ─── 服务配置 ─────────────────────────────────────────────────────────────────

const SERVICES = {
  frontend: {
    name: '前端 (React)',
    url: 'http://localhost:3000',
    restartCmd: 'npm',
    restartArgs: ['start'],
    restartCwd: path.resolve(__dirname, '../frontend'),
  },
  backend: {
    name: '后端 (FastAPI)',
    url: 'http://localhost:8000/health',
    restartCmd: 'python',
    restartArgs: ['-m', 'uvicorn', 'app.main:app', '--reload', '--port', '8000'],
    restartCwd: path.resolve(__dirname, '../backend'),
  },
};

// ─── 彩色输出 ─────────────────────────────────────────────────────────────────

const C = {
  reset:   '\x1b[0m',
  red:     '\x1b[31m',
  green:   '\x1b[32m',
  yellow:  '\x1b[33m',
  blue:    '\x1b[34m',
  magenta: '\x1b[35m',
  cyan:    '\x1b[36m',
  gray:    '\x1b[90m',
};

const log = {
  info:    (msg) => console.log(`${C.blue}[Health]${C.reset} ${msg}`),
  ok:      (msg) => console.log(`${C.green}[Health]${C.reset} ✓ ${msg}`),
  warn:    (msg) => console.log(`${C.yellow}[Health]${C.reset} ⚠ ${msg}`),
  error:   (msg) => console.log(`${C.red}[Health]${C.reset} ✗ ${msg}`),
  time:    ()    => `${C.gray}${new Date().toLocaleTimeString('zh-CN')}${C.reset}`,
};

// ─── 状态追踪 ─────────────────────────────────────────────────────────────────

const state = {};
for (const key of Object.keys(SERVICES)) {
  state[key] = { failCount: 0, restarting: false, proc: null };
}

// ─── 单次健康检查 ─────────────────────────────────────────────────────────────

function pingService(key) {
  const svc = SERVICES[key];
  return new Promise((resolve) => {
    const req = http.get(svc.url, { timeout: 5000 }, (res) => {
      resolve({ ok: res.statusCode < 500, statusCode: res.statusCode });
      res.resume(); // 消费响应体，防止内存泄漏
    });
    req.on('error',   () => resolve({ ok: false, statusCode: null }));
    req.on('timeout', () => { req.destroy(); resolve({ ok: false, statusCode: null }); });
  });
}

// ─── 自动重启 ─────────────────────────────────────────────────────────────────

function restartService(key) {
  const svc = SERVICES[key];
  const s   = state[key];
  if (s.restarting) return;
  s.restarting = true;

  // 先终止旧进程
  if (s.proc && !s.proc.killed) {
    try { s.proc.kill('SIGTERM'); } catch (_) {}
  }

  log.warn(`正在重启 ${svc.name}...`);
  const child = spawn(svc.restartCmd, svc.restartArgs, {
    cwd: svc.restartCwd,
    stdio: 'ignore',
    shell: true,
    detached: false,
  });

  child.on('spawn', () => {
    log.info(`${svc.name} 重启进程已启动 (PID: ${child.pid})`);
  });

  child.on('error', (err) => {
    log.error(`${svc.name} 重启失败: ${err.message}`);
    s.restarting = false;
  });

  child.on('close', (code) => {
    if (code !== 0) log.warn(`${svc.name} 进程退出，退出码: ${code}`);
    s.restarting = false;
  });

  s.proc      = child;
  s.failCount = 0; // 重置计数
}


// ─── 主检查循环 ───────────────────────────────────────────────────────────────

async function checkAll() {
  const results = await Promise.all(
    Object.keys(SERVICES).map(async (key) => {
      const svc = SERVICES[key];
      const s   = state[key];
      const { ok, statusCode } = await pingService(key);
      const ts  = log.time();

      if (ok) {
        if (s.failCount > 0) {
          log.ok(`${ts} ${svc.name} 已恢复（HTTP ${statusCode}）`);
        } else {
          log.ok(`${ts} ${svc.name} 正常（HTTP ${statusCode}）`);
        }
        s.failCount  = 0;
        s.restarting = false;
      } else {
        s.failCount += 1;
        const badge = statusCode ? `HTTP ${statusCode}` : '无法连接';
        log.error(`${ts} ${svc.name} 不可达（${badge}）— 失败 ${s.failCount}/${threshold} 次`);

        if (s.failCount >= threshold) {
          if (autoRestart) {
            restartService(key);
          } else {
            log.warn(`${svc.name} 连续失败 ${s.failCount} 次。添加 --restart 以启用自动重启。`);
          }
        }
      }
      return { key, ok };
    })
  );
  return results;
}

// ─── 启动 ─────────────────────────────────────────────────────────────────────

function printBanner() {
  console.log(`${C.cyan}
╔══════════════════════════════════════════════════════════════╗
║            AI Teaching Assistant - 健康检查                  ║
╚══════════════════════════════════════════════════════════════╝${C.reset}`);
  log.info(`间隔: ${intervalSec}s  |  阈值: ${threshold} 次  |  自动重启: ${autoRestart ? '✓' : '✗'}`);
  for (const [key, svc] of Object.entries(SERVICES)) {
    log.info(`  [${key}] ${svc.name} → ${svc.url}`);
  }
  console.log();
}

async function main() {
  printBanner();
  await checkAll();
  const timer = setInterval(checkAll, intervalSec * 1000);

  function shutdown() {
    clearInterval(timer);
    log.info('健康检查已停止。');
    for (const [key, s] of Object.entries(state)) {
      if (s.proc && !s.proc.killed) {
        try { s.proc.kill('SIGTERM'); } catch (_) {}
      }
    }
    process.exit(0);
  }

  process.on('SIGINT',  shutdown);
  process.on('SIGTERM', shutdown);
}

main().catch((err) => {
  log.error(`脚本异常: ${err.message}`);
  process.exit(1);
});
