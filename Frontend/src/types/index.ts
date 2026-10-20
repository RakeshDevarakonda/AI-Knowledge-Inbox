export interface SavedItem {
  id: string;
  source_type: 'note' | 'url';
  title: string;
  content: string;
  source_url?: string | null;
  created_at: string;
}

export interface CitedSource {
  source_id: number;
  item_id: string;
  title: string;
  source_url?: string | null;
  snippet: string;
  similarity_score: number;
}

export interface QueryResponse {
  question: string;
  answer: string;
  sources: CitedSource[];
}

export interface ApiErrorResponse {
  success: boolean;
  detail: string;
  message?: string;
  status_code?: number;
  error_type?: string;
}

export interface IngestPayload {
  source_type: 'note' | 'url';
  content?: string;
  url?: string;
  title?: string;
}
