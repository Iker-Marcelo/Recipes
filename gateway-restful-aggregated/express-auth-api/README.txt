1. Set up the project

mkdir express-auth-api
cd express-auth-api
npm init -y
npm install express bcryptjs jsonwebtoken swagger-ui-express yamljs

2. Create a Basic Express Server

// create new file server.js
const express = require('express');
const app = express();
app.use(express.json());

// Import routes
const authRoutes = require('./routes/auth');

// Use routes
app.use('/api/user', authRoutes);

// Start the server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));

3. Create Routes for Authentication
Create a new directory named routes and within that directory, create a file named auth.js:

const express = require('express');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const router = express.Router();

// Dummy user database
let users = [];

// Register user
router.post('/register', async (req, res) => {
    const { username, password } = req.body;
    const hashedPassword = await bcrypt.hash(password, 10);

    const user = { username, password: hashedPassword };
    users.push(user);

    res.status(201).send('User registered successfully');
});

// Login user
router.post('/login', async (req, res) => {
    const { username, password } = req.body;
    const user = users.find(user => user.username === username);

    if (user && await bcrypt.compare(password, user.password)) {
        const token = jwt.sign({ username: user.username }, 'secret');
        res.json({ token });
    } else {
        res.status(400).send('Invalid credentials');
    }
});

module.exports = router;


4: Add OpenAPI Documentation
Create an OpenAPI documentation file in YAML format. Name it api-doc.yaml:

openapi: 3.0.0
info:
  title: User Authentication API
  version: 1.0.0
paths:
  /api/user/register:
    post:
      summary: Register a new user
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                username:
                  type: string
                password:
                  type: string
      responses:
        '201':
          description: User registered successfully
  /api/user/login:
    post:
      summary: Login a user
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                username:
                  type: string
                password:
                  type: string
      responses:
        '200':
          description: Successful login
          content:
            application/json:
              schema:
                type: object
                properties:
                  token:
                    type: string
        '400':
          description: Invalid credentials

5: Serve the OpenAPI Documentation
Update server.js to serve the OpenAPI documentation using swagger-ui-express:

const swaggerUi = require('swagger-ui-express');
const YAML = require('yamljs');
const swaggerDocument = YAML.load('./api-doc.yaml');

app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(swaggerDocument));

6: Run the Server
node server.js

The API endpoints will be available at /api/user/register and /api/user/login, and the OpenAPI documentation can be accessed at /api-docs.