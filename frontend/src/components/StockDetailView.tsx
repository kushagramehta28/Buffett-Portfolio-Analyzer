import {
  Dialog,
  DialogTitle,
  DialogContent,
  Grid,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableRow,
  IconButton
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';

interface StockDetail {
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

interface StockDetailViewProps {
  open: boolean;
  onClose: () => void;
  stock: StockDetail | null;
}

const StockDetailView = ({ open, onClose, stock }: StockDetailViewProps) => {
  if (!stock) return null;

  return (
    <Dialog 
      open={open} 
      onClose={onClose}
      aria-labelledby="stock-detail-dialog-title"
      keepMounted={false}
      disablePortal={false}
      PaperProps={{
        sx: {
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(255, 255, 255, 0.1)'
        }
      }}
    >
      <DialogTitle id="stock-detail-dialog-title">
        <Grid container justifyContent="space-between" alignItems="center">
          <Typography variant="h6">
            Detailed Analysis: {stock.symbol}
          </Typography>
          <IconButton 
            onClick={onClose}
            aria-label="close dialog"
            sx={{
              color: 'rgba(255, 255, 255, 0.7)',
              '&:hover': {
                color: '#ffffff'
              }
            }}
          >
            <CloseIcon />
          </IconButton>
        </Grid>
      </DialogTitle>
      <DialogContent>
        <Grid container spacing={3}>
          {/* Market Data */}
          <Grid item xs={12}>
            <Paper sx={{ p: 2, mb: 2 }}>
              <Typography variant="h6" gutterBottom>Market Data</Typography>
              <TableContainer>
                <Table>
                  <TableBody>
                    <TableRow>
                      <TableCell>Current Price</TableCell>
                      <TableCell align="right">${stock.current_price?.toFixed(2) || 'N/A'}</TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </TableContainer>
            </Paper>
          </Grid>

          {/* Fundamental Analysis */}
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>Fundamental Analysis</Typography>
              <TableContainer>
                <Table>
                  <TableBody>
                    <TableRow>
                      <TableCell>P/E Ratio</TableCell>
                      <TableCell align="right">{stock.pe_ratio?.toFixed(2) || 'N/A'}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>ROE</TableCell>
                      <TableCell align="right">{stock.roe?.toFixed(2)}%</TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </TableContainer>
            </Paper>
          </Grid>

          {/* Analyst Ratings */}
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>Analyst Ratings</Typography>
              <TableContainer>
                <Table>
                  <TableBody>
                    <TableRow>
                      <TableCell>Strong Buy</TableCell>
                      <TableCell align="right">{stock.analyst_ratings_strong_buy || 'N/A'}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Buy</TableCell>
                      <TableCell align="right">{stock.analyst_ratings_buy || 'N/A'}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Hold</TableCell>
                      <TableCell align="right">{stock.analyst_ratings_hold || 'N/A'}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Sell</TableCell>
                      <TableCell align="right">{stock.analyst_ratings_sell || 'N/A'}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Strong Sell</TableCell>
                      <TableCell align="right">{stock.analyst_ratings_strong_sell || 'N/A'}</TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </TableContainer>
            </Paper>
          </Grid>

          {/* Technical Indicators */}
          <Grid item xs={12}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>Technical Indicators</Typography>
              <TableContainer>
                <Table>
                  <TableBody>
                    <TableRow>
                      <TableCell>RSI</TableCell>
                      <TableCell align="right">{stock.rsi?.toFixed(2) || 'N/A'}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>MACD</TableCell>
                      <TableCell align="right">{stock.macd?.toFixed(2) || 'N/A'}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Volatility</TableCell>
                      <TableCell align="right">{stock.volatility?.toFixed(3) || 'N/A'}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Sentiment Score</TableCell>
                      <TableCell align="right">{stock.sentiment_score?.toFixed(2) || 'N/A'}</TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell>Beta</TableCell>
                      <TableCell align="right">{stock.beta?.toFixed(2) || 'N/A'}</TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </TableContainer>
            </Paper>
          </Grid>

          {/* Buffet Analysis */}
          <Grid item xs={12}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>Buffet Analysis</Typography>
              <TableContainer>
                <Table>
                  <TableBody>
                    <TableRow>
                      <TableCell>Total Score</TableCell>
                      <TableCell align="right">{stock.total_score?.toFixed(2) || 'N/A'}</TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </TableContainer>
            </Paper>
          </Grid>
        </Grid>
      </DialogContent>
    </Dialog>
  );
};

export default StockDetailView; 