import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AppRouter } from './route/AppRouter';
import 'react-datepicker/dist/react-datepicker.css';
import { AuthProvider } from './provider/AuthProvider';

const queryClient = new QueryClient();

function App() {
  return (
      <QueryClientProvider client={queryClient}>
        <AppRouter />
      </QueryClientProvider>
  );
}

export default App;
