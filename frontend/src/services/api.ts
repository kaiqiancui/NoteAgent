import axios from 'axios';

// 创建 axios 实例
export const api = axios.create({
  baseURL: '/api', // 通过 Vite 代理到 http://localhost:8000/api
  timeout: 600000, // 10 分钟（视频上传可能较长）
  headers: {
    'Content-Type': 'application/json',
  },
});

// 响应拦截器
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);
