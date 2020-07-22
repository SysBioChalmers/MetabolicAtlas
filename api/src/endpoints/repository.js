import express from 'express';
import gemsRepoJson from 'data/gemsRepository.json';
import integratedGemsRepoJson from 'data/integratedModels.json';

const routes = express.Router();

routes.get('/integrated_models', async (req, res) => {
  try {
    res.json(integratedGemsRepoJson);
  } catch (e) {
    res.status(400).send(e);
  }
});

routes.get('/integrated_models/:name', async (req, res) => {
  const { name } = req.params;

  try {
    const gem = integratedGemsRepoJson.filter(g => g.short_name.toLowerCase() === name.toLowerCase())[0];
    if (!!gem) {
      res.json(gem);
    } else {
      res.sendStatus(404);
    }
  } catch (e) {
    res.status(400).send(e);
  }
});

routes.get('/models', async (req, res) => {
  try {
    res.json(gemsRepoJson);
  } catch (e) {
    res.status(400).send(e);
  }
});

export default routes;
