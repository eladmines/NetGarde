import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';
import AutoAwesomeRoundedIcon from '@mui/icons-material/AutoAwesomeRounded';
import './CardAlert.css';

export default function CardAlert() {
  return (
    <Card variant="outlined" className="cardAlert">
      <CardContent>
        <AutoAwesomeRoundedIcon fontSize="small" />
        <Typography gutterBottom className="titleTypography">
          Plan about to expire
        </Typography>
        <Typography variant="body2" sx={{ color: 'text.secondary' }} className="descriptionTypography">
          Enjoy 10% off when renewing your plan today.
        </Typography>
        <Button variant="contained" size="small" fullWidth>
          Get the discount
        </Button>
      </CardContent>
    </Card>
  );
}
