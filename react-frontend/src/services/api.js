import axios from 'axios';

export const getUserRole = async (token) => {
  const res = await axios.get('http://localhost:8000/users/me', {
    headers: { Authorization: `Bearer ${token}` }
  });
  return res.data.role;
};

