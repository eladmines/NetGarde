import * as React from 'react';
import IconButton from '@mui/material/IconButton';
import Popover from '@mui/material/Popover';
import Box from '@mui/material/Box';
import FormGroup from '@mui/material/FormGroup';
import FormControlLabel from '@mui/material/FormControlLabel';
import Checkbox from '@mui/material/Checkbox';
import FilterListIcon from '@mui/icons-material/FilterList';
import { useCategories } from '../../../categories/hooks/useCategories';
import './CategoryFilter.css';

interface CategoryFilterProps {
  selectedCategories: string[];
  onCategoryChange: (categories: string[]) => void;
  allCategoryNames?: string[]; // Categories from blocked sites data
}

export default function CategoryFilter({
  selectedCategories,
  onCategoryChange,
  allCategoryNames = [],
}: CategoryFilterProps) {
  const [anchorEl, setAnchorEl] = React.useState<HTMLButtonElement | null>(null);
  const { categories, loading } = useCategories();

  const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    event.stopPropagation();
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleCategoryToggle = (categoryName: string) => {
    const newSelected = selectedCategories.includes(categoryName)
      ? selectedCategories.filter((cat) => cat !== categoryName)
      : [...selectedCategories, categoryName];
    onCategoryChange(newSelected);
  };

  const open = Boolean(anchorEl);

  // Extract unique category names from both categories table and blocked sites data
  const uniqueCategories = React.useMemo(() => {
    const categorySet = new Set<string>();
    // Add categories from the categories table
    categories.forEach((cat) => {
      if (cat.name) {
        categorySet.add(cat.name);
      }
    });
    // Add categories from blocked sites data (in case some categories are deleted but still referenced)
    allCategoryNames.forEach((name) => {
      if (name) {
        categorySet.add(name);
      }
    });
    return Array.from(categorySet).sort();
  }, [categories, allCategoryNames]);

  return (
    <>
      <IconButton
        size="small"
        onClick={handleClick}
        className={`categoryFilterIcon ${selectedCategories.length > 0 ? 'hasFilters' : ''}`}
        aria-label="filter categories"
      >
        <FilterListIcon fontSize="small" />
      </IconButton>
      <Popover
        open={open}
        anchorEl={anchorEl}
        onClose={handleClose}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'left',
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'left',
        }}
        onClick={(e) => e.stopPropagation()}
        onKeyDown={(e) => e.stopPropagation()}
        className="categoryFilterPopover"
      >
        <Box className="categoryFilterContent">
          <FormGroup>
            {loading ? (
              <Box className="categoryFilterLoading">Loading categories...</Box>
            ) : uniqueCategories.length === 0 ? (
              <Box className="categoryFilterEmpty">No categories available</Box>
            ) : (
              uniqueCategories.map((categoryName) => (
                <FormControlLabel
                  key={categoryName}
                  control={
                    <Checkbox
                      checked={selectedCategories.includes(categoryName)}
                      onChange={() => handleCategoryToggle(categoryName)}
                      size="small"
                    />
                  }
                  label={categoryName}
                  className="categoryFilterCheckbox"
                />
              ))
            )}
          </FormGroup>
        </Box>
      </Popover>
    </>
  );
}

