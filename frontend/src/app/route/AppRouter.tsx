import { AppRoutes } from '@/shared/config/routes';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import { Layout } from '../Layout';
import { MainPage } from '@/pages/main';
import { GeneralPage } from '@/pages/general';

export const AppRouter = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path={AppRoutes.home} element={<Layout />}>
          <Route index element={<MainPage />}></Route>
          <Route
            path={AppRoutes.generalStatisticPage}
            element={<GeneralPage />}
          />
        </Route>
      </Routes>
    </BrowserRouter>
  );
};
