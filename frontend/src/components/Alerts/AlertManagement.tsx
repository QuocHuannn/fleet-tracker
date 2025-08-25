import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Tabs,
  Tab,
  Paper
} from '@mui/material';

import AlertDashboard from './AlertDashboard';
import AlertRules from './AlertRules';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index, ...other }) => {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`alert-tabpanel-${index}`}
      aria-labelledby={`alert-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
};

const AlertManagement: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Quản lý Cảnh báo
      </Typography>

      <Paper>
        <Tabs
          value={activeTab}
          onChange={handleTabChange}
          indicatorColor="primary"
          textColor="primary"
          variant="fullWidth"
        >
          <Tab label="Dashboard Cảnh báo" />
          <Tab label="Quy tắc Cảnh báo" />
        </Tabs>

        <TabPanel value={activeTab} index={0}>
          <AlertDashboard />
        </TabPanel>

        <TabPanel value={activeTab} index={1}>
          <AlertRules />
        </TabPanel>
      </Paper>
    </Box>
  );
};

export default AlertManagement;
