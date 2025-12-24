import * as React from 'react';
import Button from '@mui/material/Button';
import { SxProps, Theme } from '@mui/material/styles';
import './PrimaryButton.css';

interface PrimaryButtonProps {
  onClick: () => void;
  disabled?: boolean;
  children: React.ReactNode;
  startIcon?: React.ReactNode;
  endIcon?: React.ReactNode;
  size?: 'small' | 'medium' | 'large';
  sx?: SxProps<Theme>;
  className?: string;
}

export default function PrimaryButton({
  onClick,
  disabled = false,
  children,
  startIcon,
  endIcon,
  size = 'small',
  sx,
  className = '',
}: PrimaryButtonProps) {
  return (
    <Button
      variant="outlined"
      size={size}
      startIcon={startIcon}
      endIcon={endIcon}
      onClick={onClick}
      disabled={disabled}
      className={`primaryButton ${className}`.trim()}
      {...(sx && { sx })}
    >
      {children}
    </Button>
  );
}

