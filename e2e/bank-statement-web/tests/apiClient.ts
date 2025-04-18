import { APIRequestContext } from '@playwright/test';

export class ApiClient {
  private readonly request: APIRequestContext;
  private readonly baseUrl: string;

  constructor(request: APIRequestContext, baseUrl: string) {
    this.request = request;
    this.baseUrl = baseUrl.replace(/\/$/, '');
  }

  async get<T>(path: string): Promise<T> {
    const res = await this.request.get(`${this.baseUrl}${path}`);
    if (!res.ok()) throw new Error(`GET ${path} failed: ${res.status()}`);
    return res.json();
  }

  async post<T>(path: string, data: unknown): Promise<T> {
    const res = await this.request.post(`${this.baseUrl}${path}`, { data });
    if (!res.ok()) throw new Error(`POST ${path} failed: ${res.status()}`);
    return res.json();
  }
}

export class SourcesApi {
  private readonly api: ApiClient;
  constructor(api: ApiClient) {
    this.api = api;
  }

  async list() {
    return this.api.get<{ id: number; name: string }[]>('/sources');
  }

  async create(name: string) {
    return this.api.post<{ id: number; name: string }>('/sources', { name });
  }

  async ensureExists(name: string): Promise<{ id: number; name: string }> {
    const sources = await this.list();
    let found = sources.find((s) => s.name === name);
    if (!found) {
      found = await this.create(name);
    }
    return found;
  }
}
