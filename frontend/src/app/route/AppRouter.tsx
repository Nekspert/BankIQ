import { AppRoutes } from '@/shared/config/routes';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import { Layout } from '../Layout';
import { MainPage } from '@/pages/main';
import { GeneralPage } from '@/pages/general';
import { AuthProvider } from '../provider/AuthProvider';

export const AppRouter = () => {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path={AppRoutes.home} element={<Layout />}>
            <Route index element={<MainPage />}></Route>
            <Route
              path={AppRoutes.generalStatisticPage}
              element={<GeneralPage />}
            />
          </Route>
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
};
