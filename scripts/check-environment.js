#!/usr/bin/env node

/**
 * 环境检查脚本 - AI Teaching Assistant
 * 检查开发环境是否满足项目要求
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// 颜色输出工具
const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m',
  white: '\x1b[37m'
};

const log = {
  info: (msg) => console.log(`${colors.blue}ℹ${colors.reset} ${msg}`),
  success: (msg) => console.log(`${colors.green}✓${colors.reset} ${msg}`),
  warning: (msg) => console.log(`${colors.yellow}⚠${colors.reset} ${msg}`),
  error: (msg) => console.log(`${colors.red}✗${colors.reset} ${msg}`),
  title: (msg) => console.log(`\n${colors.cyan}${msg}${colors.reset}\n${'='.repeat(50)}`)
};

// 检查结果统计
let checkResults = {
  passed: 0,
  failed: 0,
  warnings: 0
};

/**
 * 执行命令并返回结果
 */
function runCommand(command, silent = true) {
  try {
    const result = execSync(command, { 
      encoding: 'utf8',
      stdio: silent ? 'pipe' : 'inherit'
    }).trim();
    return { success: true, output: result };
  } catch (error) {
    return { success: false, error: error.message };
  }
}

/**
 * 检查文件是否存在
 */
function checkFileExists(filePath, description) {
  const fullPath = path.resolve(filePath);
  if (fs.existsSync(fullPath)) {
    log.success(`${description}: ${filePath}`);
    checkResults.passed++;
    return true;
  } else {
    log.error(`${description}不存在: ${filePath}`);
    checkResults.failed++;
    return false;
  }
}

/**
 * 检查版本要求
 */
function checkVersion(current, required, name) {
  const currentParts = current.split('.').map(Number);
  const requiredParts = required.split('.').map(Number);
  
  for (let i = 0; i < Math.max(currentParts.length, requiredParts.length); i++) {
    const currentPart = currentParts[i] || 0;
    const requiredPart = requiredParts[i] || 0;
    
    if (currentPart > requiredPart) return true;
    if (currentPart < requiredPart) return false;
  }
  return true;
}

/**
 * 检查 Node.js 环境
 */
function checkNodeEnvironment() {
  log.title('检查 Node.js 环境');
  
  // 检查 Node.js 版本
  const nodeResult = runCommand('node --version');
  if (nodeResult.success) {
    const nodeVersion = nodeResult.output.replace('v', '');
    const requiredNodeVersion = '18.0.0';
    
    if (checkVersion(nodeVersion, requiredNodeVersion, 'Node.js')) {
      log.success(`Node.js 版本: ${nodeVersion} (>= ${requiredNodeVersion})`);
      checkResults.passed++;
    } else {
      log.error(`Node.js 版本过低: ${nodeVersion} (需要 >= ${requiredNodeVersion})`);
      checkResults.failed++;
    }
  } else {
    log.error('Node.js 未安装或不在 PATH 中');
    checkResults.failed++;
  }
  
  // 检查 npm 版本
  const npmResult = runCommand('npm --version');
  if (npmResult.success) {
    log.success(`npm 版本: ${npmResult.output}`);
    checkResults.passed++;
  } else {
    log.error('npm 未安装或不在 PATH 中');
    checkResults.failed++;
  }
}

/**
 * 检查 Python 环境
 */
function checkPythonEnvironment() {
  log.title('检查 Python 环境');
  
  // 检查 Python 版本
  const pythonResult = runCommand('python --version');
  if (pythonResult.success) {
    const versionMatch = pythonResult.output.match(/Python (\d+\.\d+\.\d+)/);
    if (versionMatch) {
      const pythonVersion = versionMatch[1];
      const requiredPythonVersion = '3.10.0';
      
      if (checkVersion(pythonVersion, requiredPythonVersion, 'Python')) {
        log.success(`Python 版本: ${pythonVersion} (>= ${requiredPythonVersion})`);
        checkResults.passed++;
      } else {
        log.error(`Python 版本过低: ${pythonVersion} (需要 >= ${requiredPythonVersion})`);
        checkResults.failed++;
      }
    }
  } else {
    log.error('Python 未安装或不在 PATH 中');
    checkResults.failed++;
  }
  
  // 检查 pip 版本
  const pipResult = runCommand('pip --version');
  if (pipResult.success) {
    log.success(`pip 已安装: ${pipResult.output.split(' ')[1]}`);
    checkResults.passed++;
  } else {
    log.error('pip 未安装或不在 PATH 中');
    checkResults.failed++;
  }
}

/**
 * 检查项目文件结构
 */
function checkProjectStructure() {
  log.title('检查项目文件结构');
  
  const requiredFiles = [
    { path: 'frontend/package.json', desc: '前端 package.json' },
    { path: 'backend/requirements.txt', desc: '后端依赖文件' },
    { path: 'frontend/src/App.vue', desc: '前端主应用文件' },
    { path: 'backend/app/main.py', desc: '后端主应用文件' }
  ];
  
  requiredFiles.forEach(file => {
    checkFileExists(file.path, file.desc);
  });
}

/**
 * 检查依赖安装状态
 */
function checkDependencies() {
  log.title('检查依赖安装状态');
  
  // 检查前端依赖
  if (fs.existsSync('frontend/node_modules')) {
    log.success('前端依赖已安装 (node_modules 存在)');
    checkResults.passed++;
  } else {
    log.warning('前端依赖未安装，请运行: cd frontend && npm install');
    checkResults.warnings++;
  }
  
  // 检查后端虚拟环境
  const venvPaths = ['backend/venv', 'backend/.venv'];
  const hasVenv = venvPaths.some(path => fs.existsSync(path));
  
  if (hasVenv) {
    log.success('后端虚拟环境已创建');
    checkResults.passed++;
  } else {
    log.warning('后端虚拟环境未创建，请运行: cd backend && python -m venv venv');
    checkResults.warnings++;
  }
}

/**
 * 主函数
 */
function main() {
  console.log(`${colors.magenta}
╔══════════════════════════════════════════════════════════════╗
║                AI Teaching Assistant                         ║
║                   环境检查工具                                ║
╚══════════════════════════════════════════════════════════════╝
${colors.reset}`);
  
  checkNodeEnvironment();
  checkPythonEnvironment();
  checkProjectStructure();
  checkDependencies();
  
  // 输出检查结果摘要
  log.title('检查结果摘要');
  console.log(`${colors.green}✓ 通过: ${checkResults.passed}${colors.reset}`);
  console.log(`${colors.yellow}⚠ 警告: ${checkResults.warnings}${colors.reset}`);
  console.log(`${colors.red}✗ 失败: ${checkResults.failed}${colors.reset}`);
  
  if (checkResults.failed > 0) {
    console.log(`\n${colors.red}环境检查失败，请解决上述问题后重试。${colors.reset}`);
    process.exit(1);
  } else if (checkResults.warnings > 0) {
    console.log(`\n${colors.yellow}环境检查通过，但有警告项需要注意。${colors.reset}`);
  } else {
    console.log(`\n${colors.green}🎉 环境检查全部通过！可以开始开发了。${colors.reset}`);
  }
}

// 运行检查
if (require.main === module) {
  main();
}

module.exports = { checkNodeEnvironment, checkPythonEnvironment, checkProjectStructure, checkDependencies };
