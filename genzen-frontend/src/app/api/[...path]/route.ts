import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL;

if (!BACKEND_URL) {
  throw new Error('NEXT_PUBLIC_API_URL environment variable is not set');
}

// Helper function to forward headers while removing host and connection
function filterAndForwardHeaders(headers: Headers): HeadersInit {
  const filteredHeaders = new Headers(headers);
  // Remove headers that should not be forwarded
  ['host', 'connection'].forEach(header => filteredHeaders.delete(header));
  return filteredHeaders;
}

// Handle all HTTP methods
export async function GET(request: NextRequest, { params }: { params: { path: string[] } }) {
  return handleRequest(request, params.path, 'GET');
}

export async function POST(request: NextRequest, { params }: { params: { path: string[] } }) {
  return handleRequest(request, params.path, 'POST');
}

export async function PUT(request: NextRequest, { params }: { params: { path: string[] } }) {
  return handleRequest(request, params.path, 'PUT');
}

export async function DELETE(request: NextRequest, { params }: { params: { path: string[] } }) {
  return handleRequest(request, params.path, 'DELETE');
}

export async function PATCH(request: NextRequest, { params }: { params: { path: string[] } }) {
  return handleRequest(request, params.path, 'PATCH');
}

async function handleRequest(
  request: NextRequest,
  pathSegments: string[],
  method: string
): Promise<NextResponse> {
  try {
    // Construct the target URL
    const targetUrl = new URL(
      `${BACKEND_URL}/${pathSegments.join('/')}${request.nextUrl.search}`
    );

    // Forward the request to the backend
    const response = await fetch(targetUrl, {
      method: method,
      headers: filterAndForwardHeaders(request.headers),
      body: ['GET', 'HEAD'].includes(method) ? undefined : await request.blob(),
      redirect: 'follow',
    });

    // Get the response body as an ArrayBuffer
    const responseBody = await response.arrayBuffer();

    // Create the response with the same status and headers
    const headers = new Headers(response.headers);
    
    // Return the proxied response
    return new NextResponse(responseBody, {
      status: response.status,
      statusText: response.statusText,
      headers: headers,
    });

  } catch (error) {
    console.error('API proxy error:', error);
    
    return NextResponse.json(
      { 
        error: 'Internal Server Error',
        message: error instanceof Error ? error.message : 'An unexpected error occurred'
      },
      { status: 500 }
    );
  }
} 