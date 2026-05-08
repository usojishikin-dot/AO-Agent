export const showToast = (message: string) => {
  if (typeof window !== 'undefined') {
    const event = new CustomEvent('show-toast', { detail: { message } });
    window.dispatchEvent(event);
  }
};
