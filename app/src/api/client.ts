import {API_BASE_URL} from '../constants/config';
import type {Quote, CategoryGroup, SituationGroup, AuthorListItem} from '../types';

const BASE = `${API_BASE_URL}/app/api/v1`;

async function fetchJSON<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(url, options);
  if (!res.ok) {
    throw new Error(`API error: ${res.status}`);
  }
  return res.json();
}

export function fetchDailyQuote(params?: {situations?: string; keywords?: string; exclude?: string}): Promise<Quote> {
  const qs = params ? '?' + new URLSearchParams(params).toString() : '';
  return fetchJSON<Quote>(`${BASE}/daily${qs}`);
}

export function fetchRecommend(params: {situations?: string; keywords?: string; exclude?: string; limit?: string}): Promise<Quote[]> {
  const qs = new URLSearchParams(params).toString();
  return fetchJSON<Quote[]>(`${BASE}/recommend?${qs}`);
}

export function fetchCategories(): Promise<CategoryGroup[]> {
  return fetchJSON<CategoryGroup[]>(`${BASE}/categories`);
}

export function fetchSituations(): Promise<SituationGroup[]> {
  return fetchJSON<SituationGroup[]>(`${BASE}/situations`);
}

export function fetchAuthors(page = 1, limit = 20): Promise<AuthorListItem[]> {
  return fetchJSON<AuthorListItem[]>(`${BASE}/authors?page=${page}&limit=${limit}`);
}

export function fetchQuotes(params: Record<string, string>): Promise<Quote[]> {
  const qs = new URLSearchParams(params).toString();
  return fetchJSON<Quote[]>(`${BASE}/quotes?${qs}`);
}

export function fetchQuoteDetail(id: string): Promise<Quote> {
  return fetchJSON<Quote>(`${BASE}/quotes/${id}`);
}

export function fetchQuotesBatch(ids: string[]): Promise<Quote[]> {
  return fetchJSON<Quote[]>(`${BASE}/quotes/batch`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ids}),
  });
}
