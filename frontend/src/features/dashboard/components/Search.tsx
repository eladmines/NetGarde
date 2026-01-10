import FormControl from '@mui/material/FormControl';
import InputAdornment from '@mui/material/InputAdornment';
import OutlinedInput from '@mui/material/OutlinedInput';
import SearchRoundedIcon from '@mui/icons-material/SearchRounded';
import './Search.css';

export default function Search() {
  return (
    <FormControl className="searchFormControl" variant="outlined">
      <OutlinedInput
        size="small"
        id="search"
        placeholder="Search…"
        className="outlinedInput"
        startAdornment={
          <InputAdornment position="start" sx={{ color: 'text.primary' }} className="inputAdornment">
            <SearchRoundedIcon fontSize="small" />
          </InputAdornment>
        }
        inputProps={{
          'aria-label': 'search',
        }}
      />
    </FormControl>
  );
}
