import { RouteObject } from 'react-router-dom';
import Layout from '../shared/components/Layout';
import DashboardPage from '../pages/DashboardPage';
import PolicyPage from '../pages/PolicyPage';
import CountryAccessPage from '../pages/CountryAccessPage';
import ClientProfilesPage from '../pages/ClientProfilesPage';
import ClientMapPage from '../pages/ClientMapPage';

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
    path: '/policy/countries',
    element: (
      <Layout>
        <CountryAccessPage />
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
  {
    path: '/client-map',
    element: (
      <Layout>
        <ClientMapPage />
      </Layout>
    ),
  },
];

