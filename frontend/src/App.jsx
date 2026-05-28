import { useState } from 'react';
import axios from 'axios';

function App() {
  const [formData, setFormData] = useState({ username: '', password: '', email: '' });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      // Sending the form data to your live FastAPI backend
      const response = await axios.post('https://3svk-platform.onrender.com/register', formData);
      alert("Success: " + response.data.message);
    } catch (error) {
      alert("Error: Registration failed. Please check the console.");
      console.error(error);
    }
  };

  return (
    <div style={{ padding: '50px', fontFamily: 'Arial' }}>
      <h1>3SVK Platform Registration</h1>
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', width: '300px', gap: '10px' }}>
        <input type="text" placeholder="Username" onChange={(e) => setFormData({...formData, username: e.target.value})} required />
        <input type="password" placeholder="Password" onChange={(e) => setFormData({...formData, password: e.target.value})} required />
        <input type="email" placeholder="Email" onChange={(e) => setFormData({...formData, email: e.target.value})} required />
        <button type="submit">Register</button>
      </form>
    </div>
  );
}

export default App;