import { api } from './api';
import type { Note, NoteCreateRequest, NoteUpdateRequest, NotesResponse, ExportResponse } from '../types/index';

export const noteApi = {
  // 创建笔记
  create: async (request: NoteCreateRequest): Promise<Note> => {
    const response = await api.post<Note>('/notes', request);
    return response.data;
  },

  // 更新笔记
  update: async (request: NoteUpdateRequest): Promise<void> => {
    await api.put('/notes', request);
  },

  // 获取所有笔记
  getAll: async (videoId: string): Promise<Note[]> => {
    const response = await api.get<NotesResponse>(`/notes/${videoId}`);
    return response.data.notes;
  },

  // 删除笔记
  delete: async (videoId: string, noteId: string): Promise<void> => {
    await api.delete(`/notes/${videoId}/${noteId}`);
  },

  // 导出笔记
  export: async (videoId: string): Promise<string> => {
    const response = await api.get<ExportResponse>(`/notes/export/${videoId}`);
    return response.data.markdown;
  },
};
