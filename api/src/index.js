import express from 'express';
import router from 'endpoints/index';

const app = express();

app.use('/api', router);
app.use('/api/public', express.static('public'));
app.use('/api/svg', express.static('svg'));

app.listen(8081);
