import { Box, AppBar, Toolbar, Typography, Container, createTheme, ThemeProvider, Button, useTheme, useMediaQuery } from '@mui/material';
import Spline from '@splinetool/react-spline';
import StockList from './components/StockList';
import AddStockForm from './components/AddStockForm';
import AnalyzeStocksButton from './components/AnalyzeStocksButton';

// Create dark theme
const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#90caf9',
    },
    background: {
      default: 'transparent',
      paper: 'rgba(0, 0, 0, 0.7)',
    },
    text: {
      primary: '#ffffff',
      secondary: 'rgba(255, 255, 255, 0.7)',
    }
  },
});

function App() {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  const handleRefresh = () => {
    window.location.reload();
  };

  // Common button style - update with exact dimensions
  const commonButtonStyle = {
    backgroundColor: 'rgba(147, 51, 234, 0.3)',
    backdropFilter: 'blur(8px)',
    border: '1px solid rgba(255, 255, 255, 0.2)',
    borderRadius: '15px',
    transition: 'all 0.3s ease',
    color: '#ffffff',
    textTransform: 'none',
    fontSize: '1rem',
    padding: '8px 24px',
    width: isMobile ? '100%' : '180px',  // Exact width
    height: '45px',  // Exact height
    minHeight: '45px', // Ensure minimum height
    maxHeight: '45px', // Ensure maximum height
    boxShadow: '0 0 15px rgba(147, 51, 234, 0.3)',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    '&:hover': {
      backgroundColor: 'rgba(147, 51, 234, 0.5)',
      borderColor: 'rgba(255, 255, 255, 0.4)',
      transform: 'translateY(-2px)',
      boxShadow: '0 0 25px rgba(147, 51, 234, 0.5)',
    },
    '&:active': {
      transform: 'translateY(0)',
    },
    '&:disabled': {
      backgroundColor: 'rgba(0, 0, 0, 0.2)',
      color: 'rgba(255, 255, 255, 0.3)',
    }
  };

  return (
    <ThemeProvider theme={darkTheme}>
      <Box sx={{ 
        flexGrow: 1, 
        position: 'relative', 
        minHeight: '100vh', 
        bgcolor: 'rgba(0, 0, 0, 0.8)',
        overflow: 'hidden',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center'
      }}>
        {/* Dark overlay for the entire app */}
        <Box
          sx={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.7)',
            backdropFilter: 'blur(8px)',
            zIndex: 0,
          }}
        />

        {/* Spline Background */}
        <Box
          sx={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            zIndex: 0,
            filter: 'blur(2px)', // Slight blur to the 3D background
            opacity: 0.6,
            '& > div': {
              width: '100%',
              height: '100%'
            }
          }}
        >
          <Spline 
            scene="https://prod.spline.design/oKQGBZZdXpMfRJ2o/scene.splinecode"
          />
        </Box>

        {/* Main Content */}
        <Container 
          maxWidth="lg"
          sx={{ 
            position: 'relative',
            zIndex: 1,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            pt: isMobile ? 8 : 15,
            px: isMobile ? 2 : 3,
          }}
        >
          <Typography 
            variant={isMobile ? "h3" : "h2"}
            component="div" 
            sx={{ 
              mb: isMobile ? 4 : 6,
              textAlign: 'center',
              textShadow: '0 0 10px rgba(144, 202, 249, 0.3)',
              letterSpacing: '0.5px',
              fontWeight: 500,
              color: '#ffffff',
              fontSize: isMobile ? '2rem' : '3.75rem',
              width: '100%'
            }}
          >
            Buffett Portfolio Analyzer
          </Typography>

          <Box sx={{ 
            width: '100%',
            maxWidth: '584px',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: 3
          }}>
            <AddStockForm onStockAdded={handleRefresh} />
            
            <Box sx={{ 
              display: 'flex',
              gap: 2,
              flexDirection: isMobile ? 'column' : 'row',
              width: '100%',
              justifyContent: 'center',
              alignItems: 'center',
              mb: 4
            }}>
              <Button
                onClick={() => document.querySelector('form')?.requestSubmit()}
                variant="contained"
                sx={{
                  ...commonButtonStyle,
                  minWidth: '180px',
                  maxWidth: '180px',
                  width: '180px',
                }}
              >
                Add Stock
              </Button>
              <AnalyzeStocksButton 
                onAnalysisComplete={handleRefresh} 
                buttonStyle={{
                  ...commonButtonStyle,
                  minWidth: '180px',
                  maxWidth: '180px',
                  width: '180px',
                }}
              />
            </Box>

            <StockList />
          </Box>
        </Container>
      </Box>
    </ThemeProvider>
  );
}

export default App;