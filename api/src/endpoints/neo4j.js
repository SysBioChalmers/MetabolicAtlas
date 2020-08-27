import express from 'express';
import {
  getCompartment,
  getGene,
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
  modelSearch,
  globalSearch,
  getInteractionPartners,
  getMapsListing,
  mapSearch,
} from 'neo4j/index';

const neo4jRoutes = express.Router();

const fetchWith = async (req, res, getter) => {
  const { id, version } = req.params;
  const { limit, model, full, searchTerm } = req.query;

  try {
    const result = await getter({ id, version, limit, model, full, searchTerm });
    res.json(result);
  } catch (e) {
    res.status(400).send(e);
  }
};

neo4jRoutes.get('/:version/compartments/:id', async (req, res) => fetchWith(req, res, getCompartment));
neo4jRoutes.get('/:version/compartments/:id/related-reactions', async (req, res) => fetchWith(req, res, getRelatedReactionsForCompartment));

neo4jRoutes.get('/:version/genes/:id', async (req, res) => fetchWith(req, res, getGene));
neo4jRoutes.get('/:version/genes/:id/related-reactions', async (req, res) => fetchWith(req, res, getRelatedReactionsForGene));

neo4jRoutes.get('/:version/metabolites/:id', async (req, res) => fetchWith(req, res, getMetabolite));
neo4jRoutes.get('/:version/metabolites/:id/related-reactions', async (req, res) => fetchWith(req, res, getRelatedReactionsForMetabolite));
neo4jRoutes.get('/:version/metabolites/:id/related-metabolites', async (req, res) => fetchWith(req, res, getRelatedMetabolites));

neo4jRoutes.get('/:version/reactions/:id', async (req, res) => fetchWith(req, res, getReaction));
neo4jRoutes.get('/:version/reactions/:id/related-reactions', async (req, res) => fetchWith(req, res, getRelatedReactionsForReaction));

neo4jRoutes.get('/:version/subsystems/:id', async (req, res) => fetchWith(req, res, getSubsystem));
neo4jRoutes.get('/:version/subsystems/:id/related-reactions', async (req, res) => fetchWith(req, res, getRelatedReactionsForSubsystem));

neo4jRoutes.get('/:version/random-components', async (req, res) => fetchWith(req, res, getRandomComponents));
neo4jRoutes.get('/:version/interaction-partners/:id', async (req, res) => fetchWith(req, res, getInteractionPartners));

neo4jRoutes.get('/:version/maps/listing', async (req, res) => fetchWith(req, res, getMapsListing));
neo4jRoutes.get('/:version/maps/search', async (req, res) => fetchWith(req, res, mapSearch));

neo4jRoutes.get('/:version/search', async (req, res) => {
  const { version } = req.params;
  const { model, searchTerm, limit } = req.query;

  try {
    let result;
    if (model) {
      result = await modelSearch({ searchTerm, model, version, limit });
    } else {
      result = await globalSearch({ searchTerm, version, limit });
    }
    res.json(result);
  } catch (e) {
    res.status(400).send(e);
  }
});


export default neo4jRoutes;
