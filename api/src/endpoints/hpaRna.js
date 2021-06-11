import express from 'express';

const routes = express.Router();
let HPA_JSON = null;

routes.get('/all', async (req, res) => {
  try {
    if (!HPA_JSON) {
      HPA_JSON = require('data/hpaRna.json');
    }

    res.json(HPA_JSON);
  } catch (e) {
    res.status(400).send(e.message);
  }
});

export default routes;
