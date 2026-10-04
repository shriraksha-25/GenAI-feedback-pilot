/**
 * Formatting utilities for FeedbackForge AI
 */

/**
 * Format a date string into readable short or full date
 * @param {string|Date} dateStr 
 * @param {boolean} includeTime 
 * @returns {string}
 */
export function formatDate(dateStr, includeTime = false) {
  if (!dateStr) return '—';
  try {
    const d = new Date(dateStr);
    if (isNaN(d.getTime())) return dateStr;
    
    const options = {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      ...(includeTime ? { hour: '2-digit', minute: '2-digit' } : {})
    };
    return new Intl.DateTimeFormat('en-US', options).format(d);
  } catch {
    return dateStr || '—';
  }
}

/**
 * Format large numbers with commas
 * @param {number|string} val 
 * @returns {string}
 */
export function formatNumber(val) {
  if (val === null || val === undefined || isNaN(Number(val))) return '0';
  return Number(val).toLocaleString('en-US');
}

/**
 * Truncate text cleanly with ellipsis
 * @param {string} text 
 * @param {number} maxLen 
 * @returns {string}
 */
export function truncateText(text, maxLen = 100) {
  if (!text) return '—';
  if (text.length <= maxLen) return text;
  return `${text.slice(0, maxLen).trim()}...`;
}

/**
 * Format byte count to human-readable size
 * @param {number} bytes 
 * @returns {string}
 */
export function formatFileSize(bytes) {
  if (!bytes || bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
}

/**
 * Safe fallback for null, undefined, or empty values
 * @param {any} val 
 * @param {string} fallback 
 * @returns {any}
 */
export function safeVal(val, fallback = '—') {
  if (val === null || val === undefined || val === '') return fallback;
  return val;
}
