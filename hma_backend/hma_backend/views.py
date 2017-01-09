from flask import jsonify, abort, url_for
from flask import make_response, request
from flask_swagger import swagger
from sqlalchemy import or_, and_
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from hma_backend import app
from hma_backend.models import *


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin','*')
    response.headers.add('Access-Control-Allow-Headers',
                         "Authorization, Content-Type")
    response.headers.add('Access-Control-Expose-Headers', "Authorization")
    response.headers.add('Access-Control-Allow-Methods',
                         "GET, POST, PUT, DELETE, OPTIONS")
    response.headers.add('Access-Control-Allow-Credentials', "true")
    response.headers.add('Access-Control-Max-Age', 60 * 60 * 24 * 20)
    return response


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(405)
def method_not_allowed(error):
    return make_response(jsonify({'error': 'Method not allowed'}), 405)


@app.errorhandler(500)
def internal_server_error(error):
    return make_response(jsonify({'error': 'Internal server error'}), 500)


@app.route("/")
def index():
    msg = ("Welcome to the Human Metabolic Atlas! Please check the API "
           "documentation for usage.")
    return jsonify({'message': msg})


@app.route("/api/v1/spec")
def spec():
    swag = swagger(app)
    swag['info']['version'] = "1.0"
    swag['info']['title'] = "Human Metabolic Atlas"
    swag['info']['description'] = ("This is an API for accessing "
                                   "metabolic models")
    return jsonify(swag)


@app.route("/api/v1/models")
def list_models():
    """
    List models
    ---
    tags:
      - Models
    responses:
      200:
        description: Returns a list of Models
        schema:
          type: array
          items:
            $ref: "#/definitions/Model"
    """
    models = MetabolicModel.query.all()
    json_models = [make_public_model(model) for model in models]
    return jsonify({'models': json_models})


@app.route("/api/v1/models/<int:model_id>")
def list_model(model_id):
    """
    Find model by ID
    ---
    tags:
      - Models
    definitions:
      - schema:
          id: Model
          type: object
          properties:
            model_id:
              type: integer
              description: Model ID
              default: 1
            short_name:
              type: string
              description: Short model name
              default: HMR2.0
            name:
              type: string
              description: Model name
              default: Human Metabolic Reaction (2.0) Database
            authors:
              type: array
              items:
                $ref: "#/definitions/Author"
    parameters:
      - in: path
        name: model_id
        type: integer
        format: int32
        required: true
        description: Model ID
    responses:
      200:
        description: Returns the specified model
        schema:
          $ref: "#/definitions/Model"
      404:
        description: Model not found
    """
    model = MetabolicModel.query.get_or_404(model_id)
    return jsonify(make_public_model(model))


def make_public_model(model):
    json = {}
    json['model_id'] = model.id
    json['short_name'] = model.short_name
    json['name'] = model.name
    json['authors'] = [make_public_author(author) for author in model.authors]
    return json


@app.route("/api/v1/authors")
def list_authors():
    """
    List authors
    ---
    tags:
      - Authors
    responses:
      200:
        description: Returns a list of Authors
        schema:
          type: array
          items:
            $ref: "#/definitions/Author"
    """
    authors = Author.query.all()
    json_authors = [make_public_author(author) for author in authors]
    return jsonify({'authors': json_authors})


@app.route("/api/v1/authors/<int:author_id>")
def list_author(author_id):
    """
    Find author by ID
    ---
    tags:
      - Authors
    definitions:
      - schema:
          id: Author
          type: object
          properties:
            author_id:
              type: integer
              description: Author ID
              default: 1
            given_name:
              type: string
              description: Author's given name
              default: Author
            family_name:
              type: string
              description: Author's family name
              default: McAuthor
            email:
              type: string
              description: Author's email
              default: author.mcauthor@example.com
            organization:
              type: string
              description: Author's organization
              default: ACME Modelers
            models:
              type: array
              items:
                type: integer
                default: 1
    parameters:
      - in: path
        name: author_id
        type: integer
        format: int32
        required: true
        description: Author ID
    responses:
      200:
        description: Returns the specified Author
        schema:
          $ref: "#/definitions/Author"
      404:
        description: Author not found
    """
    author = Author.query.get_or_404(author_id)
    return jsonify(make_public_author(author))


def make_public_author(author):
    json = {}
    json['author_id'] = author.id
    json['given_name'] = author.given_name
    json['family_name'] = author.family_name
    json['email'] = author.email
    json['organization'] = author.organization
    json['models'] = [model.id for model in author.models]
    return json


@app.route("/api/v1/reactions")
def list_reactions():
    """
    List reactions
    ---
    tags:
      - Reactions
    parameters:
      - in: query
        name: limit
        type: integer
        description: Maximum number of results to return
      - in: query
        name: offset
        type: integer
        description: Offset for database query
    responses:
      200:
        description: Returns a list of Reactions
        schema:
          type: object
          properties:
            limit:
              type: integer
              description: Maximum number of results to return
              default: 20
            offset:
              type: integer
              description: Offset for database query
              default: 20
            reactions:
              type: array
              items:
                $ref: "#/definitions/Reaction"
    """
    limit = int(request.args.get('limit', 20))
    offset = int(request.args.get('offset', 0))
    reactions = Reaction.query.limit(limit).offset(offset).all()
    json = {}
    json['offset'] = offset + len(reactions)
    json['limit'] = limit
    json['reactions'] = [make_public_reaction(reaction)
                         for reaction in reactions]
    return jsonify(json)


@app.route("/api/v1/reactions/<string:reaction_id>")
def list_reaction(reaction_id):
    """
    Find reaction by ID
    ---
    tags:
      - Reactions
    definitions:
      - schema:
          id: Reaction
          type: object
          properties:
            reaction_id:
              type: string
              description: Reaction ID
              default: R_HMR_3905
            name:
              type: string
              description: Reaction name
            sbo_id:
              type: string
              description: SBO ID
              default: "SBO:0000176"
            equation:
              type: string
              description: Equation
              default: "reactant_1 + ... + reactant_n => product_1 + ... + product_m"
            ec:
              type: string
              description: zero to many EC numbers separataed by ;
              default: "EC:2.7.1.1;EC:2.7.1.2;EC:2.7.1.147"
            lower_bound:
              type: number
              format: float
              description: Lower bound
              default: 0.0
            upper_bound:
              type: number
              format: float
              description: Upper bound
              default: 1.0
            objective_coefficient:
              type: number
              format: float
              description: Objective coefficient
              default: 1.0
            reactants:
              type: array
              items:
                $ref: "#/definitions/ReactionComponent"
              description: Reactants
            products:
              type: array
              items:
                $ref: "#/definitions/ReactionComponent"
              description: Products
            modifiers:
              type: array
              items:
                $ref: "#/definitions/ReactionComponent"
              description: Modifiers
    parameters:
      - in: path
        name: reaction_id
        type: string
        required: true
        description: Reaction ID
    responses:
      200:
        description: Returns the specified Reaction
        schema:
          $ref: "#/definitions/Reaction"
      404:
        description: Reaction not found
    """
    reaction = Reaction.query.get_or_404(reaction_id)
    return jsonify(make_public_reaction(reaction))


def make_public_reaction(reaction):
    json = {}
    json['reaction_id'] = reaction.id
    json['name'] = reaction.name
    json['sbo_id'] = reaction.sbo_id
    json['equation'] = reaction.equation
    json['ec'] = reaction.ec
    json['lower_bound'] = float(reaction.lower_bound)
    json['upper_bound'] = float(reaction.upper_bound)
    json['objective_coefficient'] = float(reaction.objective_coefficient)
    json['reactants'] = [make_public_component(component)
                         for component in reaction.reactants]
    json['products'] = [make_public_component(component)
                        for component in reaction.products]
    json['modifiers'] = [make_public_component(component)
                         for component in reaction.modifiers]
    return json


@app.route("/api/v1/reactions/<string:reaction_id>/reactants")
def list_reaction_reactants(reaction_id):
    """
    List reactants for a specific reaction
    ---
    tags:
      - Reactions
    parameters:
      - in: path
        name: reaction_id
        type: string
        description: Reaction ID
        required: true
    responses:
      200:
        description: Returns a list of reactants for the specified reaction
        schema:
          type: array
          items:
            $ref: "#/definitions/ReactionComponent"
    """
    reaction = Reaction.query.get_or_404(reaction_id)
    reactants = [make_public_component(reactant)
                 for reactant in reaction.reactants]
    return jsonify({'reactants': reactants})


@app.route("/api/v1/reactions/<string:reaction_id>/reactants/<string:reactant_id>")
def list_reaction_reactant(reaction_id, reactant_id):
    """
    Find reactant by ID for a specific reaction
    ---
    tags:
      - Reactions
    parameters:
      - in: path
        name: reaction_id
        type: string
        description: Reaction ID
        required: true
      - in: path
        name: reactant_id
        type: string
        description: Reactant ID
        required: true
    responses:
      200:
        description: Returns the specified reactant
        schema:
          $ref: "#/definitions/ReactionComponent"
      404:
        description: Reactant not found
    """
    reaction = Reaction.query.get_or_404(reaction_id)
    reactants = [reactant for reactant in reaction.reactants if
                 reactant.id == reactant_id]
    if len(reactants) == 1:
        return jsonify(make_public_component(reactants[0]))
    else:
        abort(404)


@app.route("/api/v1/reactions/<string:reaction_id>/products")
def list_reaction_products(reaction_id):
    """
    List products for a specific reaction
    ---
    tags:
      - Reactions
    parameters:
      - in: path
        name: reaction_id
        type: string
        description: Reaction ID
        required: true
    responses:
      200:
        description: Returns a list of products for the specified reaction
        schema:
          type: array
          items:
            $ref: "#/definitions/ReactionComponent"
    """
    reaction = Reaction.query.get_or_404(reaction_id)
    products = [make_public_component(product)
                for product in reaction.products]
    return jsonify({'products': products})


@app.route("/api/v1/reactions/<string:reaction_id>/products/<string:product_id>")
def list_reaction_product(reaction_id, product_id):
    """
    Find product by ID for a specific reaction
    ---
    tags:
      - Reactions
    parameters:
      - in: path
        name: reaction_id
        type: string
        description: Reaction ID
        required: true
      - in: path
        name: product_id
        type: string
        description: Product ID
        required: true
    responses:
      200:
        description: Returns the specified product
        schema:
          $ref: "#/definitions/ReactionComponent"
      404:
        description: Product not found
    """
    reaction = Reaction.query.get_or_404(reaction_id)
    products = [product for product in reaction.products if
                product.id == product_id]
    if len(products) == 1:
        return jsonify(make_public_component(products[0]))
    else:
        abort(404)


@app.route("/api/v1/reactions/<string:reaction_id>/modifiers")
def list_reaction_modifiers(reaction_id):
    """
    List modifiers for a specific reaction
    ---
    tags:
      - Reactions
    parameters:
      - in: path
        name: reaction_id
        type: string
        description: Reaction ID
        required: true
    responses:
      200:
        description: Returns a list of modifiers for the specified reaction
        schema:
          type: array
          items:
            $ref: "#/definitions/ReactionComponent"
    """
    reaction = Reaction.query.get_or_404(reaction_id)
    modifiers = [make_public_component(modifier)
                 for modifier in reaction.modifiers]
    return jsonify({'modifiers': modifiers})


@app.route("/api/v1/reactions/<string:reaction_id>/modifiers/<string:modifier_id>")
def list_reaction_modifier(reaction_id, modifier_id):
    """
    Find modifier by ID for a specific reaction
    ---
    tags:
      - Reactions
    parameters:
      - in: path
        name: reaction_id
        type: string
        description: Reaction ID
        required: true
      - in: path
        name: modifier_id
        type: string
        description: Modifier ID
        required: true
    responses:
      200:
        description: Returns the specified modifier
        schema:
          $ref: "#/definitions/ReactionComponent"
      404:
        description: Modifier not found
    """
    reaction = Reaction.query.get_or_404(reaction_id)
    modifiers = [modifier for modifier in reaction.modifiers if
                modifier.id == modifier_id]
    if len(modifiers) == 1:
        return jsonify(make_public_component(modifiers[0]))
    else:
        abort(404)


@app.route("/api/v1/reaction_components")
def list_components():
    """
    List reaction components
    ---
    tags:
      - ReactionComponents
    parameters:
      - in: query
        name: limit
        type: integer
        description: Maximum number of results to return
      - in: query
        name: offset
        type: integer
        description: Offset for database query
      - in: query
        name: name
        type: string
        description: Filter on component_id, short_name, or long_name
    responses:
      200:
        description: Returns a list of ReactionComponentss
        schema:
          type: object
          properties:
            limit:
              type: integer
              description: Maximum number of results to return
              default: 20
            offset:
              type: integer
              description: Offset for database query
              default: 20
            reaction_components:
              type: array
              items:
                $ref: "#/definitions/ReactionComponent"
    """
    limit = int(request.args.get('limit', 20))
    offset = int(request.args.get('offset', 0))
    maybe_name = request.args.get('name')
    if maybe_name:
        search = "%{0}%".format(maybe_name)
        components = ReactionComponent.query.filter(
            or_(ReactionComponent.id.ilike(search),
                or_(ReactionComponent.long_name.ilike(search),
                    ReactionComponent.short_name.ilike(search)))).\
                    limit(limit).offset(offset).all()
    else:
        components = ReactionComponent.query.limit(limit).offset(offset).all()
    json = {}
    json['limit'] = limit
    json['offset'] = offset + len(components)
    json['reaction_components'] = [make_public_component(component)
                                   for component in components]
    return jsonify(json)


@app.route("/api/v1/reaction_components/<string:component_id>")
def list_component(component_id):
    """
    Find reaction component by ID
    ---
    tags:
      - ReactionComponents
    definitions:
      - schema:
          id: ReactionComponent
          type: object
          properties:
            component_id:
              type: string
              description: Reaction component ID
              default: M_m02040s
            short_name:
              type: string
              description: Short name
              default: H2O
            long_name:
              type: string
              description: Long name
              default: H2O
            type:
              type: string
              description: Reaction component type
              default: metabolite
            organism:
              type: string
              description: Organism
              default: Human
            formula:
              type: string
              description: Formula
              default: H2O
    parameters:
      - in: path
        name: component_id
        type: string
        required: true
        description: Reaction component ID
    responses:
      200:
        description: Returns the specified ReactionComponent
        schema:
          $ref: "#/definitions/ReactionComponent"
      404:
        description: ReactionComponent not found
    """
    component = ReactionComponent.query.get_or_404(component_id)
    return jsonify(make_public_component(component))


def make_public_component(component):
    json = {}
    json['component_id'] = component.id
    json['type'] = component.component_type
    if component.short_name:
        json['short_name'] = component.short_name
    else:
        json['short_name'] = component.long_name
    json['long_name'] = component.long_name
    json['type'] = component.component_type
    json['organism'] = component.organism
    json['formula'] = component.formula
    if component.compartment:
        json['compartment'] = Compartment.query.get(component.compartment).name
    return json


@app.route(
    "/api/v1/reaction_components/<string:component_id>/currency_metabolites"
)
def list_currency_metabolites(component_id):
    """
    Find currency metabolites for reaction component by ID
    ---
    tags:
      - ReactionComponent
      - Reaction
    parameters:
      - in: path
        name: component_id
        type: string
        required: true
        description: Reaction component ID
    responses:
      200:
        description: Returns the reaction IDs in which the given metabolite
                     is considered a 'currency metabolite', meaning a metabolite
                     that has multiple uses in different reactions/pathways,
                     such as ATP and NAD.
        schema:
          type: objcet
          properties:
            reaction_ids:
              type: array
              items:
                type: string
      404:
        description: ReactionComponent not found
    """
    component = ReactionComponent.query.get_or_404(component_id)
    reaction_ids = [reaction.id for reaction in component.currency_metabolites]
    return jsonify({'reaction_ids': reaction_ids})


@app.route("/api/v1/reaction_components/<string:component_id>/expressions")
def list_component_expressions(component_id):
    """
    Find expressions for reaction component by ID
    ---
    tags:
      - ReactionComponents
      - Expressions
    parameters:
      - in: path
        name: component_id
        type: string
        required: true
        description: Reaction component ID
      - in: query
        name: tissue
        type: string
        description: Tissue to filter on
      - in: query
        name: expression_type
        type: string
        description: Expression type to filter on
    responses:
      200:
        description: Returns the expressions for the specified ReactionComponent
        schema:
          type: object
          properties:
            expressions:
              type: array
              items:
                $ref: "#/definitions/Expression"
      404:
        description: ReactionComponent not found
    """
    # FIXME when to return 404?
    tissue = request.args.get('tissue', '')
    expression_type = request.args.get('expression_type', '')
    expressions = ExpressionData.query.filter(
        and_(ExpressionData.id == component_id,
             and_(ExpressionData.tissue.ilike(tissue + '%'),
                  ExpressionData.expression_type.ilike(expression_type + '%'))
        )
    ).all()
    expressions = [make_public_expression(e) for e in expressions]
    return jsonify({'expressions': expressions})

@app.route("/api/v1/reaction_components/<string:component_id>/interaction_partners")
def list_interaction_partners(component_id):
    """
    List interaction partners
    ---
    tags:
      - ReactionComponents
    parameters:
      - in: path
        name: component_id
        type: string
        required: true
        description: Reaction component ID
    definitions:
      - schema:
          id: InteractionPartners
          type: object
          properties:
            reaction_id:
              type: string
              description: Reaction ID
              default: R_HMR_3905
            modifiers:
              type: array
              description: Reaction modifiers
              items:
                $ref: "#/definitions/ReactionComponent"
            reactants:
              type: array
              description: Reaction reactants
              items:
                $ref: "#/definitions/ReactionComponent"
            products:
              type: array
              description: Reaction products
              items:
                $ref: "#/definitions/ReactionComponent"
            currency_metabolites:
              type: array
              description: Currency metabolite IDs
              items:
                type: string
    responses:
      200:
        description: Returns a list of interaction partners
        schema:
          type: object
          properties:
            reactions:
              type: array
              items:
                $ref: "#/definitions/InteractionPartners"
    """
    # FIXME component_id or long_name here?
    component = ReactionComponent.query.get_or_404(component_id)
    reactions = (component.reactions_as_reactant +
                 component.reactions_as_product +
                 component.reactions_as_modifier)
    interaction_partners = {}
    interaction_partners['reactions'] = []
    for reaction in reactions:
        partners = {}
        partners['reaction_id'] = reaction.id
        partners['modifiers'] = [make_public_component(modifier) for
                                 modifier in reaction.modifiers if
                                 modifier.id != component_id]
        partners['products'] = [make_public_component(modifier) for
                                 modifier in reaction.products if
                                 modifier.id != component_id]
        partners['reactants'] = [make_public_component(modifier) for
                                 modifier in reaction.reactants if
                                 modifier.id != component_id]
        partners['currency_metabolites'] = [cm.id for cm in
                                            reaction.currency_metabolites]
        interaction_partners['reactions'].append(partners)

    return jsonify(interaction_partners)

@app.route("/api/v1/enzymes")
def somethinghere():
    return jsonify("You wanna look at enzymes?")

@app.route("/api/v1/enzymes/<string:enzyme_id>/connected_metabolites")
def connected_metabolites(enzyme_id):
    """
    Find connected metabolites
    ---
    tags:
      - ReactionComponents
      - Reactions
    definitions:
      - schema:
          id: ConnectedMetabolites
          type: object
          properties:
            enzyme_id:
              type: string
              description: Enzyme ID
              default: E_1
            short_name:
              type: string
              description: Enzyme short name
              default: DPM1
            long_name:
              type: string
              description: Enzyme long name
              default: ENSG00000000419
            compartment:
              type: string
              description: Compartment
              default: Cytosol
            reactions:
              type: array
              items:
                $ref: "#/definitions/Reaction"
              description: Reactions
            expressions:
              type: array
              items:
                $ref: "#/definitions/Expression"
              description: Expressions
    parameters:
      - in: path
        name: enzyme_id
        type: string
        required: true
        description: Enzyme ID
      - in: query
        name: tissue
        type: string
        description: Tissue to filter on for expression data
      - in: query
        name: expression_type
        type: string
        description: Expression type to filter on for expression data
    responses:
      200:
        description: Returns the connected metabolites for the specified enzyme
        schema:
          $ref: "#/definitions/ConnectedMetabolites"
      404:
        description: Enzyme not found
    """
    try:
        tissue = request.args.get('tissue', '')
        expression_type = request.args.get('expression_type', '')
        include_expressions = False
        # include expressions iff parameter is set to 'true'
        if request.args.get('include_expressions') == 'true':
            include_expressions = True
        enzyme = ReactionComponent.query.filter(
            and_(ReactionComponent.component_type == "enzyme",
                 ReactionComponent.long_name == enzyme_id)).one()
        as_reactant = get_metabolites(enzyme.reactions_as_reactant, "reactant")
        as_product = get_metabolites(enzyme.reactions_as_product, "product")
        as_modifier = get_metabolites(enzyme.reactions_as_modifier, "modifier")
        reactions = as_reactant + as_product + as_modifier
        json = {}
        json['id'] = enzyme.id
        json['short_name'] = enzyme.short_name
        json['long_name'] = enzyme.long_name
        if enzyme.compartment:
            json['compartment'] = Compartment.query.get(enzyme.compartment).name
        json['id'] = enzyme.id
        json['reactions'] = [make_public_reaction_metabolites(reaction) for
                             reaction in reactions]
        if include_expressions:
            expressions = get_expressions(enzyme_id, tissue, expression_type)
            json['expressions'] = [make_public_expression(expr) for
                                       expr in expressions]
        return jsonify(json)
    except NoResultFound:
        abort(404)
    except MultipleResultsFound:
        abort(500)


def get_metabolites(reactions, role):
    metabolites = []
    for r in reactions:
        reaction_id = r.id
        reactants = [m for m in r.reactants
                     if m.component_type == "metabolite"]
        products = [m for m in r.products
                    if m.component_type == "metabolite"]
        modifiers = [m for m in r.modifiers
                     if m.component_type == "metabolite"]
        metabolites.append((reaction_id, role, reactants,
                          products, modifiers))
    return metabolites


@app.route("/api/v1/expressions/<string:enzyme_id>")
def list_expressions(enzyme_id):
    """
    List expressions
    ---
    tags:
      - Expressions
    definitions:
      - schema:
          id: Expression
          type: object
          properties:
            id:
              type: string
              description: Component ID
              default: M_m02040s
            gene_id:
              type: string
              description: ENSEMBL Gene ID
              default: ENSG00000000419
            gene_name:
              type: string
              description: Gene name
              default: DPM1
            transcript_id:
              type: string
              description: Transcript ID
              default: N/A
            tissue:
              type: string
              description: Tissue
              default: Colon
            cell_type:
              type: string
              description: Cell type
              default: glandular cells
            level:
              type: string
              description: Level
              default: High
            expression_type:
              type: string
              description: Expression type
              default: APE
            reliability:
              type: string
              description: Reliability
              default: Uncertain
            source:
              type: string
              description: Data source
              default: HPA V14
    parameters:
      - in: path
        name: enzyme_id
        type: string
        required: true
        description: ENSEMBL gene ID
      - in: query
        name: tissue
        type: string
        description: Tissue to filter on
      - in: query
        name: expression_type
        type: string
        description: Expression type to filter on
    responses:
      200:
        description: Returns a list of expression data
        schema:
          type: object
          properties:
            expressions:
              type: array
              items:
                $ref: "#/definitions/Expression"
    """
    tissue = request.args.get('tissue', '')
    expression_type = request.args.get('expression_type', '')
    expressions = get_expressions(enzyme_id, tissue, expression_type)
    json_expressions = [make_public_expression(expr) for
                           expr in expressions]
    return jsonify({'expressions': json_expressions})


def get_expressions(enzyme_id, tissue='', expression_type=''):
    return ExpressionData.query.filter(
        # this allows us to use the GIS index. \o/
        and_(ExpressionData.gene_id.like(enzyme_id),
             and_(ExpressionData.tissue.ilike(tissue + '%'),
                  ExpressionData.expression_type.ilike(expression_type + '%'))
        )
    ).all()


def make_public_expression(expression):
    json = {}
    json['gene_id'] = expression.gene_id
    json['gene_name'] = expression.gene_name
    json['transcript_id'] = expression.transcript_id
    json['tissue'] = expression.tissue
    json['expression_type'] = expression.expression_type
    json['level'] = expression.level
    json['cell_type'] = expression.cell_type
    json['reliability'] = expression.reliability
    json['source'] = expression.source

    return json


def make_public_reaction_metabolites(reaction):
    (reaction_id, role, reactants, products, modifiers) = reaction
    json = {}
    json['reaction_id'] = reaction_id
    json['enzyme_role'] = role
    json['reactants'] = [make_public_component(c) for c in reactants]
    json['products'] = [make_public_component(c) for c in products]
    json['modifiers'] = [make_public_component(c) for c in modifiers]

    return json
