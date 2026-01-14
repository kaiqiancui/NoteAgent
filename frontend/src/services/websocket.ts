export class AIWebSocket {
  private ws: WebSocket | null = null;
  private url = 'ws://localhost:8000/ws/ai/chat'; // 直接连接后端
  private currentOnChunk: ((text: string) => void) | null = null;
  private currentOnComplete: (() => void) | null = null;

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      console.log('[WebSocket] 正在连接:', this.url);
      this.ws = new WebSocket(this.url);

      this.ws.onopen = () => {
        console.log('[WebSocket] 连接成功');
        resolve();
      };

      this.ws.onerror = (error) => {
        console.error('[WebSocket] 连接错误:', error);
        reject(error);
      };

      this.ws.onclose = () => {
        console.log('[WebSocket] 连接已关闭');
      };

      // 设置统一的消息处理器
      this.ws.onmessage = (event) => {
        const text = event.data;
        console.log('[WebSocket] 收到消息:', text.substring(0, 100));

        if (text === '[DONE]') {
          console.log('[WebSocket] 收到结束标记');
          if (this.currentOnComplete) {
            this.currentOnComplete();
          }
          // 清空回调
          this.currentOnChunk = null;
          this.currentOnComplete = null;
          return;
        }

        // 检查是否是错误消息
        try {
          const parsed = JSON.parse(text);
          if (parsed.error) {
            console.error('[WebSocket] 错误:', parsed.error);
            if (this.currentOnChunk) {
              this.currentOnChunk(`错误: ${parsed.error}`);
            }
            return;
          }
        } catch {
          // 不是 JSON，正常处理为文本
        }

        if (this.currentOnChunk) {
          this.currentOnChunk(text);
        }
      };
    });
  }

  async askQuestion(
    videoId: string,
    timestamp: number,
    question: string,
    frame: string,
    onChunk: (text: string) => void,
    onComplete?: () => void
  ): Promise<void> {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.log('[WebSocket] 需要重新连接');
      await this.connect();
    }

    // 设置当前回调
    this.currentOnChunk = onChunk;
    this.currentOnComplete = onComplete || null;

    // 发送问题
    const message = {
      video_id: videoId,
      timestamp,
      question,
      frame,
    };
    console.log('[WebSocket] 发送消息:', message);
    this.ws!.send(JSON.stringify(message));
  }

  close() {
    if (this.ws) {
      console.log('[WebSocket] 关闭连接');
      this.ws.close();
      this.ws = null;
    }
    this.currentOnChunk = null;
    this.currentOnComplete = null;
  }
}

// 导出单例
export const aiWebSocket = new AIWebSocket();

