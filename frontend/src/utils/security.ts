// Security Utilities
// Security hardening utilities for Fleet Tracker

// Input sanitization
export class SecurityUtils {
  // Sanitize HTML input to prevent XSS
  static sanitizeHtml(input: string): string {
    const div = document.createElement('div');
    div.textContent = input;
    return div.innerHTML;
  }

  // Validate and sanitize SQL-like inputs
  static sanitizeSqlInput(input: string): string {
    // Remove common SQL injection patterns
    return input
      .replace(/['"`;]/g, '')
      .replace(/\b(DROP|DELETE|INSERT|UPDATE|SELECT|UNION|ALTER|CREATE)\b/gi, '')
      .trim();
  }

  // Validate email format
  static isValidEmail(email: string): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  // Validate phone number (Vietnamese format)
  static isValidPhoneNumber(phone: string): boolean {
    const phoneRegex = /^(\+84|84|0)[1-9]\d{8,9}$/;
    return phoneRegex.test(phone.replace(/\s/g, ''));
  }

  // Validate license plate (Vietnamese format)
  static isValidLicensePlate(plate: string): boolean {
    const plateRegex = /^[0-9]{2}[A-Z]-[0-9]{3}\.[0-9]{2}$|^[0-9]{2}[A-Z]-[0-9]{4,5}$/;
    return plateRegex.test(plate);
  }

  // Generate CSRF token
  static generateCSRFToken(): string {
    const array = new Uint8Array(32);
    crypto.getRandomValues(array);
    return Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('');
  }

  // Validate CSRF token
  static validateCSRFToken(token: string, expectedToken: string): boolean {
    return token === expectedToken && token.length === 64;
  }

  // Rate limiting
  static createRateLimiter(maxRequests: number, windowMs: number) {
    const requests = new Map<string, number[]>();

    return (identifier: string): boolean => {
      const now = Date.now();
      const windowStart = now - windowMs;
      
      // Get existing requests for this identifier
      const userRequests = requests.get(identifier) || [];
      
      // Filter out old requests
      const recentRequests = userRequests.filter(time => time > windowStart);
      
      // Check if limit exceeded
      if (recentRequests.length >= maxRequests) {
        return false;
      }
      
      // Add current request
      recentRequests.push(now);
      requests.set(identifier, recentRequests);
      
      return true;
    };
  }

  // Content Security Policy generator
  static generateCSP(): string {
    return [
      "default-src 'self'",
      "script-src 'self' 'unsafe-inline' https://api.mapbox.com",
      "style-src 'self' 'unsafe-inline' https://api.mapbox.com",
      "img-src 'self' data: https://api.mapbox.com",
      "connect-src 'self' ws: wss: https://api.mapbox.com",
      "font-src 'self' https://fonts.gstatic.com",
      "object-src 'none'",
      "base-uri 'self'",
      "form-action 'self'"
    ].join('; ');
  }

  // Encrypt sensitive data for local storage
  static encryptForStorage(data: string, key: string): string {
    // Simple XOR encryption for demonstration
    // In production, use proper encryption library
    let encrypted = '';
    for (let i = 0; i < data.length; i++) {
      encrypted += String.fromCharCode(
        data.charCodeAt(i) ^ key.charCodeAt(i % key.length)
      );
    }
    return btoa(encrypted);
  }

  // Decrypt data from local storage
  static decryptFromStorage(encryptedData: string, key: string): string {
    try {
      const encrypted = atob(encryptedData);
      let decrypted = '';
      for (let i = 0; i < encrypted.length; i++) {
        decrypted += String.fromCharCode(
          encrypted.charCodeAt(i) ^ key.charCodeAt(i % key.length)
        );
      }
      return decrypted;
    } catch {
      return '';
    }
  }

  // Secure token storage
  static setSecureToken(key: string, token: string): void {
    const encryptedToken = this.encryptForStorage(token, key);
    localStorage.setItem(key, encryptedToken);
  }

  static getSecureToken(key: string): string | null {
    const encryptedToken = localStorage.getItem(key);
    if (!encryptedToken) return null;
    
    return this.decryptFromStorage(encryptedToken, key);
  }

  // Input validation rules
  static validationRules = {
    required: (value: any) => {
      if (value === null || value === undefined || value === '') {
        return 'Trường này là bắt buộc';
      }
      return null;
    },

    minLength: (min: number) => (value: string) => {
      if (value && value.length < min) {
        return `Tối thiểu ${min} ký tự`;
      }
      return null;
    },

    maxLength: (max: number) => (value: string) => {
      if (value && value.length > max) {
        return `Tối đa ${max} ký tự`;
      }
      return null;
    },

    email: (value: string) => {
      if (value && !SecurityUtils.isValidEmail(value)) {
        return 'Email không hợp lệ';
      }
      return null;
    },

    phone: (value: string) => {
      if (value && !SecurityUtils.isValidPhoneNumber(value)) {
        return 'Số điện thoại không hợp lệ';
      }
      return null;
    },

    licensePlate: (value: string) => {
      if (value && !SecurityUtils.isValidLicensePlate(value)) {
        return 'Biển số xe không hợp lệ';
      }
      return null;
    },

    numeric: (value: string) => {
      if (value && isNaN(Number(value))) {
        return 'Chỉ được nhập số';
      }
      return null;
    },

    alphanumeric: (value: string) => {
      if (value && !/^[a-zA-Z0-9]+$/.test(value)) {
        return 'Chỉ được nhập chữ và số';
      }
      return null;
    },
  };

  // Form validation
  static validateForm(data: Record<string, any>, rules: Record<string, Function[]>): Record<string, string> {
    const errors: Record<string, string> = {};

    Object.keys(rules).forEach(field => {
      const fieldRules = rules[field];
      const value = data[field];

      for (const rule of fieldRules) {
        const error = rule(value);
        if (error) {
          errors[field] = error;
          break;
        }
      }
    });

    return errors;
  }

  // Permission checking
  static checkPermission(userRole: string, requiredPermission: string): boolean {
    const rolePermissions: Record<string, string[]> = {
      admin: ['read', 'write', 'delete', 'manage_users', 'manage_vehicles', 'view_analytics'],
      manager: ['read', 'write', 'manage_vehicles', 'view_analytics'],
      operator: ['read', 'write'],
      viewer: ['read'],
    };

    return rolePermissions[userRole]?.includes(requiredPermission) || false;
  }

  // Session management
  static createSession(userId: string, userRole: string): string {
    const sessionData = {
      userId,
      userRole,
      createdAt: Date.now(),
      expiresAt: Date.now() + (24 * 60 * 60 * 1000), // 24 hours
    };

    const sessionToken = btoa(JSON.stringify(sessionData));
    sessionStorage.setItem('session', sessionToken);
    
    return sessionToken;
  }

  static validateSession(): { valid: boolean; userId?: string; userRole?: string } {
    try {
      const sessionToken = sessionStorage.getItem('session');
      if (!sessionToken) return { valid: false };

      const sessionData = JSON.parse(atob(sessionToken));
      
      if (Date.now() > sessionData.expiresAt) {
        sessionStorage.removeItem('session');
        return { valid: false };
      }

      return {
        valid: true,
        userId: sessionData.userId,
        userRole: sessionData.userRole,
      };
    } catch {
      return { valid: false };
    }
  }

  static clearSession(): void {
    sessionStorage.removeItem('session');
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_data');
  }

  // Audit logging
  static logSecurityEvent(event: {
    type: 'login' | 'logout' | 'failed_login' | 'permission_denied' | 'data_access' | 'data_modification';
    userId?: string;
    details?: string;
    ipAddress?: string;
    userAgent?: string;
  }): void {
    const logEntry = {
      ...event,
      timestamp: new Date().toISOString(),
      sessionId: SecurityUtils.generateCSRFToken(),
    };

    // In production, send to security logging service
    console.log('Security Event:', logEntry);
    
    // Store locally for development
    const logs = JSON.parse(localStorage.getItem('security_logs') || '[]');
    logs.push(logEntry);
    
    // Keep only last 100 logs
    if (logs.length > 100) {
      logs.splice(0, logs.length - 100);
    }
    
    localStorage.setItem('security_logs', JSON.stringify(logs));
  }

  // Get user's IP address (approximation)
  static async getUserIP(): Promise<string> {
    try {
      // Note: This requires an external service in production
      const response = await fetch('https://api.ipify.org?format=json');
      const data = await response.json();
      return data.ip;
    } catch {
      return 'unknown';
    }
  }

  // Security headers checker
  static checkSecurityHeaders(): {
    hasCSP: boolean;
    hasXSSProtection: boolean;
    hasFrameOptions: boolean;
    hasHSTS: boolean;
  } {
    const csp = document.querySelector('meta[http-equiv="Content-Security-Policy"]');
    const xss = document.querySelector('meta[http-equiv="X-XSS-Protection"]');
    const frame = document.querySelector('meta[http-equiv="X-Frame-Options"]');
    
    return {
      hasCSP: !!csp,
      hasXSSProtection: !!xss,
      hasFrameOptions: !!frame,
      hasHSTS: location.protocol === 'https:',
    };
  }
}

// React hook for secure forms
export function useSecureForm<T extends Record<string, any>>(
  initialData: T,
  validationRules: Record<keyof T, Function[]>
) {
  const [data, setData] = React.useState<T>(initialData);
  const [errors, setErrors] = React.useState<Partial<Record<keyof T, string>>>({});
  const [isSubmitting, setIsSubmitting] = React.useState(false);

  const updateField = React.useCallback((field: keyof T, value: any) => {
    setData(prev => ({ ...prev, [field]: value }));
    
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: undefined }));
    }
  }, [errors]);

  const validate = React.useCallback(() => {
    const validationErrors = SecurityUtils.validateForm(data, validationRules as any);
    setErrors(validationErrors as Partial<Record<keyof T, string>>);
    return Object.keys(validationErrors).length === 0;
  }, [data, validationRules]);

  const reset = React.useCallback(() => {
    setData(initialData);
    setErrors({});
    setIsSubmitting(false);
  }, [initialData]);

  return {
    data,
    errors,
    isSubmitting,
    setIsSubmitting,
    updateField,
    validate,
    reset,
  };
}

// Security monitoring hook
export function useSecurityMonitoring() {
  React.useEffect(() => {
    // Monitor for potential security issues
    const handleSecurityViolation = (event: SecurityPolicyViolationEvent) => {
      SecurityUtils.logSecurityEvent({
        type: 'permission_denied',
        details: `CSP Violation: ${event.violatedDirective} - ${event.blockedURI}`,
      });
    };

    // Monitor for suspicious activity
    const handleSuspiciousActivity = () => {
      SecurityUtils.logSecurityEvent({
        type: 'permission_denied',
        details: 'Potential click-jacking attempt detected',
      });
    };

    document.addEventListener('securitypolicyviolation', handleSecurityViolation);
    
    // Check if running in iframe (potential clickjacking)
    if (window.self !== window.top) {
      handleSuspiciousActivity();
    }

    return () => {
      document.removeEventListener('securitypolicyviolation', handleSecurityViolation);
    };
  }, []);

  return SecurityUtils.checkSecurityHeaders();
}

import React from 'react';
