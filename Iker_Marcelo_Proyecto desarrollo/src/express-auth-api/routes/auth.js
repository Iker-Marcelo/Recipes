const express = require('express');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const mysql = require('mysql2/promise');

const router = express.Router();

// Configuración de la base de datos
const pool = mysql.createPool({
  host: 'localhost',
  user: 'root',
  password: 'root',
  database: 'usuarios',
  waitForConnections: true,
  connectionLimit: 10,
  queueLimit: 0
});

// Register user
router.post('/register', async (req, res) => {
  const { username, password } = req.body;

  try {
    console.log(`Attempting to register user: ${username}`);

    const [rows] = await pool.execute('SELECT * FROM users WHERE username = ?', [username]);

    if (rows.length > 0) {
      console.log(`User ${username} already exists`);
      res.status(409).send('Username already exists');
    } else {
      const hashedPassword = await bcrypt.hash(password, 10);
      await pool.execute('INSERT INTO users (username, password, token) VALUES (?, ?, ?)', [username, hashedPassword, '']);
      console.log(`User ${username} registered successfully`);
      res.status(201).send('User registered successfully');
    }
  } catch (error) {
    console.error('Error during registration:', error);
    res.status(500).send('Internal Server Error');
  }
});

// Login user
router.post('/login', async (req, res) => {
  const { username, password } = req.body;

  try {
    console.log(`Attempting to log in user: ${username}`);

    const [rows] = await pool.execute('SELECT * FROM users WHERE username = ?', [username]);
    console.log('Rows from the database:', rows);

    const user = rows[0];

    if (user && await bcrypt.compare(password, user.password)) {
      // Credenciales válidas, generar token
      const token = jwt.sign({ username: user.username }, 'secret');
      console.log(`Login successful for user: ${username}, Token: ${token}`);

      // Actualizar el token en la base de datos
      await pool.execute('UPDATE users SET token = ? WHERE id = ?', [token, user.id]);

      // Enviar el token como parte de la respuesta
      res.json({ message: 'Login successful', token });
    } else {
      // Credenciales inválidas
      console.log(`Invalid credentials for user: ${username}`);
      res.status(401).json({ message: 'Invalid credentials' });
    }
  } catch (error) {
    console.error('Error during login:', error);
    res.status(500).json({ message: 'Internal Server Error' });
  }
});

// Logout user
router.post('/revoke-token', async (req, res) => {
    try {
      // Obtener el token de la solicitud
      const authorizationHeader = req.get('Authorization');
  
      if (!authorizationHeader) {
        // Si no se proporciona un encabezado Authorization, retorno un error 401 (No autorizado)
        return res.status(401).json({ message: 'Unauthorized' });
      }
  
      // Extraer el token del encabezado
      const token = authorizationHeader.replace('Bearer ', '').trim();
  
      // Verificar que el token sea válido
      const decoded = jwt.verify(token, 'secret');
  
      // Eliminar el token de la base de datos
      await pool.execute('UPDATE users SET token = NULL WHERE token = ?', [token]);
  
      console.log(`Token revoked: ${token}`);
      res.json({ message: 'Token revoked successfully' });
    } catch (error) {
      console.error('Error during token revocation:', error);
      res.status(500).json({ message: 'Internal Server Error' });
    }
});


module.exports = router;
