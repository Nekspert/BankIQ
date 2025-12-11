import { useEffect, type FC, type ReactNode } from 'react';
import { useAuth } from '@/shared/hooks/useAuth';
import { useNavigate } from 'react-router-dom';
import { AppRoutes } from '@/shared/config/routes';

export const ProtectedRoute: FC<{ children: ReactNode }> = ({ children }) => {
  const { isAuthorized, loading } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!loading && !isAuthorized) {
      navigate(AppRoutes.home, { replace: true });
    }
  }, [loading, isAuthorized, navigate]);

  if (loading || !isAuthorized) return null;

  return <>{children}</>;
};
