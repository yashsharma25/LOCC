import axios from 'axios';

const API = axios.create({
  baseURL: 'http://localhost:8000', // FastAPI server
});

export default API;
