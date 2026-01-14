import { useState, useEffect } from 'react';
import { Upload, Button, Card, Space, Tag, Empty, message, Popconfirm } from 'antd';
import {
  InboxOutlined,
  FileTextOutlined,
  FilePdfOutlined,
  FileMarkdownOutlined,
  FileWordOutlined,
  DeleteOutlined,
} from '@ant-design/icons';
import type { UploadProps } from 'antd';
import type { KnowledgeBase, KnowledgeBaseFileType } from '../../types/index';
import './KnowledgePanel.css';

const { Dragger } = Upload;

// 预设的示例知识库（用于Demo演示）
const DEMO_KNOWLEDGE_BASES: KnowledgeBase[] = [
  {
    id: 'demo-1',
    name: 'React官方文档.pdf',
    file_type: 'pdf',
    size: 2400000,
    upload_date: new Date('2026-01-10T10:00:00Z').toISOString(),
    content_preview: 'React 是一个用于构建用户界面的 JavaScript 库...',
    mock_chunks: [
      'React Hooks 是 React 16.8 引入的新特性，它让你可以在不编写 class 的情况下使用 state 以及其他的 React 特性。',
      'useState 是最常用的 Hook，用于在函数组件中添加状态管理。它返回一个状态值和一个更新该状态的函数。',
      'useEffect 用于处理副作用，如数据获取、订阅、手动修改 DOM 等。它在组件渲染后执行。',
      'useContext 让你可以订阅 React context 而不需要引入嵌套。',
    ],
  },
  {
    id: 'demo-2',
    name: 'JavaScript高级教程.txt',
    file_type: 'txt',
    size: 856000,
    upload_date: new Date('2026-01-12T14:30:00Z').toISOString(),
    content_preview: 'JavaScript 是一门动态、弱类型的编程语言...',
    mock_chunks: [
      '闭包是 JavaScript 中的重要概念，它允许函数访问其词法作用域外的变量。',
      '原型链是 JavaScript 继承的基础。每个对象都有一个原型对象，对象以原型为模板继承属性和方法。',
      'Promise 是异步编程的一种解决方案，比回调函数更加优雅和强大。',
    ],
  },
];

const STORAGE_KEY = 'video_note_knowledge_bases';

export function KnowledgePanel() {
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBase[]>([]);

  // 加载知识库（从 localStorage）
  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      try {
        const parsed = JSON.parse(stored);
        setKnowledgeBases(parsed);
      } catch (error) {
        console.error('Failed to load knowledge bases:', error);
        // 加载失败，使用演示数据
        setKnowledgeBases(DEMO_KNOWLEDGE_BASES);
        localStorage.setItem(STORAGE_KEY, JSON.stringify(DEMO_KNOWLEDGE_BASES));
      }
    } else {
      // 首次使用，加载演示数据
      setKnowledgeBases(DEMO_KNOWLEDGE_BASES);
      localStorage.setItem(STORAGE_KEY, JSON.stringify(DEMO_KNOWLEDGE_BASES));
    }
  }, []);

  // 保存到 localStorage
  const saveToStorage = (kbs: KnowledgeBase[]) => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(kbs));
    // 触发自定义事件，通知其他组件知识库已更新
    window.dispatchEvent(new CustomEvent('knowledgeBaseUpdated'));
  };

  // 获取文件类型
  const getFileType = (filename: string): KnowledgeBaseFileType => {
    const ext = filename.split('.').pop()?.toLowerCase();
    if (ext === 'pdf') return 'pdf';
    if (ext === 'txt') return 'txt';
    if (ext === 'md') return 'md';
    if (ext === 'docx' || ext === 'doc') return 'docx';
    return 'txt';
  };

  // 获取文件图标
  const getFileIcon = (fileType: KnowledgeBaseFileType) => {
    switch (fileType) {
      case 'pdf':
        return <FilePdfOutlined style={{ fontSize: 24, color: '#ff4d4f' }} />;
      case 'md':
        return <FileMarkdownOutlined style={{ fontSize: 24, color: '#1890ff' }} />;
      case 'docx':
      case 'doc':
        return <FileWordOutlined style={{ fontSize: 24, color: '#1890ff' }} />;
      default:
        return <FileTextOutlined style={{ fontSize: 24, color: '#8c8c8c' }} />;
    }
  };

  // 格式化文件大小
  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  // 格式化日期
  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
    });
  };

  // 简单的文本分段（模拟切分）
  const splitContent = (content: string): string[] => {
    // 按段落分割
    const paragraphs = content.split(/\n\n+/).filter((p) => p.trim());
    // 每段最多500字符
    const chunks: string[] = [];
    paragraphs.forEach((para) => {
      if (para.length <= 500) {
        chunks.push(para);
      } else {
        // 长段落按句子分割
        const sentences = para.match(/[^.!?。！？]+[.!?。！？]+/g) || [para];
        let currentChunk = '';
        sentences.forEach((sentence) => {
          if ((currentChunk + sentence).length <= 500) {
            currentChunk += sentence;
          } else {
            if (currentChunk) chunks.push(currentChunk);
            currentChunk = sentence;
          }
        });
        if (currentChunk) chunks.push(currentChunk);
      }
    });
    return chunks.slice(0, 10); // 最多保留10个片段
  };

  // 生成唯一ID
  const generateId = (): string => {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
  };

  // 文件上传处理
  const uploadProps: UploadProps = {
    name: 'file',
    accept: '.pdf,.txt,.md,.docx,.doc',
    showUploadList: false,
    beforeUpload: (file) => {
      // 检查文件大小（限制 10MB，因为是前端存储）
      const maxSize = 10 * 1024 * 1024;
      if (file.size > maxSize) {
        message.error('文件不能超过 10MB（前端存储限制）');
        return false;
      }

      const reader = new FileReader();
      reader.onload = (e) => {
        const content = e.target?.result as string;

        // 创建知识库对象
        const kb: KnowledgeBase = {
          id: generateId(),
          name: file.name,
          file_type: getFileType(file.name),
          size: file.size,
          upload_date: new Date().toISOString(),
          content_preview: content.substring(0, 200),
          mock_chunks: splitContent(content),
        };

        const newKBs = [...knowledgeBases, kb];
        setKnowledgeBases(newKBs);
        saveToStorage(newKBs);
        message.success(`${file.name} 上传成功！`);
      };

      reader.onerror = () => {
        message.error('文件读取失败');
      };

      reader.readAsText(file, 'UTF-8');
      return false; // 阻止默认上传行为
    },
  };

  // 删除知识库
  const handleDelete = (id: string) => {
    const newKBs = knowledgeBases.filter((kb) => kb.id !== id);
    setKnowledgeBases(newKBs);
    saveToStorage(newKBs);
    message.success('知识库已删除');
  };

  return (
    <div className="knowledge-panel">
      {/* 上传区域 */}
      <div className="upload-section">
        <Dragger {...uploadProps}>
          <p className="ant-upload-drag-icon">
            <InboxOutlined />
          </p>
          <p className="ant-upload-text">点击或拖拽文件到此区域上传</p>
          <p className="ant-upload-hint">
            支持 PDF、TXT、Markdown、Word 文档（最大 10MB）
          </p>
        </Dragger>
      </div>

      {/* 知识库列表 */}
      <div className="kb-list-section">
        <h3 className="kb-list-title">我的知识库 ({knowledgeBases.length})</h3>

        {knowledgeBases.length === 0 ? (
          <Empty description="暂无知识库，请上传文件" />
        ) : (
          <div className="kb-list">
            {knowledgeBases.map((kb) => (
              <Card key={kb.id} className="kb-card" hoverable>
                <div className="kb-card-content">
                  <div className="kb-icon">{getFileIcon(kb.file_type)}</div>

                  <div className="kb-info">
                    <h4 className="kb-name">{kb.name}</h4>

                    <Space size="small" className="kb-meta">
                      <Tag>{formatFileSize(kb.size)}</Tag>
                      <Tag color="blue">{kb.file_type.toUpperCase()}</Tag>
                    </Space>

                    <p className="kb-date">上传于 {formatDate(kb.upload_date)}</p>

                    {kb.content_preview && (
                      <p className="kb-preview">{kb.content_preview}...</p>
                    )}
                  </div>

                  <div className="kb-actions">
                    <Popconfirm
                      title="确定删除这个知识库吗？"
                      onConfirm={() => handleDelete(kb.id)}
                      okText="确定"
                      cancelText="取消"
                    >
                      <Button type="text" danger icon={<DeleteOutlined />} />
                    </Popconfirm>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
