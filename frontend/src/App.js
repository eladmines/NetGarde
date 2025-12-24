import * as React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './shared/components/Layout';
import DashboardContent from './features/dashboard/DashboardContent';
import BlockedSites from './features/blocked-sites/BlockedSites';
import Categories from './features/categories/Categories';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout><DashboardContent /></Layout>} />
        <Route path="/blocked-sites" element={<Layout><BlockedSites /></Layout>} />
        <Route path="/categories" element={<Layout><Categories /></Layout>} />
      </Routes>
    </BrowserRouter>
  );
}
