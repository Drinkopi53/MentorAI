import axios from 'axios';

// Get the API base URL from the environment variable
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

// Create an Axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// You can add interceptors for request or response here if needed
// For example, to automatically add an Authorization header:
// apiClient.interceptors.request.use(config => {
//   const token = localStorage.getItem('authToken');
//   if (token) {
//     config.headers.Authorization = `Bearer ${token}`;
//   }
//   return config;
// }, error => {
//   return Promise.reject(error);
// });

// Define API methods
export default {
  get(path) {
    return apiClient.get(path);
  },
  post(path, data) {
    return apiClient.post(path, data);
  },
  put(path, data) {
    return apiClient.put(path, data);
  },
  delete(path) {
    return apiClient.delete(path);
  },
  // Add other methods as needed
};
