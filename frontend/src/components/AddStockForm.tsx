import { useState } from 'react';
import { 
  TextField,
  Box,
  IconButton,
  Paper,
  Button,
  useTheme,
  useMediaQuery
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import { stockService } from '../services/api';

interface AddStockFormProps {
  onStockAdded: () => void;
}

const AddStockForm = ({ onStockAdded }: AddStockFormProps) => {
  const [symbol, setSymbol] = useState('');
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!symbol) return;
    
    try {
      await stockService.addStock(symbol.toUpperCase());
      setSymbol('');
      onStockAdded();
    } catch (err) {
      console.error('Error adding stock:', err);
    }
  };

  return (
    <Paper
      component="form"
      onSubmit={handleSubmit}
      sx={{
        display: 'flex',
        alignItems: 'center',
        width: '100%',
        height: '46px',
        backgroundColor: 'rgba(255, 255, 255, 0.1)',
        backdropFilter: 'blur(8px)',
        border: '1px solid rgba(255, 255, 255, 0.2)',
        borderRadius: '24px',
        px: 2,
        '&:hover': {
          backgroundColor: 'rgba(255, 255, 255, 0.15)',
          boxShadow: '0 1px 6px rgba(32,33,36,0.28)'
        }
      }}
    >
      <SearchIcon sx={{ color: 'rgba(255, 255, 255, 0.7)', mr: 2 }} />
      <TextField
        value={symbol}
        onChange={(e) => setSymbol(e.target.value)}
        placeholder="Enter stock symbol..."
        fullWidth
        variant="standard"
        InputProps={{
          disableUnderline: true,
          sx: {
            color: '#ffffff',
            '&::placeholder': {
              color: 'rgba(255, 255, 255, 0.7)'
            }
          }
        }}
        sx={{
          '& .MuiInputBase-input': {
            padding: '8px 0',
          }
        }}
      />
    </Paper>
  );
};

export default AddStockForm; 