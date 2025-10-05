import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { AppRoutes } from '../shared/config/routes'
import { Layout } from './Layout'
import { MainPage } from '../pages/main'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

const queryClient = new QueryClient()

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path={AppRoutes.home} element={<Layout />}>
            <Route index element={<MainPage />}></Route>
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  )
}

export default App
