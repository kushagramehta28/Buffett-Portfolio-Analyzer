import axios from 'axios';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5001',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Stock related API calls
export const stockService = {
  // Get all stocks
  getAllStocks: async () => {
    try {
      console.log('Fetching stocks from:', api.defaults.baseURL + '/stocks');  // Debug log
      const response = await api.get('/stocks');
      console.log('Response received:', response.data);  // Debug log
      return response.data;
    } catch (error: any) {
      console.error('Error fetching stocks:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status,
        url: api.defaults.baseURL + '/stocks'
      });
      throw error;
    }
  },
  
  addStock: async (symbol: string) => {
    try {
      console.log('Attempting to add stock:', symbol);  // Debug log
      const response = await api.post('/stocks', { symbol });
      console.log('Add stock response:', response.data);  // Debug log
      return response.data;
    } catch (error: any) {
      console.error('Error adding stock:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status,
        url: api.defaults.baseURL + '/stocks'
      });
      throw error;
    }
  },

  analyzeStocks: async () => {
    try {
      const response = await api.post('/analyze-stocks');
      return response.data;
    } catch (error) {
      console.error('Error analyzing stocks:', error);
      throw error;
    }
  },

  async removeStock(symbol: string) {
    try {
      const response = await api.delete(`/remove-stock/${symbol}`);
      return response.data;
    } catch (error) {
      console.error('Error removing stock:', error);
      throw error;
    }
  }
};

export default api; 