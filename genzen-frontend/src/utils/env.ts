export const env = {
    // API Configuration
    apiUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001',
    
    // Authentication Configuration
    jwtStorageKey: process.env.NEXT_PUBLIC_JWT_STORAGE_KEY || 'token',
} as const; 