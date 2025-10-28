#!/usr/bin/env node

const fetch = require('node-fetch');

async function testIntegration() {
  console.log('🧪 Testing TrafficLaw Chatbot Integration...\n');

  try {
    // Test 1: Next.js API Health Check
    console.log('1. Testing Next.js API health...');
    const healthResponse = await fetch('http://localhost:3001/api/health');
    const healthData = await healthResponse.json();
    console.log('✅ Next.js API:', healthData.status);

    // Test 2: Python Backend Health Check (if running)
    console.log('\n2. Testing Python backend...');
    try {
      const pythonResponse = await fetch('http://localhost:8000/docs');
      if (pythonResponse.ok) {
        console.log('✅ Python backend: Running');
      } else {
        console.log('⚠️  Python backend: Not responding');
      }
    } catch (error) {
      console.log('⚠️  Python backend: Not running (start with: npm run dev:python)');
    }

    // Test 3: Frontend (if running)
    console.log('\n3. Testing Next.js frontend...');
    try {
      const frontendResponse = await fetch('http://localhost:3000');
      if (frontendResponse.ok) {
        console.log('✅ Next.js frontend: Running');
      } else {
        console.log('⚠️  Next.js frontend: Not responding');
      }
    } catch (error) {
      console.log('⚠️  Next.js frontend: Not running (start with: npm run dev:web)');
    }

    console.log('\n🎉 Integration test complete!');
    console.log('\nTo start all services: npm run dev');

  } catch (error) {
    console.error('❌ Test failed:', error.message);
  }
}

testIntegration();
