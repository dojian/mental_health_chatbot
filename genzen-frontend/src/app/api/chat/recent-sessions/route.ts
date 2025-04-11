// import { NextResponse } from 'next/server';
// import { NextRequest } from 'next/server';
// import { env } from '@/utils/env';

// export const dynamic = 'force-dynamic';

// export async function GET(request: NextRequest) {
//   try {
//     // Get the authorization header from the request
//     const authHeader = request.headers.get('authorization');
//     if (!authHeader) {
//       // console.log('No authorization header found');
//       return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
//     }

//     // console.log('Fetching recent sessions from backend...');
//     const response = await fetch(`/v1/chat/recent-sessions?limit=3`, {
//       headers: {
//         'Content-Type': 'application/json',
//         'Authorization': authHeader,
//       },
//     });

//     if (!response.ok) {
//       // console.error('Backend response not OK:', response.status, response.statusText);
//       throw new Error('Failed to fetch sessions');
//     }

//     const data = await response.json();
//     // console.log('Raw response from backend:', JSON.stringify(data, null, 2));
    
//     // Ensure we're returning an array of sessions
//     const sessions = Array.isArray(data) ? data : [];
//     // console.log('Processed sessions:', JSON.stringify(sessions, null, 2));
    
//     return NextResponse.json(sessions);
//   } catch (error) {
//     // console.error('Error fetching recent sessions:', error);
//     return NextResponse.json(
//       { error: 'Failed to fetch recent sessions' },
//       { status: 500 }
//     );
//   }
// } 

import { NextResponse } from 'next/server';
import { NextRequest } from 'next/server';
import { env } from '@/utils/env';

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL;

if (!BACKEND_URL) {
  throw new Error('NEXT_PUBLIC_API_URL environment variable is not set');
}

export async function GET(request: NextRequest) {
  try {
    // Get the authorization header from the request
    const authHeader = request.headers.get('authorization');
    if (!authHeader) {
      console.error('No authorization header found in request');
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    // Get the limit parameter from the request URL
    const url = new URL(request.url);
    const limit = url.searchParams.get('limit') || '2';
    
    console.log(`Fetching recent sessions with limit: ${limit}`);

    // Implement retry logic to handle temporary backend unavailability
    let retryCount = 0;
    const maxRetries = 3;
    let response = null;
    
    while (retryCount < maxRetries) {
      try {
        // Forward the request to the backend
        response = await fetch(`${BACKEND_URL}/v1/chat/recent-sessions?limit=${limit}`, {
          method: 'GET',
          headers: {
            'Authorization': authHeader,
            'Content-Type': 'application/json',
          },
          // Set a reasonable timeout
          signal: AbortSignal.timeout(5000)
        });
        
        console.log(`Backend response status (attempt ${retryCount + 1}):`, response.status);
        
        // If successful, break out of retry loop
        if (response.ok) break;
        
        // If backend returns an error (not 2xx), log and retry
        console.error(`Backend error (attempt ${retryCount + 1}):`, response.status);
      } catch (fetchError) {
        // Handle network errors or timeouts
        console.error(`Fetch error (attempt ${retryCount + 1}):`, fetchError);
      }
      
      // Increment retry counter
      retryCount++;
      
      // Only wait if we're going to retry
      if (retryCount < maxRetries) {
        // Exponential backoff (300ms, 600ms, 1200ms)
        const backoffTime = 300 * Math.pow(2, retryCount - 1);
        console.log(`Retrying in ${backoffTime}ms...`);
        await new Promise(resolve => setTimeout(resolve, backoffTime));
      }
    }
    
    if (!response || !response.ok) {
      const errorMessage = response ? await response.text().catch(() => 'Unknown error') : 'Failed to connect to backend';
      console.error('All backend request attempts failed:', errorMessage);
      return NextResponse.json(
        { error: 'Failed to fetch recent sessions' },
        { status: response?.status || 500 }
      );
    }

    // Parse the response from the backend
    let data;
    try {
      data = await response.json();
      console.log('Backend success response:', JSON.stringify(data, null, 2));
    } catch (jsonError) {
      console.error('Error parsing backend response:', jsonError);
      return NextResponse.json(
        { error: 'Invalid response from backend' },
        { status: 500 }
      );
    }
    
    // Return the data from the backend
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error in recent sessions API route:', error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Failed to fetch recent sessions' },
      { status: 500 }
    );
  }
}
