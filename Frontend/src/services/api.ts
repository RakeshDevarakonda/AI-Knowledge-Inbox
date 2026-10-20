import type { SavedItem, QueryResponse, IngestPayload } from '../types';

const API_BASE_URL = 'http://127.0.0.1:8000';

/**
 * Extracts a clear, user-friendly error message from backend HTTP responses.
 */
async function parseErrorMessage(res: Response, fallback: string): Promise<string> {
  try {
    const data = await res.json();
    if (typeof data.detail === 'string' && data.detail.trim()) {
      return data.detail;
    }
    if (typeof data.message === 'string' && data.message.trim()) {
      return data.message;
    }
    if (Array.isArray(data.detail)) {
      return data.detail
        .map((item: any) => item.msg || item.message || JSON.stringify(item))
        .join('. ');
    }
    if (data.error && typeof data.error.message === 'string') {
      return data.error.message;
    }
  } catch {
    try {
      const rawText = await res.text();
      if (rawText.trim()) return rawText;
    } catch {}
  }
  return fallback;
}

/**
 * Catches connection drops, CORS denials, and server down states.
 */
function handleNetworkError(err: unknown, defaultMessage: string): Error {
  if (err instanceof TypeError && err.message.toLowerCase().includes('fetch')) {
    return new Error(
      'Cannot connect to backend server. Please verify backend is running at http://127.0.0.1:8000'
    );
  }
  return err instanceof Error ? err : new Error(defaultMessage);
}

export async function fetchItems(): Promise<SavedItem[]> {
  try {
    const res = await fetch(`${API_BASE_URL}/items`);
    if (!res.ok) {
      const msg = await parseErrorMessage(res, 'Failed to fetch items from backend');
      throw new Error(msg);
    }
    const data = await res.json();
    return data.items || [];
  } catch (err) {
    throw handleNetworkError(err, 'Failed to load inbox items');
  }
}

export async function ingestContent(payload: IngestPayload): Promise<any> {
  try {
    const res = await fetch(`${API_BASE_URL}/ingest`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const msg = await parseErrorMessage(res, 'Failed to ingest content');
      throw new Error(msg);
    }
    return await res.json();
  } catch (err) {
    throw handleNetworkError(err, 'Failed to ingest content');
  }
}

export async function askQuestion(
  question: string,
  top_k = 3
): Promise<QueryResponse> {
  try {
    const res = await fetch(`${API_BASE_URL}/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, top_k }),
    });
    if (!res.ok) {
      const msg = await parseErrorMessage(res, 'Failed to query knowledge base');
      throw new Error(msg);
    }
    return await res.json();
  } catch (err) {
    throw handleNetworkError(err, 'Failed to complete RAG query');
  }
}
