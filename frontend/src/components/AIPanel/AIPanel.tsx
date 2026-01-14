import { useState, useRef, useEffect } from 'react';
import { Button, Input, message, Spin, Empty, Checkbox, Alert, Space, Tag } from 'antd';
import { CameraOutlined, SendOutlined, CopyOutlined, FileTextOutlined } from '@ant-design/icons';
import ReactMarkdown from 'react-markdown';
import { videoApi } from '../../services/videoApi';
import { aiWebSocket } from '../../services/websocket';
import { noteApi } from '../../services/noteApi';
import { formatTimestamp } from '../../utils/timeFormat';
import type { KnowledgeBase } from '../../types/index';
import './AIPanel.css';

const { TextArea } = Input;

const STORAGE_KEY = 'video_note_knowledge_bases';

interface AIPanelProps {
  videoId: string | null;
  currentTime: number;
}

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: number;
  frame?: string;
  usedKnowledgeBases?: string[]; // 使用的知识库名称列表
}

export function AIPanel({ videoId, currentTime }: AIPanelProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [streaming, setStreaming] = useState(false);
  const [currentAnswer, setCurrentAnswer] = useState('');
  const currentAnswerRef = useRef(''); // 用于在回调中访问最新的 answer
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // 知识库相关状态
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBase[]>([]);
  const [selectedKBIds, setSelectedKBIds] = useState<string[]>([]);

  // 生成笔记的loading状态
  const [generatingNoteId, setGeneratingNoteId] = useState<string | null>(null);

  // 加载知识库列表
  useEffect(() => {
    const loadKnowledgeBases = () => {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        try {
          const parsed = JSON.parse(stored);
          setKnowledgeBases(parsed);
        } catch (error) {
          console.error('Failed to load knowledge bases:', error);
        }
      }
    };

    // 初次加载
    loadKnowledgeBases();

    // 监听知识库更新事件
    const handleKnowledgeBaseUpdate = () => {
      console.log('[AIPanel] 检测到知识库更新，重新加载...');
      loadKnowledgeBases();
    };

    window.addEventListener('knowledgeBaseUpdated', handleKnowledgeBaseUpdate);

    // 清理监听器
    return () => {
      window.removeEventListener('knowledgeBaseUpdated', handleKnowledgeBaseUpdate);
    };
  }, []);

  // 当知识库列表变化时，清理无效的选中项
  useEffect(() => {
    const validKBIds = knowledgeBases.map((kb) => kb.id);

    setSelectedKBIds((prevSelectedIds) => {
      const filteredIds = prevSelectedIds.filter((id) => validKBIds.includes(id));
      // 只在有变化时返回新数组
      return filteredIds.length !== prevSelectedIds.length ? filteredIds : prevSelectedIds;
    });
  }, [knowledgeBases]);

  // 构建知识库增强的上下文（模拟 RAG）
  const buildKnowledgeContext = (): string => {
    if (selectedKBIds.length === 0) return '';

    const selectedKBs = knowledgeBases.filter((kb) => selectedKBIds.includes(kb.id));
    if (selectedKBs.length === 0) return '';

    let context = '\n\n📚 **参考以下知识库内容回答问题**：\n\n';

    selectedKBs.forEach((kb) => {
      context += `**来自《${kb.name}》**：\n`;
      // 随机选择一些片段（模拟检索结果）
      const chunks = kb.mock_chunks || [];
      const selectedChunks = chunks.slice(0, 2); // 取前2个片段
      selectedChunks.forEach((chunk) => {
        context += `- ${chunk}\n`;
      });
      context += '\n';
    });

    context += '请基于以上知识库内容回答用户问题，并在回答中标注内容来源。\n';
    return context;
  };

  // 自动滚动到底部
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, currentAnswer]);

  // 截图并提问
  const handleScreenshotAndAsk = async () => {
    if (!videoId) {
      message.warning('请先上传视频');
      return;
    }

    if (!question.trim()) {
      message.warning('请输入问题');
      return;
    }

    try {
      setLoading(true);

      // 1. 获取当前帧
      const frameData = await videoApi.getFrame(videoId, Math.floor(currentTime));

      // 2. 构建增强的问题（附加知识库上下文）
      const knowledgeContext = buildKnowledgeContext();
      const enhancedQuestion = question + knowledgeContext;

      // 记录使用的知识库名称
      const usedKBNames = knowledgeBases
        .filter((kb) => selectedKBIds.includes(kb.id))
        .map((kb) => kb.name);

      // 3. 添加用户消息（不显示知识库标签）
      const userMessage: Message = {
        role: 'user',
        content: question,
        timestamp: Math.floor(currentTime),
        frame: frameData.frame,
      };
      setMessages((prev) => [...prev, userMessage]);

      // 4. 连接 WebSocket 并发送问题
      setStreaming(true);
      setCurrentAnswer('');
      currentAnswerRef.current = '';

      await aiWebSocket.askQuestion(
        videoId,
        Math.floor(currentTime),
        enhancedQuestion, // 发送增强后的问题
        frameData.frame,
        (chunk: string) => {
          // 接收流式响应
          currentAnswerRef.current += chunk;
          setCurrentAnswer(currentAnswerRef.current);
        },
        () => {
          // 完成 - 先添加消息，再清空状态
          const finalAnswer = currentAnswerRef.current;
          console.log('[AIPanel] 回答完成，内容长度:', finalAnswer.length);

          // 1. 先添加到消息历史
          setMessages((prev) => [
            ...prev,
            {
              role: 'assistant',
              content: finalAnswer,
              timestamp: Math.floor(currentTime),
              usedKnowledgeBases: usedKBNames.length > 0 ? usedKBNames : undefined,
            },
          ]);

          // 2. 然后清空流式状态（稍微延迟，确保消息已添加）
          setTimeout(() => {
            setStreaming(false);
            setCurrentAnswer('');
            currentAnswerRef.current = '';
          }, 50);
        }
      );

      // 5. 清空输入框
      setQuestion('');
    } catch (error) {
      console.error('Failed to ask question:', error);
      message.error('提问失败，请重试');
      setStreaming(false);
      setCurrentAnswer('');
    } finally {
      setLoading(false);
    }
  };

  // 快速提问（不截图）
  const handleQuickAsk = async () => {
    if (!videoId) {
      message.warning('请先上传视频');
      return;
    }

    if (!question.trim()) {
      message.warning('请输入问题');
      return;
    }

    try {
      setLoading(true);

      // 1. 构建增强的问题（附加知识库上下文）
      const knowledgeContext = buildKnowledgeContext();
      const enhancedQuestion = question + knowledgeContext;

      // 记录使用的知识库名称
      const usedKBNames = knowledgeBases
        .filter((kb) => selectedKBIds.includes(kb.id))
        .map((kb) => kb.name);

      // 2. 添加用户消息（无截图，不显示知识库标签）
      const userMessage: Message = {
        role: 'user',
        content: question,
        timestamp: Math.floor(currentTime),
      };
      setMessages((prev) => [...prev, userMessage]);

      // 3. 连接 WebSocket 并发送问题（空帧）
      setStreaming(true);
      setCurrentAnswer('');
      currentAnswerRef.current = '';

      await aiWebSocket.askQuestion(
        videoId,
        Math.floor(currentTime),
        enhancedQuestion, // 发送增强后的问题
        '', // 空帧
        (chunk: string) => {
          currentAnswerRef.current += chunk;
          setCurrentAnswer(currentAnswerRef.current);
        },
        () => {
          // 完成 - 先添加消息，再清空状态
          const finalAnswer = currentAnswerRef.current;
          console.log('[AIPanel] 纯文本回答完成，内容长度:', finalAnswer.length);

          // 1. 先添加到消息历史
          setMessages((prev) => [
            ...prev,
            {
              role: 'assistant',
              content: finalAnswer,
              timestamp: Math.floor(currentTime),
              usedKnowledgeBases: usedKBNames.length > 0 ? usedKBNames : undefined,
            },
          ]);

          // 2. 然后清空流式状态（稍微延迟，确保消息已添加）
          setTimeout(() => {
            setStreaming(false);
            setCurrentAnswer('');
            currentAnswerRef.current = '';
          }, 50);
        }
      );

      setQuestion('');
    } catch (error) {
      console.error('Failed to ask question:', error);
      message.error('提问失败，请重试');
      setStreaming(false);
      setCurrentAnswer('');
    } finally {
      setLoading(false);
    }
  };

  // 前端模拟AI润色笔记（提取关键内容）
  const polishNoteContent = (rawContent: string): string => {
    // 1. 提取标题（## 开头的部分）
    const titleMatch = rawContent.match(/^##\s+(.+)$/m);
    const title = titleMatch ? titleMatch[1] : '笔记要点';

    // 2. 提取列表项（- 或数字开头）
    const listItems = rawContent.match(/^[\s]*[-*•]\s+(.+)$/gm) || [];
    const numberedItems = rawContent.match(/^[\s]*\d+\.\s+(.+)$/gm) || [];
    const allItems = [...listItems, ...numberedItems];

    // 3. 提取代码块
    const codeBlocks = rawContent.match(/```[\s\S]*?```/g) || [];

    // 4. 如果没有结构化内容，提取前200字
    if (allItems.length === 0 && codeBlocks.length === 0) {
      const plainText = rawContent
        .replace(/[#*`]/g, '') // 移除markdown符号
        .replace(/\n\n+/g, '\n') // 合并多余换行
        .trim();

      const summary = plainText.substring(0, 200) + (plainText.length > 200 ? '...' : '');
      return `## ${title}\n\n${summary}`;
    }

    // 5. 构建笔记
    let note = `## ${title}\n\n`;

    if (allItems.length > 0) {
      note += '### 核心要点\n';
      // 最多取前5个要点
      allItems.slice(0, 5).forEach((item) => {
        // 清理格式，保留纯文本
        const cleanItem = item.replace(/^[\s]*[-*•\d.]+\s+/, '').trim();
        note += `- ${cleanItem}\n`;
      });
      note += '\n';
    }

    if (codeBlocks.length > 0) {
      note += '### 代码示例\n';
      note += codeBlocks[0] + '\n\n'; // 只取第一个代码块
    }

    return note.trim();
  };

  // 生成笔记（AI润色）
  const handleGenerateNote = async (content: string, timestamp: number, messageIndex: number) => {
    if (!videoId) {
      message.warning('请先上传视频');
      return;
    }

    try {
      // 设置loading状态
      setGeneratingNoteId(`${messageIndex}`);

      // 模拟AI处理（2秒）
      await new Promise((resolve) => setTimeout(resolve, 2000));

      // 前端润色内容
      const polishedContent = polishNoteContent(content);

      // 获取当前时刻的截图
      const frameData = await videoApi.getFrame(videoId, Math.floor(timestamp));

      // 保存笔记
      await noteApi.create({
        video_id: videoId,
        timestamp: Math.floor(timestamp),
        type: 'idea', // 默认使用"想法"类型
        content: polishedContent + '\n\n---\n*🤖 AI生成笔记*',
        frame: frameData.frame, // 附带截图
      });

      // 触发笔记更新事件
      window.dispatchEvent(new CustomEvent('noteUpdated'));

      message.success('笔记已生成并保存！');

      // 提示用户切换到笔记Tab查看
      setTimeout(() => {
        message.info('已添加到笔记Tab，可以查看和编辑', 3);
      }, 500);
    } catch (error) {
      console.error('Failed to generate note:', error);
      message.error('生成笔记失败');
    } finally {
      setGeneratingNoteId(null);
    }
  };

  // 复制 AI 回答到笔记（保留旧功能，但不再使用）
  const handleCopyToNote = async (content: string, timestamp: number) => {
    if (!videoId) {
      message.warning('请先上传视频');
      return;
    }

    try {
      // 获取当前时刻的截图
      const frameData = await videoApi.getFrame(videoId, Math.floor(timestamp));

      await noteApi.create({
        video_id: videoId,
        timestamp: Math.floor(timestamp),
        type: 'idea', // 默认使用"想法"类型
        content,
        frame: frameData.frame, // 附带截图
      });
      message.success('已添加到笔记');
    } catch (error) {
      console.error('Failed to copy to note:', error);
      message.error('添加笔记失败');
    }
  };

  return (
    <div className="ai-panel">
      {/* 消息历史 */}
      <div className="messages-section">
        {messages.length === 0 && !streaming ? (
          <Empty description="开始与 AI 对话" />
        ) : (
          <div className="messages-list">
            {messages.map((msg, index) => (
              <div key={index} className={`message ${msg.role}`}>
                <div className="message-header">
                  <span className="message-role">
                    {msg.role === 'user' ? '👤 你' : '🤖 AI'}
                  </span>
                  <span className="message-time">{formatTimestamp(msg.timestamp)}</span>
                </div>

                {/* 显示使用的知识库（只在AI回答中显示） */}
                {msg.role === 'assistant' && msg.usedKnowledgeBases && msg.usedKnowledgeBases.length > 0 && (
                  <Alert
                    type="info"
                    message={
                      <div className="kb-tags-wrapper">
                        <span className="kb-tags-label">📚 使用知识库：</span>
                        <div className="kb-tags-container">
                          {msg.usedKnowledgeBases.map((kbName, idx) => (
                            <Tag key={idx} icon={<FileTextOutlined />} color="blue">
                              {kbName}
                            </Tag>
                          ))}
                        </div>
                      </div>
                    }
                    style={{ marginBottom: 8, padding: '4px 8px' }}
                    showIcon={false}
                  />
                )}

                {msg.frame && (
                  <div className="message-frame">
                    <img src={`data:image/jpeg;base64,${msg.frame}`} alt="Video frame" />
                  </div>
                )}

                <div className="message-content">
                  <ReactMarkdown>{msg.content}</ReactMarkdown>
                </div>

                {/* AI 消息添加生成笔记按钮 */}
                {msg.role === 'assistant' && (
                  <div className="message-actions">
                    <Button
                      size="small"
                      icon={<CopyOutlined />}
                      onClick={() => handleGenerateNote(msg.content, msg.timestamp, index)}
                      loading={generatingNoteId === `${index}`}
                      disabled={generatingNoteId !== null}
                    >
                      {generatingNoteId === `${index}` ? '生成中...' : '生成笔记'}
                    </Button>
                  </div>
                )}
              </div>
            ))}

            {/* 流式响应 */}
            {streaming && (
              <div className="message assistant">
                <div className="message-header">
                  <span className="message-role">🤖 AI</span>
                  <span className="message-time">{formatTimestamp(Math.floor(currentTime))}</span>
                </div>
                <div className="message-content streaming">
                  <ReactMarkdown>{currentAnswer || '正在思考...'}</ReactMarkdown>
                  <Spin size="small" style={{ marginLeft: '8px' }} />
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* 知识库选择区域 */}
      {knowledgeBases.length > 0 && (
        <div className="kb-selector-section">
          <div className="kb-selector-header">
            <span>📚 使用知识库增强回答：</span>
          </div>
          <Checkbox.Group
            value={selectedKBIds}
            onChange={(checkedValues) => setSelectedKBIds(checkedValues as string[])}
            className="kb-checkbox-group"
          >
            {knowledgeBases.map((kb) => (
              <Checkbox key={kb.id} value={kb.id}>
                {kb.name}
              </Checkbox>
            ))}
          </Checkbox.Group>
        </div>
      )}

      {/* 输入区域 */}
      <div className="input-section">
        <TextArea
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="输入你的问题..."
          autoSize={{ minRows: 2, maxRows: 4 }}
          disabled={loading || streaming || !videoId}
          onPressEnter={(e) => {
            if (e.shiftKey) {
              return; // Shift+Enter 换行
            }
            e.preventDefault();
            handleQuickAsk();
          }}
        />

        <div className="input-actions">
          <Button
            icon={<CameraOutlined />}
            onClick={handleScreenshotAndAsk}
            loading={loading}
            disabled={!videoId || !question.trim() || streaming}
          >
            截图提问
          </Button>
          <Button
            type="primary"
            icon={<SendOutlined />}
            onClick={handleQuickAsk}
            loading={loading}
            disabled={!videoId || !question.trim() || streaming}
          >
            发送
          </Button>
        </div>
      </div>
    </div>
  );
}
