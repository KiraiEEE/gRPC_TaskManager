// Script to generate JavaScript files from proto definitions
import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';

// Ensure the generated directory exists
const generatedDir = path.resolve('generated');
if (!fs.existsSync(generatedDir)) {
  fs.mkdirSync(generatedDir, { recursive: true });
  console.log('Created generated directory');
}

// Ensure the dist directory exists for webpack output
const distDir = path.resolve('dist');
if (!fs.existsSync(distDir)) {
  fs.mkdirSync(distDir, { recursive: true });
  console.log('Created dist directory');
}

try {
  // Check if protoc is installed
  try {
    execSync('protoc --version', { stdio: 'ignore' });
  } catch (error) {
    console.error('⚠️ Protocol Buffers compiler (protoc) is not installed.');
    console.log('Please install protoc from https://github.com/protocolbuffers/protobuf/releases');
    console.log('This is required to generate JavaScript files from proto definitions');
    process.exit(1);
  }

  console.log('Generating JavaScript files from proto definitions...');
  
  // Path to proto file
  const protoFile = path.resolve('taskmanager.proto');
  
  // Command to generate JavaScript files using protoc
  const cmd = `protoc \
    --js_out=import_style=commonjs:${generatedDir} \
    --grpc-web_out=import_style=commonjs,mode=grpcwebtext:${generatedDir} \
    ${protoFile}`;
    
  execSync(cmd, { stdio: 'inherit' });
  console.log('✅ Proto files generated successfully!');
  
} catch (error) {
  console.error('❌ Error generating proto files:', error.message);
  process.exit(1);
}