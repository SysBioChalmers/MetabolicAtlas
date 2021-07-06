import express from 'express';
import {
  getCompartment,
  getGene,
  getGenesForHPA,
  getGeneDetailsForHPA,
  getMetabolite,
  getReaction,
  getSubsystem,
  getRelatedReactionsForCompartment,
  getRelatedReactionsForGene,
  getRelatedReactionsForMetabolite,
  getRelatedReactionsForReaction,
  getRelatedReactionsForSubsystem,
  getRelatedMetabolites,
  getRandomComponents,
  getInteractionPartners,
  getMapsListing,
  mapSearch,
  search,
  get3dNetwork,
  getComparisonOverview,
  getComparisonDetails,
  getComponentsForExternalDb,
} from 'neo4j/index';

const neo4jRoutes = express.Router();

const fetchWith = async (req, res, queryHandler) => {
  const { id } = req.params;
  const { model, modelShortName, version, limit, full, searchTerm, componentTypes } = req.query;

  try {
    const payload = { id, version, model, modelShortName, limit, full, searchTerm };

    if (componentTypes) {
      payload.componentTypes = JSON.parse(componentTypes);
    }

    const result = await queryHandler(payload);
    res.json(result);
  } catch (e) {
    if (e.message === '404') {
      return res.sendStatus(404);
    }

    res.status(400).send(e.message);
  }
};

neo4jRoutes.get('/compartments/:id', async (req, res) => fetchWith(req, res, getCompartment));
neo4jRoutes.get('/compartments/:id/related-reactions', async (req, res) => fetchWith(req, res, getRelatedReactionsForCompartment));

neo4jRoutes.get('/genes/:id', async (req, res) => fetchWith(req, res, getGene));
neo4jRoutes.get('/genes/:id/related-reactions', async (req, res) => fetchWith(req, res, getRelatedReactionsForGene));
neo4jRoutes.get('/hpa/genes', async (req, res) => fetchWith(req, res, getGenesForHPA));
neo4jRoutes.get('/hpa/gene/:id', async (req, res) => fetchWith(req, res, getGeneDetailsForHPA));

neo4jRoutes.get('/metabolites/:id', async (req, res) => fetchWith(req, res, getMetabolite));
neo4jRoutes.get('/metabolites/:id/related-reactions', async (req, res) => fetchWith(req, res, getRelatedReactionsForMetabolite));
neo4jRoutes.get('/metabolites/:id/related-metabolites', async (req, res) => fetchWith(req, res, getRelatedMetabolites));

neo4jRoutes.get('/reactions/:id', async (req, res) => fetchWith(req, res, getReaction));
neo4jRoutes.get('/reactions/:id/related-reactions', async (req, res) => fetchWith(req, res, getRelatedReactionsForReaction));

neo4jRoutes.get('/subsystems/:id', async (req, res) => fetchWith(req, res, getSubsystem));
neo4jRoutes.get('/subsystems/:id/related-reactions', async (req, res) => fetchWith(req, res, getRelatedReactionsForSubsystem));

neo4jRoutes.get('/random-components', async (req, res) => fetchWith(req, res, getRandomComponents));
neo4jRoutes.get('/interaction-partners/:id', async (req, res) => fetchWith(req, res, getInteractionPartners));

neo4jRoutes.get('/maps/listing', async (req, res) => fetchWith(req, res, getMapsListing));
neo4jRoutes.get('/maps/search', async (req, res) => fetchWith(req, res, mapSearch));
neo4jRoutes.get('/search', async (req, res) => fetchWith(req, res, search));

neo4jRoutes.get('/3d-network', async (req, res) => {
  const { model, version, type, id } = req.query;

  try {
    let payload = { model, version };

    if (type && id) {
      payload = { ...payload, type, id };
    }

    const network = await get3dNetwork(payload);
    res.json(network);
  } catch (e) {
    res.status(400).send(e.message);
  }
});

neo4jRoutes.get('/compare', async (req, res) => {
  const { models } = req.query;
  const parsedModels = JSON.parse(models);

  try {
    if (!models || parsedModels.length < 2 || parsedModels.length > 4) {
      throw new Error('At least 2 and at most 4 models need to be provided.');
    }

    const result = await getComparisonOverview({ models: parsedModels });
    res.json(result);
  } catch (e) {
    res.status(400).send(e.message);
  }
});

neo4jRoutes.get('/comparison-details', async (req, res) => {
  const { model, models } = req.query;
  const parsedModel = JSON.parse(model);
  const parsedModels = JSON.parse(models);

  try {
    if (!models || parsedModels.length < 1 || parsedModels.length > 2) {
      throw new Error('At least 1 and at most 2 models need to be provided.');
    }

    const result = await getComparisonDetails({
      model: parsedModel,
      models: parsedModels,
    });
    res.json(result);
  } catch (e) {
    res.status(400).send(e.message);
  }
});

neo4jRoutes.get('/external-db/:dbName/:externalId', async (req, res) => {
  const { dbName, externalId } = req.params;

  try {
    const result = await getComponentsForExternalDb({ dbName, externalId });
    res.json(result);
  } catch (e) {
    if (e.message === '404') {
      return res.sendStatus(404);
    }

    res.status(400).send(e.message);
  }
});

export default neo4jRoutes;
