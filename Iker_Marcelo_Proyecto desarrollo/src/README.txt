Asegurese de tener los siguientes programas instalados en su sistema:
	-MySQL
	-MongoDB
	-Node.js
	-Python

Antes de ejecutar la aplicación, asegúrate de configurar la base de datos adecuadamente. Puedes ejecutar los siguientes comandos en tu servidor MySQL para crear la base de datos necesaria:
CREATE DATABASE IF NOT EXISTS usuarios;
USE usuarios;
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    token VARCHAR(255)
);

Alternativamente puede ejecutar el siguiente comando en la consola de comandos:

mysql -u tu_usuario -p < setup.sql

Reemplaza tu_usuario con el nombre de usuario de tu base de datos. Te pedirá la contraseña antes de ejecutar los comandos.

Asegúrate de que la configuración de la conexión a la base de datos en tu código coincida con la configuración de tu entorno. Puedes ajustar la configuración en el siguiente fragmento de código en la clase auth.js:

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

Ajusta los valores de host, user, y password según sea necesario.

Para ejecutar el proyecto, abre 3 consolas en el directorio raíz del proyecto.

1)En la primera consola ejecute los siguientes comandos para inicializar el microservicio de TODOs:

cd todo-fastapi-microservice
pip install fastapi httpx pymongo pydantic python-dotenv uvicorn
uvicorn main:app --reload

2)En la segunda consola ejecute estos comandos para iniciar el microservicio de autentificación:

cd express-auth-api
npm install express bcryptjs jsonwebtoken swagger-ui-express yamljs mysql2
node server.js



3) Start the gateway
cd fastapi-gateway
pip install fastapi httpx uvicorn pydantic python-jose
uvicorn main:app --reload --port 8080

