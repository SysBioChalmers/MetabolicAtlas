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
  getInteractionPartners,
  getMapsListing,
  mapSearch,
  search,
  get3dNetwork,
} from 'neo4j/index';

const neo4jRoutes = express.Router();
const CACHED_3D_NETWORKS = {};

const fetchWith = async (req, res, queryHandler) => {
  const { id } = req.params;
  const { model, version, limit, full, searchTerm } = req.query;

  try {
    const result = await queryHandler({ id, version, limit, model, full, searchTerm });
    res.json(result);
  } catch (e) {
    res.status(400).send(e);
  }
};

neo4jRoutes.get('/compartments/:id', async (req, res) => fetchWith(req, res, getCompartment));
neo4jRoutes.get('/compartments/:id/related-reactions', async (req, res) => fetchWith(req, res, getRelatedReactionsForCompartment));

neo4jRoutes.get('/genes/:id', async (req, res) => fetchWith(req, res, getGene));
neo4jRoutes.get('/genes/:id/related-reactions', async (req, res) => fetchWith(req, res, getRelatedReactionsForGene));

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
    if (!CACHED_3D_NETWORKS[model]) {
      CACHED_3D_NETWORKS[model] = {};
    }

    let network;

    if (!CACHED_3D_NETWORKS[model][version]) {
      CACHED_3D_NETWORKS[model][version] = {};
    }

    if (type && id) {
      if (!CACHED_3D_NETWORKS[model][version][id]) {
        const n = await get3dNetwork({ model, version, type, id });
        CACHED_3D_NETWORKS[model][version][id] = n;
      }

      network = CACHED_3D_NETWORKS[model][version][id];
    } else {
      if (!CACHED_3D_NETWORKS[model][version].whole) {
        const n = await get3dNetwork({ model, version });
        CACHED_3D_NETWORKS[model][version].whole = n;
      }

      network = CACHED_3D_NETWORKS[model][version].whole;
    }

    res.json(network);
  } catch (e) {
    res.status(400).send(e);
  }
});

export default neo4jRoutes;
