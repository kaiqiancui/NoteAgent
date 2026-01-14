import { useState } from 'react';
import { Tabs } from 'antd';
import type { TabsProps } from 'antd';
import './MainLayout.css';

interface MainLayoutProps {
  leftPanel: React.ReactNode;
  notePanel: React.ReactNode;
  aiPanel: React.ReactNode;
  kbPanel: React.ReactNode;
}

export function MainLayout({ leftPanel, notePanel, aiPanel, kbPanel }: MainLayoutProps) {
  const [activeTab, setActiveTab] = useState<'notes' | 'ai' | 'kb'>('notes');

  const tabItems: TabsProps['items'] = [
    {
      key: 'notes',
      label: '📝 笔记',
      children: notePanel,
    },
    {
      key: 'ai',
      label: '🤖 AI 助手',
      children: aiPanel,
    },
    {
      key: 'kb',
      label: '📚 知识库',
      children: kbPanel,
    },
  ];

  return (
    <div className="main-layout">
      {/* 左侧：视频播放器 */}
      <div className="left-panel">
        {leftPanel}
      </div>

      {/* 右侧：笔记/AI 面板 */}
      <div className="right-panel">
        <Tabs
          activeKey={activeTab}
          items={tabItems}
          onChange={(key) => setActiveTab(key as 'notes' | 'ai' | 'kb')}
          size="large"
        />
      </div>
    </div>
  );
}
