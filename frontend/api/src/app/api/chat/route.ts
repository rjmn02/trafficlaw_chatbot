import { NextRequest, NextResponse } from 'next/server';
import { getCorsHeaders } from '../../../lib/cors';

const PYTHON_API_URL = process.env.PYTHON_API_URL || 'http://localhost:8000';

export async function OPTIONS(request: NextRequest) {
  return new NextResponse(null, {
    status: 200,
    headers: getCorsHeaders(request),
  });
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    // Forward the request to Python backend
    const response = await fetch(`${PYTHON_API_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      throw new Error(`Python API error: ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json(data, {
      headers: getCorsHeaders(request),
    });
  } catch (error) {
    // Log full error in development, sanitized in production
    if (process.env.NODE_ENV === 'production') {
      console.error('API Error: Chat request failed');
    } else {
      console.error('API Error:', error);
    }
    return NextResponse.json(
      { error: 'Failed to process chat request' },
      { 
        status: 500,
        headers: getCorsHeaders(request),
      }
    );
  }
}
