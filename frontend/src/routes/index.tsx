import { RouteObject } from 'react-router-dom';
import Layout from '../shared/components/Layout';
import DashboardPage from '../pages/DashboardPage';
import BlockedSitesPage from '../pages/BlockedSitesPage';
import CategoriesPage from '../pages/CategoriesPage';

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
    path: '/blocked-sites',
    element: (
      <Layout>
        <BlockedSitesPage />
      </Layout>
    ),
  },
  {
    path: '/categories',
    element: (
      <Layout>
        <CategoriesPage />
      </Layout>
    ),
  },
];

