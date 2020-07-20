import express from 'express';
import fs from 'fs';
import swaggerUi from 'swagger-ui-express';
import config from 'swagger/config.json';
import customCss from 'swagger/style.css';

const routes = express.Router();

const options = {
  customSiteTitle: 'Metabolic Atlas API',
  customCss,
  customJs: 'static/helper.js',
};

routes.use('', swaggerUi.serve);
routes.get('', swaggerUi.setup(config, options));


export default routes;
