import * as React from 'react';
import Box from '@mui/material/Box';
import './CircularDotsLoader.css';

export default function CircularDotsLoader() {
  const dots = Array.from({ length: 10 }, (_, i) => i);

  return (
    <Box className="circularDotsLoader">
      {dots.map((index) => (
        <Box
          key={index}
          className="loaderDot"
          sx={{
            '--dot-index': index,
          }}
        />
      ))}
    </Box>
  );
}

