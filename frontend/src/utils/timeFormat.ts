/**
 * 格式化秒数为 MM:SS 格式
 * @param seconds 秒数
 * @returns MM:SS 格式的字符串
 */
export function formatTime(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

/**
 * 格式化秒数为时间戳显示（如 [00:30]）
 * @param seconds 秒数
 * @returns [MM:SS] 格式的字符串
 */
export function formatTimestamp(seconds: number): string {
  return `[${formatTime(seconds)}]`;
}
