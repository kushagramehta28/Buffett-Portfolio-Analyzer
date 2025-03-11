import { useState } from 'react';
import { Button, CircularProgress } from '@mui/material';
import { stockService } from '../services/api';

interface AnalyzeStocksButtonProps {
  onAnalysisComplete: () => void;
  buttonStyle?: object;
}

const AnalyzeStocksButton = ({ onAnalysisComplete, buttonStyle }: AnalyzeStocksButtonProps) => {
  const [loading, setLoading] = useState(false);

  const handleAnalyze = async () => {
    try {
      setLoading(true);
      await stockService.analyzeStocks();
      onAnalysisComplete();
    } catch (err) {
      console.error('Error analyzing stocks:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Button 
      variant="contained" 
      onClick={handleAnalyze}
      disabled={loading}
      sx={{
        ...buttonStyle,
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        gap: 1,
        minWidth: '180px',    // Ensure exact width
        maxWidth: '180px',    // Ensure exact width
      }}
    >
      {loading && <CircularProgress size={20} />}
      {loading ? 'Analyzing' : 'Analyze Stocks'}
    </Button>
  );
};

export default AnalyzeStocksButton; 