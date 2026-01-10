import { useState, useEffect } from 'react';
import { useLocation, Link } from 'react-router-dom';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import Collapse from '@mui/material/Collapse';
import Stack from '@mui/material/Stack';
import Tooltip from '@mui/material/Tooltip';
import ExpandLess from '@mui/icons-material/ExpandLess';
import ExpandMore from '@mui/icons-material/ExpandMore';
import HomeRoundedIcon from '@mui/icons-material/HomeRounded';
import RouterIcon from '@mui/icons-material/Router';
import RuleIcon from '@mui/icons-material/Rule';
import CategoryIcon from '@mui/icons-material/Category';
import AnalyticsIcon from '@mui/icons-material/Analytics';
import HistoryIcon from '@mui/icons-material/History';
import SecurityIcon from '@mui/icons-material/Security';
import PeopleIcon from '@mui/icons-material/People';
import NotificationsIcon from '@mui/icons-material/Notifications';
import SettingsRoundedIcon from '@mui/icons-material/SettingsRounded';
import InfoRoundedIcon from '@mui/icons-material/InfoRounded';
import HelpRoundedIcon from '@mui/icons-material/HelpRounded';
import './MenuContent.css';

const mainListItems = [
  { text: 'Home', icon: <HomeRoundedIcon />, path: '/', iconClass: 'homeIcon' },
];

const manageNetworkItems = [
  { text: 'Blocked Sites', icon: <RuleIcon />, path: '/blocked-sites', iconClass: 'blockedSitesIcon' },
  { text: 'Categories', icon: <CategoryIcon />, path: '/categories', iconClass: 'categoriesIcon' },
];

const analyticsItems = [
  { text: 'Reports', icon: <AnalyticsIcon />, path: '/reports', iconClass: 'reportsIcon' },
  { text: 'Activity Logs', icon: <HistoryIcon />, path: '/activity-logs', iconClass: 'activityLogsIcon' },
];

const secondaryListItems = [
  { text: 'Security', icon: <SecurityIcon />, path: '/security', iconClass: 'securityIcon' },
  { text: 'Users', icon: <PeopleIcon />, path: '/users', iconClass: 'usersIcon' },
  { text: 'Notifications', icon: <NotificationsIcon />, path: '/notifications', iconClass: 'notificationsIcon' },
  { text: 'Settings', icon: <SettingsRoundedIcon />, path: '/settings', iconClass: 'settingsIcon' },
  { text: 'About', icon: <InfoRoundedIcon />, path: '/about', iconClass: 'aboutIcon' },
  { text: 'Feedback', icon: <HelpRoundedIcon />, path: '/feedback', iconClass: 'feedbackIcon' },
];

interface MenuContentProps {
  open?: boolean;
}

export default function MenuContent({ open = true }: MenuContentProps) {
  const location = useLocation();
  const [manageNetworkOpen, setManageNetworkOpen] = useState(true);
  const [analyticsOpen, setAnalyticsOpen] = useState(false);

  useEffect(() => {
    const hasSelectedChild = manageNetworkItems.some(item => location.pathname === item.path);
    if (hasSelectedChild) {
      setManageNetworkOpen(true);
    }
    const hasSelectedAnalytics = analyticsItems.some(item => location.pathname === item.path);
    if (hasSelectedAnalytics) {
      setAnalyticsOpen(true);
    }
  }, [location.pathname]);

  const handleManageNetworkClick = () => {
    setManageNetworkOpen(!manageNetworkOpen);
  };

  const handleAnalyticsClick = () => {
    setAnalyticsOpen(!analyticsOpen);
  };

  const renderNavItem = (item: typeof mainListItems[0], index: number) => {
    const isSelected = location.pathname === item.path;
    const button = (
      <ListItemButton
        component={Link}
        to={item.path}
        selected={isSelected}
        className="azure-sidebar-item"
        sx={{
          minHeight: 40,
          borderRadius: '4px',
          px: 1.5,
          py: 1,
          mx: 0.5,
          mb: 0.5,
          position: 'relative',
          '&.Mui-selected': {
            backgroundColor: 'rgba(0, 120, 212, 0.08)',
            '&:hover': {
              backgroundColor: 'rgba(0, 120, 212, 0.12)',
            },
            '&::before': {
              content: '""',
              position: 'absolute',
              left: 0,
              top: '50%',
              transform: 'translateY(-50%)',
              width: 3,
              height: 20,
              backgroundColor: '#0078d4',
              borderRadius: '0 2px 2px 0',
            },
          },
          '&:hover': {
            backgroundColor: 'rgba(0, 0, 0, 0.04)',
          },
        }}
      >
        <ListItemIcon
          className={`menuIcon ${item.iconClass}`}
          sx={{
            minWidth: open ? 40 : 'auto',
            justifyContent: open ? 'flex-start' : 'center',
          }}
        >
          {item.icon}
        </ListItemIcon>
        {open && (
          <ListItemText
            primary={item.text}
            primaryTypographyProps={{
              fontSize: '0.875rem',
              fontWeight: isSelected ? 500 : 400,
              color: isSelected ? 'rgba(0, 0, 0, 0.87)' : 'rgba(0, 0, 0, 0.6)',
            }}
          />
        )}
      </ListItemButton>
    );

    return (
      <ListItem key={index} disablePadding sx={{ display: 'block' }}>
        {!open ? (
          <Tooltip title={item.text} placement="right" arrow>
            <span>{button}</span>
          </Tooltip>
        ) : (
          button
        )}
      </ListItem>
    );
  };

  return (
    <Stack sx={{ flexGrow: 1, p: 1, justifyContent: 'space-between' }}>
      <List dense sx={{ px: 0 }}>
        {mainListItems.map((item, index) => renderNavItem(item, index))}
        
        {open && (
          <>
            <ListItem disablePadding sx={{ display: 'block' }}>
              <ListItemButton
                onClick={handleManageNetworkClick}
                sx={{
                  minHeight: 40,
                  borderRadius: '4px',
                  px: 1.5,
                  py: 1,
                  mx: 0.5,
                  mb: 0.5,
                  '&:hover': {
                    backgroundColor: 'rgba(0, 0, 0, 0.04)',
                  },
                }}
              >
                <ListItemIcon
                  className="menuIcon"
                  sx={{
                    minWidth: 40,
                    justifyContent: 'flex-start',
                  }}
                >
                  <RouterIcon />
                </ListItemIcon>
                <ListItemText
                  primary="My network"
                  primaryTypographyProps={{
                    fontSize: '0.875rem',
                    fontWeight: 400,
                    color: 'rgba(0, 0, 0, 0.6)',
                  }}
                />
                {manageNetworkOpen ? <ExpandLess /> : <ExpandMore />}
              </ListItemButton>
            </ListItem>
            <Collapse in={manageNetworkOpen} timeout="auto" unmountOnExit>
              <List component="div" disablePadding dense>
                {manageNetworkItems.map((item, index) => {
                  const isSelected = location.pathname === item.path;
                  const button = (
                    <ListItemButton
                      component={Link}
                      to={item.path}
                      selected={isSelected}
                      className="azure-sidebar-item"
                      sx={{
                        minHeight: 40,
                        borderRadius: '4px',
                        px: 1.5,
                        py: 1,
                        mx: 0.5,
                        mb: 0.5,
                        ml: 4, // Indent for nested items
                        position: 'relative',
                        '&.Mui-selected': {
                          backgroundColor: 'rgba(0, 120, 212, 0.08)',
                          '&:hover': {
                            backgroundColor: 'rgba(0, 120, 212, 0.12)',
                          },
                          '&::before': {
                            content: '""',
                            position: 'absolute',
                            left: 0,
                            top: '50%',
                            transform: 'translateY(-50%)',
                            width: 3,
                            height: 20,
                            backgroundColor: '#0078d4',
                            borderRadius: '0 2px 2px 0',
                          },
                        },
                        '&:hover': {
                          backgroundColor: 'rgba(0, 0, 0, 0.04)',
                        },
                      }}
                    >
                      <ListItemIcon
                        className={`menuIcon ${item.iconClass}`}
                        sx={{
                          minWidth: 40,
                          justifyContent: 'flex-start',
                        }}
                      >
                        {item.icon}
                      </ListItemIcon>
                      <ListItemText
                        primary={item.text}
                        primaryTypographyProps={{
                          fontSize: '0.875rem',
                          fontWeight: isSelected ? 500 : 400,
                          color: isSelected ? 'rgba(0, 0, 0, 0.87)' : 'rgba(0, 0, 0, 0.6)',
                        }}
                      />
                    </ListItemButton>
                  );

                  return (
                    <ListItem key={index} disablePadding sx={{ display: 'block' }}>
                      {button}
                    </ListItem>
                  );
                })}
              </List>
            </Collapse>
          </>
        )}
        
        {open && (
          <>
            <ListItem disablePadding sx={{ display: 'block' }}>
              <ListItemButton
                onClick={handleAnalyticsClick}
                sx={{
                  minHeight: 40,
                  borderRadius: '4px',
                  px: 1.5,
                  py: 1,
                  mx: 0.5,
                  mb: 0.5,
                  '&:hover': {
                    backgroundColor: 'rgba(0, 0, 0, 0.04)',
                  },
                }}
              >
                <ListItemIcon
                  className="menuIcon"
                  sx={{
                    minWidth: 40,
                    justifyContent: 'flex-start',
                  }}
                >
                  <AnalyticsIcon />
                </ListItemIcon>
                <ListItemText
                  primary="Analytics"
                  primaryTypographyProps={{
                    fontSize: '0.875rem',
                    fontWeight: 400,
                    color: 'rgba(0, 0, 0, 0.6)',
                  }}
                />
                {analyticsOpen ? <ExpandLess /> : <ExpandMore />}
              </ListItemButton>
            </ListItem>
            <Collapse in={analyticsOpen} timeout="auto" unmountOnExit>
              <List component="div" disablePadding dense>
                {analyticsItems.map((item, index) => {
                  const isSelected = location.pathname === item.path;
                  const button = (
                    <ListItemButton
                      component={Link}
                      to={item.path}
                      selected={isSelected}
                      className="azure-sidebar-item"
                      sx={{
                        minHeight: 40,
                        borderRadius: '4px',
                        px: 1.5,
                        py: 1,
                        mx: 0.5,
                        mb: 0.5,
                        ml: 4, // Indent for nested items
                        position: 'relative',
                        '&.Mui-selected': {
                          backgroundColor: 'rgba(0, 120, 212, 0.08)',
                          '&:hover': {
                            backgroundColor: 'rgba(0, 120, 212, 0.12)',
                          },
                          '&::before': {
                            content: '""',
                            position: 'absolute',
                            left: 0,
                            top: '50%',
                            transform: 'translateY(-50%)',
                            width: 3,
                            height: 20,
                            backgroundColor: '#0078d4',
                            borderRadius: '0 2px 2px 0',
                          },
                        },
                        '&:hover': {
                          backgroundColor: 'rgba(0, 0, 0, 0.04)',
                        },
                      }}
                    >
                      <ListItemIcon
                        className={`menuIcon ${item.iconClass}`}
                        sx={{
                          minWidth: 40,
                          justifyContent: 'flex-start',
                        }}
                      >
                        {item.icon}
                      </ListItemIcon>
                      <ListItemText
                        primary={item.text}
                        primaryTypographyProps={{
                          fontSize: '0.875rem',
                          fontWeight: isSelected ? 500 : 400,
                          color: isSelected ? 'rgba(0, 0, 0, 0.87)' : 'rgba(0, 0, 0, 0.6)',
                        }}
                      />
                    </ListItemButton>
                  );

                  return (
                    <ListItem key={index} disablePadding sx={{ display: 'block' }}>
                      {button}
                    </ListItem>
                  );
                })}
              </List>
            </Collapse>
          </>
        )}

        {!open && (
          <>
            {manageNetworkItems.map((item, index) => {
              const isSelected = location.pathname === item.path;
              const button = (
                <ListItemButton
                  component={Link}
                  to={item.path}
                  selected={isSelected}
                  className="azure-sidebar-item"
                  sx={{
                    minHeight: 40,
                    borderRadius: '4px',
                    px: 1.5,
                    py: 1,
                    mx: 0.5,
                    mb: 0.5,
                    position: 'relative',
                    '&.Mui-selected': {
                      backgroundColor: 'rgba(0, 120, 212, 0.08)',
                      '&:hover': {
                        backgroundColor: 'rgba(0, 120, 212, 0.12)',
                      },
                      '&::before': {
                        content: '""',
                        position: 'absolute',
                        left: 0,
                        top: '50%',
                        transform: 'translateY(-50%)',
                        width: 3,
                        height: 20,
                        backgroundColor: '#0078d4',
                        borderRadius: '0 2px 2px 0',
                      },
                    },
                    '&:hover': {
                      backgroundColor: 'rgba(0, 0, 0, 0.04)',
                    },
                  }}
                >
                  <ListItemIcon
                    className={`menuIcon ${item.iconClass}`}
                    sx={{
                      minWidth: 'auto',
                      justifyContent: 'center',
                    }}
                  >
                    {item.icon}
                  </ListItemIcon>
                </ListItemButton>
              );

              return (
                <ListItem key={`collapsed-${index}`} disablePadding sx={{ display: 'block' }}>
                  <Tooltip title={item.text} placement="right" arrow>
                    <span>{button}</span>
                  </Tooltip>
                </ListItem>
              );
            })}
            {analyticsItems.map((item, index) => {
              const isSelected = location.pathname === item.path;
              const button = (
                <ListItemButton
                  component={Link}
                  to={item.path}
                  selected={isSelected}
                  className="azure-sidebar-item"
                  sx={{
                    minHeight: 40,
                    borderRadius: '4px',
                    px: 1.5,
                    py: 1,
                    mx: 0.5,
                    mb: 0.5,
                    position: 'relative',
                    '&.Mui-selected': {
                      backgroundColor: 'rgba(0, 120, 212, 0.08)',
                      '&:hover': {
                        backgroundColor: 'rgba(0, 120, 212, 0.12)',
                      },
                      '&::before': {
                        content: '""',
                        position: 'absolute',
                        left: 0,
                        top: '50%',
                        transform: 'translateY(-50%)',
                        width: 3,
                        height: 20,
                        backgroundColor: '#0078d4',
                        borderRadius: '0 2px 2px 0',
                      },
                    },
                    '&:hover': {
                      backgroundColor: 'rgba(0, 0, 0, 0.04)',
                    },
                  }}
                >
                  <ListItemIcon
                    className={`menuIcon ${item.iconClass}`}
                    sx={{
                      minWidth: 'auto',
                      justifyContent: 'center',
                    }}
                  >
                    {item.icon}
                  </ListItemIcon>
                </ListItemButton>
              );

              return (
                <ListItem key={`collapsed-analytics-${index}`} disablePadding sx={{ display: 'block' }}>
                  <Tooltip title={item.text} placement="right" arrow>
                    <span>{button}</span>
                  </Tooltip>
                </ListItem>
              );
            })}
          </>
        )}
      </List>
      <List dense sx={{ px: 0 }}>
        {secondaryListItems.map((item, index) => {
          const isSelected = location.pathname === item.path;
          const button = (
            <ListItemButton
              component={Link}
              to={item.path}
              selected={isSelected}
              className="azure-sidebar-item"
              sx={{
                minHeight: 40,
                borderRadius: '4px',
                px: 1.5,
                py: 1,
                mx: 0.5,
                mb: 0.5,
                position: 'relative',
                '&.Mui-selected': {
                  backgroundColor: 'rgba(0, 120, 212, 0.08)',
                  '&:hover': {
                    backgroundColor: 'rgba(0, 120, 212, 0.12)',
                  },
                  '&::before': {
                    content: '""',
                    position: 'absolute',
                    left: 0,
                    top: '50%',
                    transform: 'translateY(-50%)',
                    width: 3,
                    height: 20,
                    backgroundColor: '#0078d4',
                    borderRadius: '0 2px 2px 0',
                  },
                },
                '&:hover': {
                  backgroundColor: 'rgba(0, 0, 0, 0.04)',
                },
              }}
            >
              <ListItemIcon
                className={`menuIcon ${item.iconClass}`}
                sx={{
                  minWidth: open ? 40 : 'auto',
                  justifyContent: open ? 'flex-start' : 'center',
                }}
              >
                {item.icon}
              </ListItemIcon>
              {open && (
                <ListItemText
                  primary={item.text}
                  primaryTypographyProps={{
                    fontSize: '0.875rem',
                    fontWeight: isSelected ? 500 : 400,
                    color: isSelected ? 'rgba(0, 0, 0, 0.87)' : 'rgba(0, 0, 0, 0.6)',
                  }}
                />
              )}
            </ListItemButton>
          );

          return (
            <ListItem key={index} disablePadding sx={{ display: 'block' }}>
              {!open ? (
                <Tooltip title={item.text} placement="right" arrow>
                  <span>{button}</span>
                </Tooltip>
              ) : (
                button
              )}
            </ListItem>
          );
        })}
      </List>
    </Stack>
  );
}
