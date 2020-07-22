import express from 'express';
import swaggerUi from 'swagger-ui-express';
import config from 'swagger/config.yaml';
import customCss from 'swagger/style.css';

const routes = express.Router();

const options = {
  customSiteTitle: 'Metabolic Atlas API',
  customCss,
  customJs: 'public/helper.js',
};

routes.get('/favicon*', function (req, res) {
  res.redirect('public' + req.url);
});
routes.use('', swaggerUi.serve);
routes.get('', swaggerUi.setup(config, options));

export default routes;
