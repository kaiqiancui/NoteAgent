// ========== 视频相关类型 ==========

export interface Chapter {
  time: number;
  title: string;
}

export interface Subtitle {
  start: number;
  end: number;
  text: string;
}

export interface VideoAnalysis {
  summary: string;
  topics: string[];
  chapters: Chapter[];
  difficulty?: string;
}

export interface Video {
  id: string;
  filename: string;
  path: string;
  duration: number;
  file_hash?: string;
  analysis: VideoAnalysis;
  transcript: Subtitle[];
  created_at: string;
}

// ========== 笔记相关类型 ==========

export type NoteType = 'important' | 'question' | 'idea';

export interface Note {
  id: string;
  timestamp: number;
  type: NoteType;
  content: string;
  frame?: string; // base64 截图（可选）
  created_at: string;
  updated_at?: string;
}

export interface NoteCreateRequest {
  video_id: string;
  timestamp: number;
  type: NoteType;
  content?: string;
  frame?: string; // base64 截图（可选）
}

export interface NoteUpdateRequest {
  video_id: string;
  note_id: string;
  content: string;
}

// ========== API 响应类型 ==========

export interface UploadResponse {
  video_id: string;
  duration: number;
  analysis: VideoAnalysis;
  cached?: boolean;
}

export interface NotesResponse {
  notes: Note[];
}

export interface ExportResponse {
  markdown: string;
}

export interface FrameResponse {
  frame: string; // base64
}

// ========== 知识库相关类型 ==========

export type KnowledgeBaseFileType = 'pdf' | 'txt' | 'md' | 'docx' | 'doc';

export interface KnowledgeBase {
  id: string;
  name: string;
  file_type: KnowledgeBaseFileType;
  size: number; // 字节
  upload_date: string;
  content_preview?: string; // 前几行预览
  mock_chunks?: string[]; // 模拟的文档片段（用于Demo）
}

export interface AIQueryConfig {
  use_video_notes: boolean;
  knowledge_bases: string[]; // 选中的知识库ID列表
}
