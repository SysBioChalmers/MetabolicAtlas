from coverage import coverage
cov = coverage(branch=True, cover_pylib=False,
               include=['hma_backend/*'], omit=['tests.py'])
cov.start()

import json
import os
import unittest

from hma_backend import app, db
from hma_backend.config import basedir
from hma_backend.models import *


class APITestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = app
        cls.client = cls.app.test_client()
        db.create_all()
        cls.populate_db()

    @classmethod
    def tearDownClass(cls):
        db.session.remove()
        db.drop_all()

    def test_method_not_allowed(self):
        response = self.client.post('/api/v1/models')
        data = dict(self.get_json(response))
        assert response.status_code == 405
        assert data['error'] == "Method not allowed"

    def test_index(self):
        expected = ("Welcome to the Human Metabolic Atlas! Please check "
                    "the API documentation for usage.")
        response = self.client.get('/')
        data = dict(self.get_json(response))
        assert data['message'] == expected

    def test_get_spec(self):
        expected = "This is an API for accessing metabolic models"
        response = self.client.get('/api/v1/spec')
        data = dict(self.get_json(response))
        assert data['info']['description'] == expected

    def test_get_models(self):
        response = self.client.get('/api/v1/models')
        data = dict(self.get_json(response))
        assert len(data['models']) == 1

    def test_get_model(self):
        response = self.client.get('/api/v1/models/1')
        data = dict(self.get_json(response))
        assert data['model_id'] == 1
        assert data['short_name'] == "TestModel"
        assert data['name'] == "Metabolic test model"
        assert len(data['authors']) == 2

    def test_get_model_404(self):
        response = self.client.get('/api/v1/models/1234')
        data = dict(self.get_json(response))
        assert response.status_code == 404
        assert data['error'] == "Not found"

    def test_get_authors(self):
        response = self.client.get('/api/v1/authors')
        data = dict(self.get_json(response))
        assert len(data['authors']) == 2

    def test_get_author(self):
        response = self.client.get('/api/v1/authors/1')
        data = dict(self.get_json(response))
        assert data['given_name'] == "First"
        assert data['family_name'] == "Author"
        assert data['email'] == "first.author@example.com"
        assert data['organization'] == "ACME Modeling"
        assert data['models'] == [1]

    def test_get_author_404(self):
        response = self.client.get('/api/v1/authors/1234')
        data = dict(self.get_json(response))
        assert response.status_code == 404
        assert data['error'] == "Not found"

    def test_get_reactions(self):
        response = self.client.get('/api/v1/reactions')
        data = dict(self.get_json(response))
        assert data['limit'] == 20
        assert data['offset'] == 2
        assert len(data['reactions']) == 2

    def test_get_reactions_with_offset(self):
        response = self.client.get('/api/v1/reactions?offset=2')
        data = dict(self.get_json(response))
        assert data['limit'] == 20
        assert data['offset'] == 2
        assert len(data['reactions']) == 0

    def test_get_reaction(self):
        response = self.client.get('/api/v1/reactions/reaction1')
        data = dict(self.get_json(response))
        assert data['reaction_id'] == "reaction1"
        assert data['name'] == "Reaction"
        assert data['sbo_id'] == "SBO:0000176"
        assert data['equation'] == "FO2 => BAr"
        assert data['lower_bound'] == 0.0
        assert data['upper_bound'] == 1.0
        assert data['objective_coefficient'] == 1.0
        assert len(data['reactants']) == 1
        assert len(data['products']) == 1

    def test_get_reaction_404(self):
        response = self.client.get('/api/v1/reactions/no_reaction')
        data = dict(self.get_json(response))
        assert response.status_code == 404
        assert data['error'] == "Not found"

    def test_get_reaction_reactants(self):
        response = self.client.get('/api/v1/reactions/reaction1/reactants')
        data = dict(self.get_json(response))
        assert len(data['reactants']) == 1

    def test_get_reaction_no_reactants(self):
        response = self.client.get('/api/v1/reactions/reaction2/reactants')
        data = dict(self.get_json(response))
        assert len(data['reactants']) == 0

    def test_get_reaction_reactant(self):
        uri = '/api/v1/reactions/reaction1/reactants/reactant1'
        response = self.client.get(uri)
        data = dict(self.get_json(response))
        assert data['component_id'] == "reactant1"
        assert data['short_name'] == "reactant1"
        assert data['long_name'] == "Reactant 1"
        assert data['type'] == "metabolite"
        assert data['compartment'] == "Mitochondria"
        assert data['organism'] == "Human"
        assert data['formula'] == "FO2"

    def test_get_reaction_reactant_404(self):
        uri = '/api/v1/reactions/reaction1/reactants/no_reactant'
        response = self.client.get(uri)
        data = dict(self.get_json(response))
        assert response.status_code == 404
        assert data['error'] == "Not found"

    def test_get_reaction_products(self):
        response = self.client.get('/api/v1/reactions/reaction1/products')
        data = dict(self.get_json(response))
        assert len(data['products']) == 1

    def test_get_reaction_no_products(self):
        response = self.client.get('/api/v1/reactions/reaction2/products')
        data = dict(self.get_json(response))
        assert len(data['products']) == 0

    def test_get_reaction_product(self):
        uri = '/api/v1/reactions/reaction1/products/product1'
        response = self.client.get(uri)
        data = dict(self.get_json(response))
        assert data['component_id'] == "product1"
        assert data['short_name'] == "Product 1"
        assert data['long_name'] == "Product 1"
        assert data['type'] == "metabolite"
        assert data['organism'] == "Human"
        assert data['formula'] == "BAr"

    def test_get_reaction_product_404(self):
        uri = '/api/v1/reactions/reaction1/products/no_product'
        response = self.client.get(uri)
        data = dict(self.get_json(response))
        assert response.status_code == 404
        assert data['error'] == "Not found"

    def test_get_reaction_modifiers(self):
        response = self.client.get('/api/v1/reactions/reaction1/modifiers')
        data = dict(self.get_json(response))
        assert len(data['modifiers']) == 2

    def test_get_reaction_no_modifiers(self):
        response = self.client.get('/api/v1/reactions/reaction2/modifiers')
        data = dict(self.get_json(response))
        assert len(data['modifiers']) == 0

    def test_get_reaction_modifier(self):
        uri = '/api/v1/reactions/reaction1/modifiers/modifier1'
        response = self.client.get(uri)
        data = dict(self.get_json(response))
        assert data['component_id'] == "modifier1"
        assert data['short_name'] == "modifier1"
        assert data['long_name'] == "Modifier 1"
        assert data['type'] == "enzyme"
        assert data['organism'] == "Human"
        assert data['formula'] == "BaZ"

    def test_get_reaction_modifier_404(self):
        uri = '/api/v1/reactions/reaction1/modifiers/no_modifier'
        response = self.client.get(uri)
        data = dict(self.get_json(response))
        assert response.status_code == 404
        assert data['error'] == "Not found"

    def test_get_reaction_components(self):
        response = self.client.get('/api/v1/reaction_components')
        data = dict(self.get_json(response))
        assert data['limit'] == 20
        assert data['offset'] == 6
        assert len(data['reaction_components']) == 6

    def test_get_reaction_components_search(self):
        query = '/api/v1/reaction_components?name={0}'
        response = self.client.get(query.format("Reactant"))
        data = dict(self.get_json(response))
        assert len(data['reaction_components']) == 1

        response = self.client.get(query.format("1"))
        data = dict(self.get_json(response))
        assert len(data['reaction_components']) == 5

    def test_get_reaction_component(self):
        response = self.client.get('/api/v1/reaction_components/product1')
        data = dict(self.get_json(response))
        assert data['component_id'] == "product1"
        assert data['short_name'] == "Product 1"
        assert data['long_name'] == "Product 1"
        assert data['type'] == "metabolite"
        assert data['organism'] == "Human"
        assert data['formula'] == "BAr"

    def test_get_reaction_component_404(self):
        response = self.client.get('/api/v1/reaction_components/no_component')
        data = dict(self.get_json(response))
        assert response.status_code == 404
        assert data['error'] == "Not found"

    def test_list_currency_metabolites(self):
        response = self.client.get(
            '/api/v1/reaction_components/modifier1/currency_metabolites'
        )
        data = dict(self.get_json(response))
        assert data['reaction_ids'] == ['reaction2']

    def test_get_reaction_component_expressions(self):
        response = self.client.get(
            '/api/v1/reaction_components/modifier1/expressions')
        data = dict(self.get_json(response))
        assert len(data['expressions']) == 1

    def test_list_interaction_partners(self):
        response = self.client.get(
            '/api/v1/reaction_components/modifier1/interaction_partners'
        )
        data = dict(self.get_json(response))
        assert len(data['reactions']) == 1
        reaction = data['reactions'][0]
        expected_reaction = {
            'reaction_id': 'reaction1',
            'modifiers': [
                {'long_name': 'Modifier 2',
                 'short_name': 'modifier2',
                 'component_id': 'modifier2',
                 'type': 'enzyme',
                 'formula': 'BaZ',
                 'organism': 'Human'}
            ],
            'products': [
                {'long_name': 'Product 1',
                 'short_name': 'Product 1',
                 'component_id': 'product1',
                 'type': 'metabolite',
                 'formula': 'BAr',
                 'organism': 'Human'}
            ],
            'reactants': [
                {'long_name': 'Reactant 1',
                 'compartment': 'Mitochondria',
                 'short_name': 'reactant1',
                 'component_id': 'reactant1',
                 'type': 'metabolite',
                 'formula': 'FO2',
                 'organism': 'Human'}
            ],
        }

        assert reaction == expected_reaction

    def test_get_connected_metabolites(self):
        response = self.client.get(
            '/api/v1/enzymes/Modifier 1/connected_metabolites'
        )
        data = dict(self.get_json(response))
        assert data['id'] == 'modifier1'
        assert data['short_name'] == 'modifier1'
        assert data['long_name'] == 'Modifier 1'
        assert data['compartment'] == 'Mitochondria'
        assert len(data['reactions']) == 1
        expected_reaction = {
            'reaction_id': 'reaction1',
            'modifiers': [],
            'products': [
                {'long_name': 'Product 1',
                 'short_name': 'Product 1',
                 'component_id': 'product1',
                 'type': 'metabolite',
                 'formula': 'BAr',
                 'organism': 'Human'}
            ],
            'reactants': [
                {'long_name': 'Reactant 1',
                 'compartment': 'Mitochondria',
                 'short_name': 'reactant1',
                 'component_id': 'reactant1',
                 'type': 'metabolite',
                 'formula': 'FO2',
                 'organism': 'Human'}
            ],
            'enzyme_role': 'modifier'
        }
        assert data['reactions'] == [expected_reaction]

    def test_get_connected_metabolites_no_compartment(self):
        response = self.client.get(
            '/api/v1/enzymes/Modifier 2/connected_metabolites'
        )
        data = dict(self.get_json(response))
        assert data['id'] == 'modifier2'
        assert data['short_name'] == 'modifier2'
        assert data['long_name'] == 'Modifier 2'
        with self.assertRaises(KeyError):
            data['compartment'] == None
        assert len(data['reactions']) == 1
        expected_reaction = {
            'reaction_id': 'reaction1',
            'modifiers': [],
            'products': [
                {'long_name': 'Product 1',
                 'short_name': 'Product 1',
                 'component_id': 'product1',
                 'type': 'metabolite',
                 'formula': 'BAr',
                 'organism': 'Human'}
            ],
            'reactants': [
                {'long_name': 'Reactant 1',
                 'compartment': 'Mitochondria',
                 'short_name': 'reactant1',
                 'component_id': 'reactant1',
                 'type': 'metabolite',
                 'formula': 'FO2',
                 'organism': 'Human'}
            ],
            'enzyme_role': 'modifier'
        }
        assert data['reactions'] == [expected_reaction]

    def test_get_connected_metabolites_include_expressions(self):
        response = self.client.get(
            ('/api/v1/enzymes/Modifier 1/connected_metabolites?'
             'include_expressions=true')
        )
        data = dict(self.get_json(response))
        assert data['id'] == 'modifier1'
        assert data['short_name'] == 'modifier1'
        assert data['long_name'] == 'Modifier 1'
        assert len(data['reactions']) == 1
        expected_reaction = {
            'reaction_id': 'reaction1',
            'modifiers': [],
            'products': [
                {'long_name': 'Product 1',
                 'short_name': 'Product 1',
                 'component_id': 'product1',
                 'type': 'metabolite',
                 'formula': 'BAr',
                 'organism': 'Human'}
            ],
            'reactants': [
                {'long_name': 'Reactant 1',
                 'compartment': 'Mitochondria',
                 'short_name': 'reactant1',
                 'component_id': 'reactant1',
                 'type': 'metabolite',
                 'formula': 'FO2',
                 'organism': 'Human'}
            ],
            'enzyme_role': 'modifier'
        }
        assert data['reactions'] == [expected_reaction]
        assert len(data['expressions']) == 1
        expected_expression = {
            'gene_id': 'Modifier 1',
            'gene_name': 'CTSV',
            'transcript_id': 'N/A',
            'tissue': 'pancreas',
            'cell_type': 'islets of Langerhans',
            'expression_type': 'APE',
            'level': 'Medium',
            'reliability': 'Uncertain',
            'source': 'HMA V14'
        }
        assert data['expressions'] == [expected_expression]

    def test_get_connected_metabolites_include_expressions_filter(self):
        response = self.client.get(
            ('/api/v1/enzymes/Modifier 1/connected_metabolites?'
             'include_expressions=true&tissue=pancreas')
        )
        data = dict(self.get_json(response))
        assert data['id'] == 'modifier1'
        assert data['short_name'] == 'modifier1'
        assert data['long_name'] == 'Modifier 1'
        assert len(data['reactions']) == 1
        expected_reaction = {
            'reaction_id': 'reaction1',
            'modifiers': [],
            'products': [
                {'long_name': 'Product 1',
                 'short_name': 'Product 1',
                 'component_id': 'product1',
                 'type': 'metabolite',
                 'formula': 'BAr',
                 'organism': 'Human'}
            ],
            'reactants': [
                {'long_name': 'Reactant 1',
                 'compartment': 'Mitochondria',
                 'short_name': 'reactant1',
                 'component_id': 'reactant1',
                 'type': 'metabolite',
                 'formula': 'FO2',
                 'organism': 'Human'}
            ],
            'enzyme_role': 'modifier'
        }
        assert data['reactions'] == [expected_reaction]
        assert len(data['expressions']) == 1
        expected_expression = {
            'gene_id': 'Modifier 1',
            'gene_name': 'CTSV',
            'transcript_id': 'N/A',
            'tissue': 'pancreas',
            'cell_type': 'islets of Langerhans',
            'expression_type': 'APE',
            'level': 'Medium',
            'reliability': 'Uncertain',
            'source': 'HMA V14'
        }
        assert data['expressions'] == [expected_expression]

    def test_get_connected_metabolites_include_expressions_bad_filter(self):
        response = self.client.get(
            ('/api/v1/enzymes/Modifier 1/connected_metabolites?'
             'include_expressions=true&tissue=adipose')
        )
        data = dict(self.get_json(response))
        assert data['id'] == 'modifier1'
        assert data['short_name'] == 'modifier1'
        assert data['long_name'] == 'Modifier 1'
        assert len(data['reactions']) == 1
        expected_reaction = {
            'reaction_id': 'reaction1',
            'modifiers': [],
            'products': [
                {'long_name': 'Product 1',
                 'short_name': 'Product 1',
                 'component_id': 'product1',
                 'type': 'metabolite',
                 'formula': 'BAr',
                 'organism': 'Human'}
            ],
            'reactants': [
                {'long_name': 'Reactant 1',
                 'compartment': 'Mitochondria',
                 'short_name': 'reactant1',
                 'component_id': 'reactant1',
                 'type': 'metabolite',
                 'formula': 'FO2',
                 'organism': 'Human'}
            ],
            'enzyme_role': 'modifier'
        }
        assert data['reactions'] == [expected_reaction]
        assert len(data['expressions']) == 0

    def test_get_connected_metabolites_404(self):
        response = self.client.get(
            '/api/v1/enzymes/NO_SUCH_ENZYME/connected_metabolites'
        )
        data = self.get_json(response)
        assert response.status_code == 404
        assert data['error'] == "Not found"

    def test_get_connected_metabolites_500(self):
        response = self.client.get(
            '/api/v1/enzymes/Dupe 1/connected_metabolites'
        )
        data = self.get_json(response)
        assert response.status_code == 500
        assert data['error'] == "Internal server error"

    def test_list_expressions(self):
        response = self.client.get('/api/v1/expressions/Modifier 1')
        data = dict(self.get_json(response))
        assert len(data['expressions']) == 1
        expected_expression = {
            'gene_id': 'Modifier 1',
            'gene_name': 'CTSV',
            'transcript_id': 'N/A',
            'tissue': 'pancreas',
            'cell_type': 'islets of Langerhans',
            'expression_type': 'APE',
            'level': 'Medium',
            'reliability': 'Uncertain',
            'source': 'HMA V14'
        }
        assert data['expressions'] == [expected_expression]

    def test_list_expressions_no_expressions(self):
        response = self.client.get('/api/v1/expressions/Product 1')
        data = dict(self.get_json(response))
        assert len(data['expressions']) == 0

    def get_json(self, response):
        return json.loads(response.data.decode('utf-8'))

    @classmethod
    def populate_db(cls):
        model = MetabolicModel()
        model.short_name = "TestModel"
        model.name = "Metabolic test model"
        author1 = Author()
        author1.given_name = "First"
        author1.family_name = "Author"
        author1.email = "first.author@example.com"
        author1.organization = "ACME Modeling"
        author2 = Author()
        author2.given_name = "Second"
        author2.family_name = "Author"
        author2.email = "second.author@example.com"
        author2.organization = "ACME Modeling"
        model.authors.append(author1)
        model.authors.append(author2)

        db.session.add(model)

        compartment1 = Compartment(id=1, name="Mitochondria")

        db.session.add(compartment1)

        reactant1 = ReactionComponent(id="reactant1")
        reactant1.short_name = "reactant1"
        reactant1.long_name = "Reactant 1"
        reactant1.component_type = "metabolite"
        reactant1.compartment = compartment1.id
        reactant1.organism = "Human"
        reactant1.formula = "FO2"

        product1 = ReactionComponent(id="product1")
        product1.long_name = "Product 1"
        product1.component_type = "metabolite"
        product1.organism = "Human"
        product1.formula = "BAr"

        modifier1 = ReactionComponent(id="modifier1")
        modifier1.short_name = "modifier1"
        modifier1.long_name = "Modifier 1"
        modifier1.component_type = "enzyme"
        modifier1.compartment = compartment1.id
        modifier1.organism = "Human"
        modifier1.formula = "BaZ"

        modifier2 = ReactionComponent(id="modifier2")
        modifier2.short_name = "modifier2"
        modifier2.long_name = "Modifier 2"
        modifier2.component_type = "enzyme"
        # no compartment here
        modifier2.organism = "Human"
        modifier2.formula = "BaZ"

        dupe_enzyme1 = ReactionComponent(id="dupe_enzyme1")
        dupe_enzyme1.short_name = "dupe_enzyme1"
        dupe_enzyme1.long_name = "Dupe 1"
        dupe_enzyme1.component_type = "enzyme"
        dupe_enzyme1.organism = "Human"
        dupe_enzyme1.formula = "BaZ"

        dupe_enzyme2 = ReactionComponent(id="dupe_enzyme2")
        dupe_enzyme2.short_name = "dupe_enzyme1"
        dupe_enzyme2.long_name = "Dupe 1"
        dupe_enzyme2.component_type = "enzyme"
        dupe_enzyme2.organism = "Human"
        dupe_enzyme2.formula = "BaZ"

        db.session.add(dupe_enzyme1)
        db.session.add(dupe_enzyme2)

        expression_data1 = ExpressionData(id='modifier1')
        expression_data1.gene_id = modifier1.long_name
        expression_data1.gene_name = "CTSV"
        expression_data1.transcript_id = "N/A"
        expression_data1.tissue = "pancreas"
        expression_data1.cell_type = "islets of Langerhans"
        expression_data1.level = "Medium"
        expression_data1.expression_type = "APE"
        expression_data1.reliability = "Uncertain"
        expression_data1.source = "HMA V14"

        db.session.add(expression_data1)

        reaction1 = Reaction(id="reaction1")
        reaction1.name = "Reaction"
        reaction1.sbo_id = "SBO:0000176"
        reaction1.equation = "FO2 => BAr"
        reaction1.lower_bound = 0.0
        reaction1.upper_bound = 1.0
        reaction1.objective_coefficient = 1.0
        reaction1.reactants.append(reactant1)
        reaction1.products.append(product1)
        reaction1.modifiers.append(modifier1)
        reaction1.modifiers.append(modifier2)

        db.session.add(reaction1)

        reaction2 = Reaction(id="reaction2")
        reaction2.name = "Reaction"
        reaction2.sbo_id = "SBO:0000176"
        reaction2.equation = "FO2 => BAr"
        reaction2.lower_bound = 0.0
        reaction2.upper_bound = 1.0
        reaction2.objective_coefficient = 1.0

        db.session.add(reaction2)

        modifier1.currency_metabolites.append(reaction2)
        db.session.add(modifier1)

        db.session.commit()


class ModelTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_model_repr(self):
        model = MetabolicModel(short_name="Model")
        assert model.__repr__() == "<MetabolicModel: Model>"

    def test_author_repr(self):
        author = Author(given_name="Given", family_name="Family")
        assert author.__repr__() == "<Author: Given Family>"

    def test_reaction_repr(self):
        reaction = Reaction(id="MyReaction")
        assert reaction.__repr__() == "<Reaction: MyReaction>"

    def test_reaction_component_repr(self):
        rc = ReactionComponent(id="MyComponent")
        assert rc.__repr__() == "<ReactionComponent: MyComponent>"


if __name__ == "__main__":
    try:
        unittest.main()
    except:
        pass
    cov.stop()
    cov.save()
    print("\n\nCoverage Report:\n")
    cov.report()
    print("\nHTML Version: " +
          os.path.join(basedir, "tmp/coverage/index.html"))
    cov.html_report(directory='tmp/coverage')
    cov.erase()
