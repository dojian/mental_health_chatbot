import { NextResponse } from 'next/server';
import { cookies } from 'next/headers';
import { env } from '@/utils/env';

export async function POST(request: Request) {
  try {
    const cookieStore = cookies();
    const token = cookieStore.get('token')?.value;

    if (!token) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const body = await request.json();
    const response = await fetch(`/v1/pre-chat-survey`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      throw new Error('Failed to submit pre-chat survey');
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error submitting pre-chat survey:', error);
    return NextResponse.json(
      { error: 'Failed to submit pre-chat survey' },
      { status: 500 }
    );
  }
} 