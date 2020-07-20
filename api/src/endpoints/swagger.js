import express from 'express';
import swaggerUi from 'swagger-ui-express';
import swaggerDocument from 'swagger.json';

const routes = express.Router();

routes.use('', swaggerUi.serve);
routes.get('', swaggerUi.setup(swaggerDocument));

export default routes;
