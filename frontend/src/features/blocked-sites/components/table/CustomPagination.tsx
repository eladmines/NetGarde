import * as React from 'react';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import IconButton from '@mui/material/IconButton';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';
import './CustomPagination.css';

interface CustomPaginationProps {
  page: number; // 0-based page index
  pageSize: number;
  totalCount: number;
  onPageChange: (newPage: number) => void;
}

export default function CustomPagination({
  page,
  pageSize,
  totalCount,
  onPageChange,
}: CustomPaginationProps) {
  const totalPages = Math.ceil(totalCount / pageSize);

  const handlePageChange = (newPage: number) => {
    if (newPage >= 0 && newPage < totalPages) {
      onPageChange(newPage);
    }
  };

  // Calculate which page numbers to show
  const getPageNumbers = () => {
    const pages: (number | string)[] = [];
    const maxVisible = 7; // Maximum number of page buttons to show

    if (totalPages <= maxVisible) {
      // Show all pages if total is less than max
      for (let i = 0; i < totalPages; i++) {
        pages.push(i);
      }
    } else {
      // Show first page
      pages.push(0);

      if (page > 2) {
        pages.push('...');
      }

      // Show pages around current page
      const start = Math.max(1, page - 1);
      const end = Math.min(totalPages - 2, page + 1);

      for (let i = start; i <= end; i++) {
        pages.push(i);
      }

      if (page < totalPages - 3) {
        pages.push('...');
      }

      // Show last page
      pages.push(totalPages - 1);
    }

    return pages;
  };

  const pageNumbers = getPageNumbers();

  if (totalPages <= 1) {
    return null; // Don't show pagination if there's only one page or less
  }

  return (
    <Box className="customPagination">
      <IconButton
        onClick={() => handlePageChange(page - 1)}
        disabled={page === 0}
        className="paginationButton paginationNavButton"
        aria-label="previous page"
      >
        <ChevronLeftIcon />
      </IconButton>

      <Box className="paginationPageButtons">
        {pageNumbers.map((pageNum, index) => {
          if (pageNum === '...') {
            return (
              <Box key={`ellipsis-${index}`} className="paginationEllipsis">
                ...
              </Box>
            );
          }

          const pageIndex = pageNum as number;
          const isActive = pageIndex === page;

          return (
            <Button
            key={pageIndex}
            onClick={() => handlePageChange(pageIndex)}
            className={`paginationButton paginationPageButton ${isActive ? 'active' : ''}`}
            variant={isActive ? 'contained' : 'outlined'}
            aria-label={`page ${pageIndex + 1}`}
            aria-current={isActive ? 'page' : undefined}
            sx={{
              minWidth: '32px',
              width: '32px',
              height: '32px',
              padding: 0,
              borderRadius: 0,
              boxShadow: 'none !important',
          
              ...(isActive && {
                backgroundColor: '#0067b8 !important',
                color: '#ffffff !important',
                borderColor: '#25a0ff !important',
          
                '&:hover': {
                  backgroundColor: '#1e90e6 !important',
                  borderColor: '#1e90e6 !important',
                },
          
                // ❤️ FIXES: removes black active/focus background
                '&:focus, &:active, &:focus-visible': {
                  backgroundColor: '#25a0ff !important',
                  boxShadow: 'none !important',
                  outline: 'none !important',
                },
          
                '&.Mui-focusVisible': {
                  backgroundColor: '#25a0ff !important',
                  boxShadow: 'none !important',
                  outline: 'none !important',
                },
          
                // Prevent MUI from applying dark overlay on click
                '&.MuiButtonBase-root.MuiButton-contained:active': {
                  backgroundColor: '#25a0ff !important',
                  boxShadow: 'none !important',
                },
              }),
            }}
          >
            {pageIndex + 1}
          </Button>
          
          );
        })}
      </Box>

      <IconButton
        onClick={() => handlePageChange(page + 1)}
        disabled={page >= totalPages - 1}
        className="paginationButton paginationNavButton"
        aria-label="next page"
      >
        <ChevronRightIcon />
      </IconButton>
    </Box>
  );
}

