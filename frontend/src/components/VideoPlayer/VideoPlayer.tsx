import { useRef, useState, useEffect } from 'react';
import { Upload, Button, Progress, message } from 'antd';
import { UploadOutlined, PlayCircleOutlined, PauseCircleOutlined } from '@ant-design/icons';
import type { UploadProps } from 'antd';
import { videoApi } from '../../services/videoApi';
import type { Video } from '../../types/index';
import { formatTime } from '../../utils/timeFormat';
import './VideoPlayer.css';

interface VideoPlayerProps {
  onVideoLoaded?: (video: Video) => void;
  onTimeUpdate?: (currentTime: number) => void;
}

export function VideoPlayer({ onVideoLoaded, onTimeUpdate }: VideoPlayerProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [video, setVideo] = useState<Video | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);

  // 跳转到指定时间
  const seekTo = (time: number) => {
    if (videoRef.current) {
      videoRef.current.currentTime = time;
    }
  };

  // 暴露 seekTo 方法给父组件
  useEffect(() => {
    (window as any).videoPlayerSeekTo = seekTo;
    return () => {
      delete (window as any).videoPlayerSeekTo;
    };
  }, []);

  // 视频上传配置
  const uploadProps: UploadProps = {
    name: 'file',
    accept: 'video/*',
    showUploadList: false,
    beforeUpload: async (file) => {
      // 检查文件大小（限制 500MB）
      const maxSize = 500 * 1024 * 1024;
      if (file.size > maxSize) {
        message.error('视频文件不能超过 500MB');
        return false;
      }

      setUploading(true);
      setUploadProgress(0);

      try {
        // 调用上传 API
        const response = await videoApi.upload(file, (progress) => {
          setUploadProgress(progress);
        });

        message.success('视频上传成功！');

        // 获取视频详情
        const videoData = await videoApi.get(response.video_id);
        setVideo(videoData);

        if (onVideoLoaded) {
          onVideoLoaded(videoData);
        }
      } catch (error) {
        console.error('Upload error:', error);
        message.error('视频上传失败，请重试');
      } finally {
        setUploading(false);
        setUploadProgress(0);
      }

      return false; // 阻止默认上传行为
    },
  };

  // 播放/暂停
  const togglePlay = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause();
      } else {
        videoRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  // 监听视频时间更新
  const handleTimeUpdate = () => {
    if (videoRef.current) {
      const time = videoRef.current.currentTime;
      setCurrentTime(time);
      if (onTimeUpdate) {
        onTimeUpdate(time);
      }
    }
  };

  // 监听视频加载完成
  const handleLoadedMetadata = () => {
    if (videoRef.current) {
      setDuration(videoRef.current.duration);
    }
  };

  // 进度条拖动
  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const time = parseFloat(e.target.value);
    seekTo(time);
    setCurrentTime(time);
  };

  return (
    <div className="video-player">
      {!video ? (
        <div className="upload-section">
          <Upload {...uploadProps}>
            <Button
              type="primary"
              icon={<UploadOutlined />}
              size="large"
              loading={uploading}
              disabled={uploading}
            >
              {uploading ? '上传中...' : '选择视频文件'}
            </Button>
          </Upload>

          {uploading && (
            <div className="upload-progress">
              <Progress percent={uploadProgress} status="active" />
              <p>正在上传和分析视频，请稍候...</p>
            </div>
          )}
        </div>
      ) : (
        <div className="player-section">
          <div className="video-container">
            <video
              ref={videoRef}
              src={`/api/videos/${video.id}/stream`}
              onTimeUpdate={handleTimeUpdate}
              onLoadedMetadata={handleLoadedMetadata}
              onPlay={() => setIsPlaying(true)}
              onPause={() => setIsPlaying(false)}
            />
          </div>

          <div className="controls">
            <div className="control-bar">
              <Button
                type="text"
                icon={isPlaying ? <PauseCircleOutlined /> : <PlayCircleOutlined />}
                onClick={togglePlay}
                size="large"
                className="play-button"
              />

              <div className="time-display">
                {formatTime(currentTime)} / {formatTime(duration)}
              </div>

              <input
                type="range"
                min="0"
                max={duration}
                value={currentTime}
                onChange={handleSeek}
                className="seek-bar"
              />
            </div>
          </div>

          <div className="video-info">
            <h3>{video.filename}</h3>
            <p>时长: {formatTime(video.duration)}</p>
          </div>
        </div>
      )}
    </div>
  );
}
