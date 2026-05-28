import { RouteObject } from 'react-router-dom';
import Layout from '../shared/components/Layout';
import DashboardPage from '../pages/DashboardPage';
import PolicyPage from '../pages/PolicyPage';
import ClientProfilesPage from '../pages/ClientProfilesPage';

export const routes: RouteObject[] = [
  {
    path: '/',
    element: (
      <Layout>
        <DashboardPage />
      </Layout>
    ),
  },
  {
    path: '/policy',
    element: (
      <Layout>
        <PolicyPage />
      </Layout>
    ),
  },
  {
    path: '/client-profiles',
    element: (
      <Layout>
        <ClientProfilesPage />
      </Layout>
    ),
  },
];

