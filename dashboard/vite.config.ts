import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const rootDir = path.resolve(__dirname, '..');

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  // 1. Root .env fallback
  const rootEnv = loadEnv(mode, rootDir, '');
  // 2. Dashboard .env (primary)
  const localEnv = loadEnv(mode, __dirname, '');
  // localEnv takes precedence over rootEnv
  const env = { ...rootEnv, ...localEnv };

  const apiUrl = env.VITE_API_URL || process.env.VITE_API_URL;
  const portStr =
    env.FRONTEND_PORT ||
    env.VITE_PORT ||
    env.PORT ||
    process.env.FRONTEND_PORT ||
    process.env.VITE_PORT ||
    process.env.PORT;
  if (!portStr) {
    throw new Error(
      "[URI Dashboard] ERROR: FRONTEND_PORT must be set in dashboard/.env file!"
    );
  }
  const serverPort = Number(portStr);

  return {
    envDir: __dirname,
    define: {
      'import.meta.env.VITE_API_URL': JSON.stringify(apiUrl),
    },
    plugins: [react()],
    server: {
      host: '0.0.0.0',
      port: serverPort,
      strictPort: true,
      ...(apiUrl
        ? {
            proxy: {
              '/api': {
                target: apiUrl,
                changeOrigin: true,
              },
            },
          }
        : {}),
    },
    preview: {
      host: '0.0.0.0',
      port: serverPort,
      strictPort: true,
      ...(apiUrl
        ? {
            proxy: {
              '/api': {
                target: apiUrl,
                changeOrigin: true,
              },
            },
          }
        : {}),
    },
  };
});


