import { api } from './api';
import type { Video, UploadResponse, FrameResponse } from '../types/index';

export const videoApi = {
  // 上传视频
  upload: async (file: File, onProgress?: (progress: number) => void): Promise<UploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post<UploadResponse>('/videos/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (progressEvent) => {
        if (progressEvent.total && onProgress) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(progress);
        }
      },
    });

    return response.data;
  },

  // 获取视频信息
  get: async (videoId: string): Promise<Video> => {
    const response = await api.get<Video>(`/videos/${videoId}`);
    return response.data;
  },

  // 获取指定时间的帧
  getFrame: async (videoId: string, timestamp: number): Promise<FrameResponse> => {
    const response = await api.get<FrameResponse>(`/videos/${videoId}/frame`, {
      params: { timestamp },
    });
    return response.data;
  },
};
