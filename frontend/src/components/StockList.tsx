import { useState, useEffect, useCallback } from 'react';
import { 
  Paper, 
  Table, 
  TableBody, 
  TableCell, 
  TableContainer, 
  TableHead, 
  TableRow,
  Typography,
  CircularProgress,
  Box,
  Button,
  useTheme,
  useMediaQuery
} from '@mui/material';
import { stockService } from '../services/api';
import StockDetailView from './StockDetailView';

interface Stock {
  symbol: string;
  current_price: number;
  pe_ratio: number;
  roe: number;
  total_score: number;
  analyst_ratings_buy: number;
  analyst_ratings_hold: number;
  analyst_ratings_sell: number;
  analyst_ratings_strong_buy: number;
  analyst_ratings_strong_sell: number;
  rsi: number;
  macd: number;
  volatility: number;
  sentiment_score: number;
  beta: number;
}

const StockList = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  
  const [stocks, setStocks] = useState<Stock[]>([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [selectedStock, setSelectedStock] = useState<Stock | null>(null);
  const [detailViewOpen, setDetailViewOpen] = useState(false);
  const [removingSymbol, setRemovingSymbol] = useState<string | null>(null);

  useEffect(() => {
    const fetchStocks = async () => {
      try {
        setLoading(true);
        const data = await stockService.getAllStocks();
        // Check if data is an array before sorting
        const stocksArray = Array.isArray(data) ? data : [];
        const sortedStocks = stocksArray.sort((a: Stock, b: Stock) => 
          (b.total_score || 0) - (a.total_score || 0)
        );
        setStocks(sortedStocks);
      } catch (err) {
        console.error('Error details:', err);
        setError('Failed to fetch stocks');
      } finally {
        setLoading(false);
      }
    };

    fetchStocks();
  }, []);

  const handleViewDetails = (stock: Stock) => {
    setSelectedStock(stock);
    setDetailViewOpen(true);
  };

  const handleRemoveStock = async (symbol: string) => {
    try {
      setRemovingSymbol(symbol);
      await stockService.removeStock(symbol);
      // Remove the stock from the local state
      setStocks(stocks.filter(stock => stock.symbol !== symbol));
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to remove stock');
    } finally {
      setRemovingSymbol(null);
    }
  };

  // Function to render mobile view
  const renderMobileView = () => (
    <Box sx={{ width: '100%' }}>
      {stocks.map((stock) => (
        <Paper
          key={stock.symbol}
          sx={{
            p: 2,
            mb: 2,
            backgroundColor: 'rgba(0, 0, 0, 0.5)',
            backdropFilter: 'blur(10px)',
            borderRadius: '10px',
          }}
        >
          <Box sx={{ mb: 2, textAlign: 'center' }}>
            <Typography variant="h6" sx={{ color: '#ffffff' }}>
              {stock.symbol}
            </Typography>
          </Box>
          
          <Box sx={{ display: 'grid', gap: 1, mb: 2 }}>
            {[
              { label: 'Price:', value: stock.current_price ? `$${stock.current_price.toFixed(2)}` : 'N/A' },
              { label: 'P/E Ratio:', value: stock.pe_ratio ? stock.pe_ratio.toFixed(2) : 'N/A' },
              { label: 'ROE:', value: stock.roe ? `${stock.roe.toFixed(2)}%` : 'N/A' },
              { label: 'Score:', value: stock.total_score ? stock.total_score.toFixed(2) : 'N/A' }
            ].map(({ label, value }) => (
              <Box 
                key={label} 
                sx={{ 
                  display: 'flex', 
                  justifyContent: 'space-between',
                  width: '100%',
                  maxWidth: '300px',
                  margin: '0 auto',
                  px: 2
                }}
              >
                <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                  {label}
                </Typography>
                <Typography variant="body2" sx={{ color: '#ffffff' }}>
                  {value}
                </Typography>
              </Box>
            ))}
          </Box>
          
          <Box sx={{ 
            display: 'flex', 
            gap: 2,
            justifyContent: 'center',
            width: '100%' 
          }}>
            <Button
              variant="outlined"
              size="small"
              onClick={() => handleViewDetails(stock)}
              sx={{
                flex: 1,
                backgroundColor: 'rgba(147, 51, 234, 0.2)',
                color: '#ffffff',
                borderRadius: '12px',
                fontSize: '0.8rem',
                padding: '8px 0',
                '&:hover': {
                  backgroundColor: 'rgba(147, 51, 234, 0.4)',
                  transform: 'translateY(-1px)',
                }
              }}
            >
              Details
            </Button>
            <Button
              variant="contained"
              size="small"
              color="error"
              disabled={removingSymbol === stock.symbol}
              onClick={() => handleRemoveStock(stock.symbol)}
              sx={{
                flex: 1,
                backgroundColor: 'rgba(244, 67, 54, 0.2)',
                color: '#ff8a80',
                borderRadius: '12px',
                fontSize: '0.8rem',
                padding: '8px 0',
                '&:hover': {
                  backgroundColor: 'rgba(244, 67, 54, 0.4)',
                  transform: 'translateY(-1px)',
                }
              }}
            >
              {removingSymbol === stock.symbol ? (
                <CircularProgress size={20} color="inherit" />
              ) : (
                'Remove'
              )}
            </Button>
          </Box>
        </Paper>
      ))}
    </Box>
  );

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return <Typography color="error">{error}</Typography>;
  }

  return (
    <Box sx={{ width: '100%', px: isMobile ? 2 : 0 }}>
      <Typography 
        variant={isMobile ? "h6" : "h5"} 
        sx={{ 
          mb: 3, 
          color: '#ffffff',
          textAlign: isMobile ? 'center' : 'left'
        }}
      >
        Stock Portfolio
      </Typography>
      
      {isMobile ? (
        renderMobileView()
      ) : (
        <TableContainer 
          component={Paper} 
          sx={{ 
            backgroundColor: 'rgba(0, 0, 0, 0.5)',
            backdropFilter: 'blur(10px)',
            '& .MuiTableCell-root': {
              borderColor: 'rgba(255, 255, 255, 0.1)'
            }
          }}
        >
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Symbol</TableCell>
                <TableCell>Current Price ($)</TableCell>
                <TableCell>P/E Ratio</TableCell>
                <TableCell>ROE (%)</TableCell>
                <TableCell>Total Score</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {stocks.map((stock) => (
                <TableRow key={stock.symbol}>
                  <TableCell>{stock.symbol}</TableCell>
                  <TableCell>
                    {stock.current_price ? `$${stock.current_price.toFixed(2)}` : 'N/A'}
                  </TableCell>
                  <TableCell>
                    {stock.pe_ratio ? stock.pe_ratio.toFixed(2) : 'N/A'}
                  </TableCell>
                  <TableCell>
                    {stock.roe ? `${stock.roe.toFixed(2)}%` : 'N/A'}
                  </TableCell>
                  <TableCell>
                    {stock.total_score ? stock.total_score.toFixed(2) : 'N/A'}
                  </TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <Button
                        variant="outlined"
                        size="small"
                        onClick={() => handleViewDetails(stock)}
                        sx={{
                          backgroundColor: 'rgba(147, 51, 234, 0.2)',
                          color: '#ffffff',
                          borderRadius: '12px',
                          fontSize: '0.8rem',
                          '&:hover': {
                            backgroundColor: 'rgba(147, 51, 234, 0.4)',
                            transform: 'translateY(-1px)',
                          }
                        }}
                      >
                        View Details
                      </Button>
                      <Button
                        variant="contained"
                        size="small"
                        color="error"
                        disabled={removingSymbol === stock.symbol}
                        onClick={() => handleRemoveStock(stock.symbol)}
                        sx={{
                          backgroundColor: 'rgba(244, 67, 54, 0.2)',
                          color: '#ff8a80',
                          borderRadius: '12px',
                          fontSize: '0.8rem',
                          '&:hover': {
                            backgroundColor: 'rgba(244, 67, 54, 0.4)',
                            transform: 'translateY(-1px)',
                          }
                        }}
                      >
                        {removingSymbol === stock.symbol ? (
                          <CircularProgress size={20} color="inherit" />
                        ) : (
                          'Remove'
                        )}
                      </Button>
                    </Box>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      <StockDetailView
        open={detailViewOpen}
        onClose={() => setDetailViewOpen(false)}
        stock={selectedStock}
      />
    </Box>
  );
};

export default StockList; 