// Performance Optimization Utilities
// Utilities for optimizing Fleet Tracker performance

import React, { useState, useEffect, useMemo, useCallback, useRef } from 'react';

// Debounce hook for API calls
export function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}

// Throttle hook for frequent updates
export function useThrottle<T>(value: T, interval: number): T {
  const [throttledValue, setThrottledValue] = useState(value);
  const lastUpdated = useRef(Date.now());

  useEffect(() => {
    const now = Date.now();
    if (now - lastUpdated.current >= interval) {
      setThrottledValue(value);
      lastUpdated.current = now;
    } else {
      const timer = setTimeout(() => {
        setThrottledValue(value);
        lastUpdated.current = Date.now();
      }, interval - (now - lastUpdated.current));

      return () => clearTimeout(timer);
    }
  }, [value, interval]);

  return throttledValue;
}

// Virtual scrolling for large lists
export function useVirtualScroll<T>(
  items: T[],
  itemHeight: number,
  containerHeight: number
) {
  const [scrollTop, setScrollTop] = useState(0);

  const visibleItems = useMemo(() => {
    const startIndex = Math.floor(scrollTop / itemHeight);
    const endIndex = Math.min(
      startIndex + Math.ceil(containerHeight / itemHeight) + 1,
      items.length
    );

    return {
      startIndex,
      endIndex,
      items: items.slice(startIndex, endIndex),
      totalHeight: items.length * itemHeight,
      offsetY: startIndex * itemHeight,
    };
  }, [items, itemHeight, containerHeight, scrollTop]);

  const handleScroll = useCallback((e: React.UIEvent<HTMLDivElement>) => {
    setScrollTop(e.currentTarget.scrollTop);
  }, []);

  return {
    ...visibleItems,
    handleScroll,
  };
}

// Memoized component wrapper
export function withMemo<T extends object>(
  Component: React.ComponentType<T>,
  propsAreEqual?: (prevProps: T, nextProps: T) => boolean
) {
  return React.memo(Component, propsAreEqual);
}

// Cache hook for API responses
export function useCache<T>(key: string, fetchFn: () => Promise<T>, ttl = 300000) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const cache = useRef(new Map<string, { data: T; timestamp: number }>());

  const fetchData = useCallback(async () => {
    const cached = cache.current.get(key);
    const now = Date.now();

    if (cached && now - cached.timestamp < ttl) {
      setData(cached.data);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const result = await fetchFn();
      
      cache.current.set(key, { data: result, timestamp: now });
      setData(result);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  }, [key, fetchFn, ttl]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { data, loading, error, refetch: fetchData };
}

// Performance monitoring hook
export function usePerformanceMonitoring(name: string) {
  const startTime = useRef(performance.now());

  useEffect(() => {
    return () => {
      const endTime = performance.now();
      const duration = endTime - startTime.current;
      
      // Log performance metrics
      console.log(`${name} took ${duration.toFixed(2)}ms`);
      
      // Send to analytics if needed
      if (duration > 1000) {
        console.warn(`${name} took longer than expected: ${duration.toFixed(2)}ms`);
      }
    };
  }, [name]);
}

// Export performance utilities
export const PerformanceUtils = {
  // Measure component render time
  measureRenderTime: (componentName: string) => {
    return function<T extends object>(Component: React.ComponentType<T>) {
      return function MeasuredComponent(props: T) {
        usePerformanceMonitoring(`${componentName} render`);
        return React.createElement(Component, props);
      };
    };
  },

  // Optimize heavy calculations
  optimizeCalculation: <T, R>(
    calculation: (data: T) => R,
    dependencies: React.DependencyList
  ) => {
    return useMemo(() => calculation, dependencies);
  },
};
