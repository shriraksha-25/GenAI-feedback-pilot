/**
 * Validation utilities for FeedbackForge AI forms
 */

export const SUPPORTED_FILE_EXTENSIONS = ['.csv', '.txt', '.pdf', '.doc', '.docx'];
export const MAX_FILE_SIZE_BYTES = 15 * 1024 * 1024; // 15MB

/**
 * Validate email address
 * @param {string} email 
 * @returns {string|null} Error message or null
 */
export function validateEmail(email) {
  if (!email || !email.trim()) {
    return 'Email address is required.';
  }
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email.trim())) {
    return 'Please enter a valid email address.';
  }
  return null;
}

/**
 * Validate password requirements
 * @param {string} password 
 * @returns {string|null}
 */
export function validatePassword(password) {
  if (!password) {
    return 'Password is required.';
  }
  if (password.length < 8) {
    return 'Password must be at least 8 characters long.';
  }
  return null;
}

/**
 * Validate password confirmation match
 * @param {string} password 
 * @param {string} confirmPassword 
 * @returns {string|null}
 */
export function validateConfirmPassword(password, confirmPassword) {
  if (!confirmPassword) {
    return 'Please confirm your password.';
  }
  if (password !== confirmPassword) {
    return 'Passwords do not match.';
  }
  return null;
}

/**
 * Validate required field
 * @param {string} val 
 * @param {string} fieldName 
 * @returns {string|null}
 */
export function validateRequired(val, fieldName = 'This field') {
  if (!val || (typeof val === 'string' && !val.trim())) {
    return `${fieldName} is required.`;
  }
  return null;
}

/**
 * Validate uploaded file format and size
 * @param {File} file 
 * @returns {string|null}
 */
export function validateUploadedFile(file) {
  if (!file) return null;
  const fileName = file.name.toLowerCase();
  const isValidExt = SUPPORTED_FILE_EXTENSIONS.some(ext => fileName.endsWith(ext));
  
  if (!isValidExt) {
    return `Unsupported file format. Allowed: ${SUPPORTED_FILE_EXTENSIONS.join(', ')}`;
  }
  
  if (file.size > MAX_FILE_SIZE_BYTES) {
    return 'File size exceeds 15MB limit.';
  }
  
  return null;
}
