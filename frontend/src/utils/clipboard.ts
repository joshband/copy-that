/**
 * Shared clipboard utilities for copying text with visual feedback
 */

export interface CopyOptions {
  showNotification?: boolean;
  notificationDuration?: number;
}

/**
 * Copy text to clipboard with optional visual notification
 */
export async function copyToClipboard(
  text: string,
  options: CopyOptions = {}
): Promise<boolean> {
  const { showNotification = true, notificationDuration = 2000 } = options;

  try {
    await navigator.clipboard.writeText(text);

    if (showNotification) {
      showCopyNotification(text, notificationDuration);
    }

    return true;
  } catch (err) {
    console.error('Failed to copy:', err);
    return false;
  }
}

/**
 * Show a brief notification when text is copied
 */
function showCopyNotification(text: string, duration: number): void {
  const notification = document.createElement('div');
  notification.className = 'copy-notification';
  notification.textContent = `Copied ${text}`;
  notification.style.cssText = `
    position: fixed;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    background: #333;
    color: white;
    padding: 10px 20px;
    border-radius: 6px;
    z-index: 1000;
    animation: fadeInOut ${duration}ms ease;
  `;

  document.body.appendChild(notification);
  setTimeout(() => notification.remove(), duration);
}
