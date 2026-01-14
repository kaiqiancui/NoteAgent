import { useState } from 'react';
import { MainLayout } from './components/Layout/MainLayout';
import { VideoPlayer } from './components/VideoPlayer/VideoPlayer';
import { NotePanel } from './components/NotePanel/NotePanel';
import { AIPanel } from './components/AIPanel/AIPanel';
import { KnowledgePanel } from './components/KnowledgePanel/KnowledgePanel';
import type { Video } from './types/index';

function App() {
  const [currentVideo, setCurrentVideo] = useState<Video | null>(null);
  const [currentTime, setCurrentTime] = useState(0);

  const handleVideoLoaded = (video: Video) => {
    setCurrentVideo(video);
  };

  const handleTimeUpdate = (time: number) => {
    setCurrentTime(time);
  };

  const handleNoteClick = (timestamp: number) => {
    // 跳转到指定时间戳
    if ((window as any).videoPlayerSeekTo) {
      (window as any).videoPlayerSeekTo(timestamp);
    }
  };

  return (
    <MainLayout
      leftPanel={
        <VideoPlayer
          onVideoLoaded={handleVideoLoaded}
          onTimeUpdate={handleTimeUpdate}
        />
      }
      notePanel={
        <NotePanel
          videoId={currentVideo?.id || null}
          currentTime={currentTime}
          onNoteClick={handleNoteClick}
        />
      }
      aiPanel={
        <AIPanel
          videoId={currentVideo?.id || null}
          currentTime={currentTime}
        />
      }
      kbPanel={<KnowledgePanel />}
    />
  );
}

export default App;
