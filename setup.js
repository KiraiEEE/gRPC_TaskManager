/**
 * Setup script for the gRPC Task Manager project
 */
import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

// Get directory name
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Colors for console output
const colors = {
  reset: '\x1b[0m',
  bold: '\x1b[1m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  red: '\x1b[31m',
  blue: '\x1b[34m'
};

console.log(`${colors.bold}${colors.blue}=== gRPC Task Manager Setup ===${colors.reset}\n`);

/**
 * Execute a command and handle potential errors
 */
function execCommand(command, errorMessage) {
  try {
    console.log(`${colors.yellow}Running: ${command}${colors.reset}`);
    execSync(command, { stdio: 'inherit' });
    return true;
  } catch (error) {
    console.error(`${colors.red}ERROR: ${errorMessage}${colors.reset}`);
    console.error(`${colors.red}${error.message}${colors.reset}`);
    return false;
  }
}

/**
 * Check if a command is available
 */
function checkCommandAvailable(command) {
  try {
    execSync(`${command} --version`, { stdio: 'ignore' });
    return true;
  } catch (error) {
    return false;
  }
}

// Step 1: Check for required dependencies
console.log(`${colors.bold}Checking dependencies...${colors.reset}`);

// Check for Node.js
console.log('Checking for Node.js...');
const nodeVersion = process.version;
console.log(`Node.js ${nodeVersion} is installed.`);

// Check for npm
console.log('Checking for npm...');
if (!checkCommandAvailable('npm')) {
  console.error(`${colors.red}ERROR: npm is not installed. Please install npm.${colors.reset}`);
  process.exit(1);
}
console.log('npm is installed.');

// Check for protoc
console.log('Checking for Protocol Buffers compiler (protoc)...');
if (!checkCommandAvailable('protoc')) {
  console.log(`${colors.yellow}WARNING: Protocol Buffers compiler (protoc) is not installed.${colors.reset}`);
  console.log('You will need to install protoc to generate proto files.');
  console.log('Download from: https://github.com/protocolbuffers/protobuf/releases');
}
else {
  console.log('protoc is installed.');
}

// Step 2: Create necessary directories
console.log(`\n${colors.bold}Creating necessary directories...${colors.reset}`);

// Create directories
const dirs = ['generated', 'dist'];
for (const dir of dirs) {
  const dirPath = path.join(__dirname, dir);
  if (!fs.existsSync(dirPath)) {
    fs.mkdirSync(dirPath, { recursive: true });
    console.log(`Created ${dir} directory.`);
  } else {
    console.log(`Directory ${dir} already exists.`);
  }
}

// Step 3: Install dependencies
console.log(`\n${colors.bold}Installing dependencies...${colors.reset}`);
execCommand('npm install', 'Failed to install dependencies.');

// Step 4: Building the project
console.log(`\n${colors.bold}Building the project...${colors.reset}`);

// Try to generate proto files if protoc is available
if (checkCommandAvailable('protoc')) {
  console.log('Generating proto files...');
  execCommand('npm run proto:generate', 'Failed to generate proto files.');
} else {
  console.log(`${colors.yellow}Skipping proto file generation. Please install protoc and run 'npm run proto:generate' manually.${colors.reset}`);
}

// Build client-side JavaScript
console.log('Building client-side JavaScript...');
execCommand('npm run build', 'Failed to build client-side JavaScript.');

// Step 5: Success message
console.log(`\n${colors.green}${colors.bold}Setup completed successfully!${colors.reset}`);
console.log(`\nYou can now run the application with: ${colors.bold}npm start${colors.reset}`);
console.log(`Then open your browser and navigate to: ${colors.bold}http://localhost:8080${colors.reset}`);

// Print additional instructions if protoc was not found
if (!checkCommandAvailable('protoc')) {
  console.log(`\n${colors.yellow}IMPORTANT: You need to install Protocol Buffers compiler (protoc) and run 'npm run proto:generate' before starting the application.${colors.reset}`);
}