export function camelToSnake(s: string): string {
  const step1 = s.replace(/([A-Z])([A-Z][a-z0-9])/g, '$1_$2');
  const step2 = step1.replace(/([a-z0-9])([A-Z])/g, '$1_$2');
  return step2.replace(/-/g, '_').toLowerCase();
}

export function deepKeysToSnake<T>(input: T): any {
  if (input === null || input === undefined) return input;

  const type = typeof input;
  if (type === 'string' || type === 'number' || type === 'boolean' || type === 'bigint' || type === 'symbol' || type === 'function') {
    return input;
  }

  if (input instanceof Date || input instanceof RegExp || input instanceof Map || input instanceof Set) {
    return input;
  }

  if (Array.isArray(input)) {
    return input.map(item => deepKeysToSnake(item));
  }

  if (type === 'object') {
    const out: Record<string, any> = {};
    for (const key of Object.keys(input as Record<string, any>)) {
      const val = (input as Record<string, any>)[key];
      const newKey = camelToSnake(key);
      out[newKey] = deepKeysToSnake(val);
    }
    return out;
  }

  return input;
}

export const deepKeysToCamel = (obj: any): any => {
  if (Array.isArray(obj)) {
    return obj.map((v) => deepKeysToCamel(v));
  }

  if (obj !== null && typeof obj === "object") {
    return Object.entries(obj).reduce((acc, [key, value]) => {
      const camelKey = key.replace(/_([a-z])/g, (g) => g[1].toUpperCase());
      acc[camelKey] = deepKeysToCamel(value);
      return acc;
    }, {} as any);
  }

  return obj;
};