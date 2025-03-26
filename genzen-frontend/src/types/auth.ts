export interface CreateGenZenUser {
    username: string;
    password: string;
    email: string;
    role: string;
}

export interface Token {
    access_token: string;
    token_type: string;
}

export interface ValidationError {
    loc: (string | number)[];
    msg: string;
    type: string;
}

export interface HTTPValidationError {
    detail: ValidationError[];
} 