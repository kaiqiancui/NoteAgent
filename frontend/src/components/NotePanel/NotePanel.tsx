import { useState, useEffect, useRef } from 'react';
import { Button, List, Tag, Input, Popconfirm, message, Space, Empty } from 'antd';
import {
  BulbOutlined,
  QuestionCircleOutlined,
  ExclamationCircleOutlined,
  DeleteOutlined,
  ExportOutlined,
  CameraOutlined,
} from '@ant-design/icons';
import ReactMarkdown from 'react-markdown';
import type { Note, NoteType } from '../../types/index';
import { noteApi } from '../../services/noteApi';
import { videoApi } from '../../services/videoApi';
import { formatTimestamp } from '../../utils/timeFormat';
import './NotePanel.css';

const { TextArea } = Input;

interface NotePanelProps {
  videoId: string | null;
  currentTime: number;
  onNoteClick?: (timestamp: number) => void;
}

const noteTypeConfig = {
  important: {
    label: '重要',
    icon: <ExclamationCircleOutlined />,
    color: 'red',
  },
  question: {
    label: '问题',
    icon: <QuestionCircleOutlined />,
    color: 'orange',
  },
  idea: {
    label: '想法',
    icon: <BulbOutlined />,
    color: 'blue',
  },
};

export function NotePanel({ videoId, currentTime, onNoteClick }: NotePanelProps) {
  const [notes, setNotes] = useState<Note[]>([]);
  const [editingNote, setEditingNote] = useState<string | null>(null);
  const [editContent, setEditContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [highlightedNote, setHighlightedNote] = useState<string | null>(null);
  const noteRefs = useRef<{ [key: string]: HTMLDivElement | null }>({});
  const textAreaRef = useRef<any>(null);
  const [insertingScreenshot, setInsertingScreenshot] = useState(false);

  // 加载笔记
  useEffect(() => {
    if (videoId) {
      loadNotes();
    }
  }, [videoId]);

  // 监听笔记更新事件（从AI助手生成笔记）
  useEffect(() => {
    const handleNoteUpdate = () => {
      console.log('[NotePanel] 检测到笔记更新，重新加载...');
      if (videoId) {
        loadNotes();
      }
    };

    window.addEventListener('noteUpdated', handleNoteUpdate);

    // 清理监听器
    return () => {
      window.removeEventListener('noteUpdated', handleNoteUpdate);
    };
  }, [videoId]);

  const loadNotes = async () => {
    if (!videoId) return;

    try {
      setLoading(true);
      const data = await noteApi.getAll(videoId);
      setNotes(data);
    } catch (error) {
      console.error('Failed to load notes:', error);
      message.error('加载笔记失败');
    } finally {
      setLoading(false);
    }
  };

  // 快速创建笔记
  const handleQuickMark = async (type: NoteType) => {
    if (!videoId) {
      message.warning('请先上传视频');
      return;
    }

    try {
      // 1. 获取当前帧
      const frameData = await videoApi.getFrame(videoId, Math.floor(currentTime));

      // 2. 创建笔记（附带截图）
      const newNote = await noteApi.create({
        video_id: videoId,
        timestamp: Math.floor(currentTime),
        type,
        content: '', // 空内容，后续可编辑
        frame: frameData.frame, // 附带截图
      });

      setNotes([...notes, newNote]);
      message.success('标记已添加');

      // 等待 DOM 更新后，滚动到新笔记并进入编辑模式
      setTimeout(() => {
        // 滚动到新笔记
        const noteElement = noteRefs.current[newNote.id];
        if (noteElement) {
          noteElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }

        // 添加高亮效果
        setHighlightedNote(newNote.id);
        setTimeout(() => setHighlightedNote(null), 2000);

        // 自动进入编辑模式
        setEditingNote(newNote.id);
        setEditContent('');

        // 聚焦到输入框
        setTimeout(() => {
          textAreaRef.current?.focus();
        }, 100);
      }, 100);
    } catch (error) {
      console.error('Failed to create note:', error);
      message.error('添加标记失败');
    }
  };

  // 开始编辑笔记
  const startEdit = (note: Note) => {
    setEditingNote(note.id);
    setEditContent(note.content);
  };

  // 保存编辑
  const saveEdit = async (noteId: string) => {
    if (!videoId) return;

    try {
      await noteApi.update({
        video_id: videoId,
        note_id: noteId,
        content: editContent,
      });

      setNotes(
        notes.map((n) =>
          n.id === noteId ? { ...n, content: editContent, updated_at: new Date().toISOString() } : n
        )
      );

      setEditingNote(null);
      message.success('笔记已保存');
    } catch (error) {
      console.error('Failed to update note:', error);
      message.error('保存失败');
    }
  };

  // 取消编辑
  const cancelEdit = () => {
    setEditingNote(null);
    setEditContent('');
  };

  // 插入截图到笔记
  const handleInsertScreenshot = async () => {
    if (!videoId) {
      message.warning('请先上传视频');
      return;
    }

    if (!textAreaRef.current) {
      message.error('编辑器未就绪');
      return;
    }

    try {
      setInsertingScreenshot(true);

      // 获取当前时刻的截图
      const frameData = await videoApi.getFrame(videoId, Math.floor(currentTime));

      // 获取TextArea的DOM元素和光标位置
      const textarea = textAreaRef.current.resizableTextArea.textArea;
      const cursorPosition = textarea.selectionStart;
      const textBefore = editContent.substring(0, cursorPosition);
      const textAfter = editContent.substring(cursorPosition);

      // 构建Markdown格式的截图
      const timestamp = formatTimestamp(Math.floor(currentTime));
      const screenshotMarkdown = `\n\n![视频截图 ${timestamp}](data:image/jpeg;base64,${frameData.frame})\n\n`;

      // 插入截图
      const newContent = textBefore + screenshotMarkdown + textAfter;
      setEditContent(newContent);

      // 将光标移动到插入内容之后
      setTimeout(() => {
        const newCursorPosition = cursorPosition + screenshotMarkdown.length;
        textarea.setSelectionRange(newCursorPosition, newCursorPosition);
        textarea.focus();
      }, 0);

      message.success('截图已插入');
    } catch (error) {
      console.error('Failed to insert screenshot:', error);
      message.error('插入截图失败');
    } finally {
      setInsertingScreenshot(false);
    }
  };

  // 删除笔记
  const deleteNote = async (noteId: string) => {
    if (!videoId) return;

    try {
      await noteApi.delete(videoId, noteId);
      setNotes(notes.filter((n) => n.id !== noteId));
      message.success('笔记已删除');
    } catch (error) {
      console.error('Failed to delete note:', error);
      message.error('删除失败');
    }
  };

  // 导出笔记
  const exportNotes = async () => {
    if (!videoId) {
      message.warning('请先上传视频');
      return;
    }

    try {
      const markdown = await noteApi.export(videoId);

      // 创建下载链接
      const blob = new Blob([markdown], { type: 'text/markdown' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `notes_${videoId}.md`;
      a.click();
      URL.revokeObjectURL(url);

      message.success('笔记已导出');
    } catch (error) {
      console.error('Failed to export notes:', error);
      message.error('导出失败');
    }
  };

  // 点击时间戳跳转
  const handleTimestampClick = (timestamp: number) => {
    if (onNoteClick) {
      onNoteClick(timestamp);
    }
    // 也可以直接调用全局方法
    if ((window as any).videoPlayerSeekTo) {
      (window as any).videoPlayerSeekTo(timestamp);
    }
  };

  return (
    <div className="note-panel">
      {/* 笔记列表 */}
      <div className="notes-list-section">
        {!videoId ? (
          <Empty description="请先上传视频" />
        ) : notes.length === 0 ? (
          <Empty description="暂无笔记" />
        ) : (
          <List
            loading={loading}
            dataSource={notes.sort((a, b) => a.timestamp - b.timestamp)}
            renderItem={(note) => (
              <List.Item
                className={`note-item ${highlightedNote === note.id ? 'highlighted' : ''}`}
                ref={(el) => (noteRefs.current[note.id] = el)}
              >
                <div className="note-content">
                  {/* 头部：标签 + 时间戳 + 删除 */}
                  <div className="note-header">
                    <Space>
                      <Tag color={noteTypeConfig[note.type].color} icon={noteTypeConfig[note.type].icon}>
                        {noteTypeConfig[note.type].label}
                      </Tag>
                      <span
                        className="note-timestamp"
                        onClick={() => handleTimestampClick(note.timestamp)}
                      >
                        {formatTimestamp(note.timestamp)}
                      </span>
                    </Space>

                    <Popconfirm
                      title="确定删除这条笔记吗？"
                      onConfirm={() => deleteNote(note.id)}
                      okText="确定"
                      cancelText="取消"
                    >
                      <Button
                        type="text"
                        danger
                        size="small"
                        icon={<DeleteOutlined />}
                      />
                    </Popconfirm>
                  </div>

                  {/* 截图显示（如果有） */}
                  {note.frame && (
                    <div className="note-frame">
                      <img src={`data:image/jpeg;base64,${note.frame}`} alt="Note frame" />
                    </div>
                  )}

                  {/* 内容区域 */}
                  {editingNote === note.id ? (
                    <div className="note-editor">
                      <TextArea
                        ref={textAreaRef}
                        value={editContent}
                        onChange={(e) => setEditContent(e.target.value)}
                        rows={4}
                        placeholder="输入笔记内容（支持 Markdown）"
                      />
                      <div className="editor-actions">
                        <Button
                          size="small"
                          icon={<CameraOutlined />}
                          onClick={handleInsertScreenshot}
                          loading={insertingScreenshot}
                          disabled={insertingScreenshot}
                        >
                          插入截图
                        </Button>
                        <div style={{ flex: 1 }}></div>
                        <Button size="small" onClick={cancelEdit}>
                          取消
                        </Button>
                        <Button type="primary" size="small" onClick={() => saveEdit(note.id)}>
                          保存
                        </Button>
                      </div>
                    </div>
                  ) : (
                    <div className="note-display" onClick={() => startEdit(note)}>
                      {note.content ? (
                        <ReactMarkdown>{note.content}</ReactMarkdown>
                      ) : (
                        <span className="empty-note">点击编辑笔记内容</span>
                      )}
                    </div>
                  )}
                </div>
              </List.Item>
            )}
          />
        )}
      </div>

      {/* 快速标记按钮（移到底部） */}
      <div className="quick-mark-section">
        <div className="quick-mark-buttons">
          {(Object.keys(noteTypeConfig) as NoteType[]).map((type) => {
            const config = noteTypeConfig[type];
            return (
              <Button
                key={type}
                icon={config.icon}
                onClick={() => handleQuickMark(type)}
                disabled={!videoId}
                block
              >
                {config.label}
              </Button>
            );
          })}
        </div>

        <Button
          icon={<ExportOutlined />}
          onClick={exportNotes}
          disabled={!videoId || notes.length === 0}
          block
          type="dashed"
          style={{ marginTop: '8px' }}
        >
          导出笔记
        </Button>
      </div>
    </div>
  );
}
