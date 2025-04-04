export const env = {
    // Authentication Configuration
    jwtStorageKey: process.env.NEXT_PUBLIC_JWT_STORAGE_KEY || 'token',
} as const; 