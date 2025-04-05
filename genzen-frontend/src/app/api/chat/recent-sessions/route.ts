import { NextResponse } from 'next/server';
import { NextRequest } from 'next/server';
import { env } from '@/utils/env';

export const dynamic = 'force-dynamic';

export async function GET(request: NextRequest) {
  try {
    // Get the authorization header from the request
    const authHeader = request.headers.get('authorization');
    if (!authHeader) {
      // console.log('No authorization header found');
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    // console.log('Fetching recent sessions from backend...');
    const response = await fetch(`/v1/chat/recent-sessions?limit=2`, {
      headers: {
        'Authorization': authHeader,
      },
    });

    if (!response.ok) {
      // console.error('Backend response not OK:', response.status, response.statusText);
      throw new Error('Failed to fetch sessions');
    }

    const data = await response.json();
    // console.log('Raw response from backend:', JSON.stringify(data, null, 2));
    
    // Ensure we're returning an array of sessions
    const sessions = Array.isArray(data) ? data : [];
    // console.log('Processed sessions:', JSON.stringify(sessions, null, 2));
    
    return NextResponse.json(sessions);
  } catch (error) {
    // console.error('Error fetching recent sessions:', error);
    return NextResponse.json(
      { error: 'Failed to fetch recent sessions' },
      { status: 500 }
    );
  }
} 