import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useStore } from '@/store';
import Layout from '@/components/Layout';
import Setup from '@/pages/Setup';
import Lesson from '@/pages/Lesson';
import Progress from '@/pages/Progress';
import KnowledgeGraph from '@/pages/KnowledgeGraph';
import History from '@/pages/History';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 5 * 60 * 1000,
    },
  },
});

function AppContent() {
  const session = useStore((state) => state.session);

  return (
    <Routes>
      <Route path="/setup" element={<Setup />} />
      <Route element={<Layout />}>
        <Route 
          path="/lesson" 
          element={session ? <Lesson /> : <Navigate to="/setup" />} 
        />
        <Route 
          path="/progress" 
          element={session ? <Progress /> : <Navigate to="/setup" />} 
        />
        <Route 
          path="/graph" 
          element={session ? <KnowledgeGraph /> : <Navigate to="/setup" />} 
        />
        <Route 
          path="/history" 
          element={session ? <History /> : <Navigate to="/setup" />} 
        />
        <Route path="/" element={<Navigate to={session ? "/lesson" : "/setup"} />} />
      </Route>
    </Routes>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AppContent />
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
