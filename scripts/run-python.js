#!/usr/bin/env node
const { spawn } = require('child_process');
const { platform } = require('os');
const path = require('path');
const fs = require('fs');

const isWindows = platform() === 'win32';

// Determine which Python to use - prioritize venv
let pythonCmd;
const venvPaths = [
  path.join('venv', 'bin', 'python'),           // Standard venv (macOS/Linux)
  path.join('venv', 'Scripts', 'python.exe'),  // Standard venv (Windows)
  path.join('venv312', 'bin', 'python'),        // venv312 (macOS/Linux)
  path.join('venv312', 'Scripts', 'python.exe'), // venv312 (Windows)
];

// Try venv paths first (check resolved paths from project root)
let venvFound = false;
const projectRoot = path.resolve(__dirname, '..'); // scripts/ is one level down from root
for (const venvPath of venvPaths) {
  const fullPath = path.resolve(projectRoot, venvPath);
  if (fs.existsSync(fullPath)) {
    pythonCmd = fullPath;
    venvFound = true;
    break;
  }
}
if (venvFound) {
  console.log(`[python] Using virtual environment: ${pythonCmd}`);
}

if (!venvFound) {
  // Check for system Python
  if (isWindows) {
    pythonCmd = 'python';
  } else {
    pythonCmd = 'python3';
  }
  console.error(`[python] ERROR: No virtual environment found!`);
  console.error(`[python] Please create one: python3 -m venv venv`);
  console.error(`[python] Then install dependencies: pip install -r requirements.txt`);
  console.error(`[python] Falling back to system Python: ${pythonCmd}`);
  console.error(`[python] This may fail if dependencies aren't installed globally.`);
}

// Set PYTHONPATH to include backend directory so imports work correctly
// When running from backend/ directory, Python needs backend/ in PYTHONPATH for relative imports
const backendPath = path.resolve(projectRoot, 'backend');
const env = { ...process.env, PYTHONPATH: backendPath };
const args = ['-m', 'uvicorn', 'main:app', '--reload', '--host', '127.0.0.1', '--port', '8000'];

const child = spawn(pythonCmd, args, {
  env,
  stdio: 'inherit',
  shell: false,
  cwd: backendPath, // Change working directory to backend/ so uvicorn finds main.py
});

child.on('error', (err) => {
  console.error(`Error: Python not found. Please install Python 3.12+ or activate your virtual environment.`);
  console.error(`Tried: ${pythonCmd}`);
  process.exit(1);
});

child.on('exit', (code) => {
  process.exit(code || 0);
});

