import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// Vite config: https://vite.dev/config/
export default defineConfig({
  // Lets Vite understand JSX/TSX and enables fast refresh:
  // saving a component updates the page without losing its state.
  plugins: [react()],

  server: {
    // Dev proxy: any request the browser makes to /api/... on the Vite dev
    // server (localhost:5173) is forwarded to FastAPI on localhost:8000.
    //
    // Why? In production, CloudFront serves the React files AND forwards /api
    // to the backend from the same domain. The proxy copies that setup locally,
    // so the frontend code can always call plain "/api/projects" with no
    // hard-coded backend URL and no CORS issues in either environment.
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
})
