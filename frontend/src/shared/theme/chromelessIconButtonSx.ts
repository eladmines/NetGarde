import { SxProps, Theme } from '@mui/material/styles';

/** Overrides default MuiIconButton chrome (border/background) from inputs theme. */
export const chromelessIconButtonSx: SxProps<Theme> = {
  border: 'none',
  boxShadow: 'none',
  backgroundColor: 'transparent',
  minWidth: 'auto',
  '&:hover': {
    border: 'none',
    boxShadow: 'none',
    backgroundColor: 'action.hover',
  },
  '&:active': {
    border: 'none',
    backgroundColor: 'action.selected',
  },
};
