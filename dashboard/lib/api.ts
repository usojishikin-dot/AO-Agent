export const getApiUrl = (path: string) => {
  // Use the local proxy to avoid CORS and firewall issues on mobile
  return `/api-proxy${path}`;
};
