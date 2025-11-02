import { NextRequest, NextResponse } from 'next/server';
import { getCorsHeaders } from '../../../../lib/cors';

const PYTHON_API_URL = process.env.PYTHON_API_URL || 'http://localhost:8000';

export async function OPTIONS(
  request: NextRequest,
  { params }: { params: { sessionId: string } }
) {
  return new NextResponse(null, {
    status: 200,
    headers: getCorsHeaders(request),
  });
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: { sessionId: string } }
) {
  try {
    const { sessionId } = params;
    
    // Forward the request to Python backend
    const response = await fetch(`${PYTHON_API_URL}/sessions/${sessionId}`, {
      method: 'DELETE',
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
      console.error('API Error: Session deletion failed');
    } else {
      console.error('API Error:', error);
    }
    return NextResponse.json(
      { error: 'Failed to clear session' },
      {
        status: 500,
        headers: getCorsHeaders(request),
      }
    );
  }
}
