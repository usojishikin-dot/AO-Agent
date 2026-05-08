export const showToast = (message: string, type?: 'success' | 'error' | 'info') => {
  if (typeof window !== 'undefined') {
    const event = new CustomEvent('show-toast', { detail: { message, type } });
    window.dispatchEvent(event);
  }
};
