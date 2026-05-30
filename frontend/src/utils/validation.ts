// Validation helpers — used by Zod schemas and forms

export function isValidEmail(email: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

export function isStrongPassword(password: string): boolean {
  // At least 8 chars, 1 uppercase, 1 lowercase, 1 digit
  return /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$/.test(password);
}

export function isValidStudentCode(code: string): boolean {
  return /^[A-Z0-9\-]{3,20}$/.test(code);
}
