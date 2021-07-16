import express from 'express';
import neo4jRoutes from 'endpoints/neo4j';
import repoRoutes from 'endpoints/repository';
import hpaRoutes from 'endpoints/hpaRna';
import swaggerRoutes from 'endpoints/swagger';

const router = express.Router();

router.use(neo4jRoutes);
router.use('/repository', repoRoutes);
router.use('/rna', hpaRoutes);
router.use(swaggerRoutes);

export default router;
