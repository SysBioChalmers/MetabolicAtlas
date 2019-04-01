from rest_framework import serializers
import api.models as APImodels
import api.serializers_rc as APIrcSerializer
from django.db import models

import logging


class ReactionReferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = APImodels.ReactionReference
        fields = ('pmid',)

class SubsystemReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = APImodels.SubsystemReaction
        fields = ('reaction', 'subsystem')

# ===============================================================================

class ReactionBasicSerializer(serializers.ModelSerializer):
    id_equation = serializers.SerializerMethodField('read_id_equation')
    equation = serializers.SerializerMethodField('read_equation')
    name_gene_rule = serializers.SerializerMethodField('read_name_gene_rule')
    subsystem = serializers.SerializerMethodField('read_subsystem')

    class Meta:
        model = APImodels.Reaction
        fields = ('id', 'id_equation', 'equation', 'gene_rule', 'name_gene_rule', 'ec', 'lower_bound', 'upper_bound', 'objective_coefficient',
                'compartment', 'subsystem', 'is_transport', 'is_reversible',)
    def read_subsystem(self, model):
        return model.subsystem_str

    def read_equation(self, model):
        return model.equation_wname

    def read_id_equation(self, model):
        return model.equation

    def read_name_gene_rule(self, model):
        return model.gene_rule_wname


class HmrReactionBasicSerializer(ReactionBasicSerializer):
    class Meta(ReactionBasicSerializer.Meta):
        model = APImodels.Reaction
        fields = ReactionBasicSerializer.Meta.fields + \
            ('sbo_id',)

# serializer use for reactome table
class HmrReactionBasicRTSerializer(ReactionBasicSerializer):
    modifiers = APIrcSerializer.ReactionComponentLiteSerializer(many=True)

    class Meta(ReactionBasicSerializer.Meta):
        model = APImodels.Reaction
        fields = ReactionBasicSerializer.Meta.fields + \
            ('modifiers',)

# serializer use for searchTable table
class ReactionSearchSerializer(serializers.ModelSerializer):
    subsystem = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='name',
     )

    class Meta:
        model = APImodels.Reaction
        fields = ('id', 'equation_wname', 'subsystem', 'compartment', 'is_transport')


class ReactionLiteSerializer(ReactionBasicSerializer):
    reactants = APIrcSerializer.ReactionComponentLiteSerializer(many=True)
    products = APIrcSerializer.ReactionComponentLiteSerializer(many=True)
    modifiers = APIrcSerializer.ReactionComponentLiteSerializer(many=True)

    class Meta(ReactionBasicSerializer.Meta):
        model = APImodels.Reaction
        fields = ReactionBasicSerializer.Meta.fields + \
            ('reactants', 'products', 'modifiers')


class HmrReactionLiteSerializer(ReactionLiteSerializer):
    # more ids will be added
    mnxref_id = serializers.SerializerMethodField('read_mnxref')
    mnxref_link =  serializers.SerializerMethodField('read_mnxref_link')

    class Meta(ReactionLiteSerializer.Meta):
        model = APImodels.Reaction
        fields = ReactionLiteSerializer.Meta.fields + \
            ('sbo_id', 'mnxref_id', 'mnxref_link',)

    def read_mnxref(self, model):
        return model.external_id1

    def read_mnxref_link(self, model):
        return model.external_link1


class ReactionSerializer(ReactionBasicSerializer):
    reactants = APIrcSerializer.MetaboliteReactionComponentSerializer(many=True)
    products = APIrcSerializer.MetaboliteReactionComponentSerializer(many=True)
    modifiers = APIrcSerializer.EnzymeReactionComponentSerializer(many=True)
    subsystem = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='name',
     )

    class Meta(ReactionBasicSerializer.Meta):
        model = APImodels.Reaction
        fields = ReactionBasicSerializer.Meta.fields + \
            ('reactants', 'products', 'modifiers', 'external_id1', 'external_link1', 'external_id2', 'external_link2',
                'external_id3', 'external_link3', 'external_id4', 'external_link4',)


class HmrReactionSerializer(ReactionBasicSerializer):
    reactants = APIrcSerializer.HmrMetaboliteReactionComponentSerializer(many=True)
    products = APIrcSerializer.HmrMetaboliteReactionComponentSerializer(many=True)
    modifiers = APIrcSerializer.HmrEnzymeReactionComponentSerializer(many=True)
    subsystem = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='name',
     )
    mnxref_id = serializers.SerializerMethodField('read_mnxref')
    mnxref_link =  serializers.SerializerMethodField('read_mnxref_link')

    class Meta(ReactionBasicSerializer.Meta):
        model = APImodels.Reaction
        fields = ReactionBasicSerializer.Meta.fields + \
            ('sbo_id', 'reactants', 'products', 'modifiers', 'mnxref_id', 'mnxref_link')

    def read_mnxref(self, model):
        return model.external_id1

    def read_mnxref_link(self, model):
        return model.external_link1

# =========================================================================================

class InteractionPartnerSerializer(serializers.ModelSerializer):
    modifiers = APIrcSerializer.ReactionComponentSerializer(many=True, read_only=True)
    products = APIrcSerializer.ReactionComponentSerializer(many=True, read_only=True)
    reactants = APIrcSerializer.ReactionComponentSerializer(many=True, read_only=True)

    class Meta:
        model = APImodels.Reaction
        fields = ('id', 'is_reversible', 'modifiers', 'products', 'reactants')


class HmrInteractionPartnerLiteSerializer(serializers.ModelSerializer):
    modifiers = APIrcSerializer.ReactionComponentLiteSerializer(many=True, read_only=True)
    products = APIrcSerializer.ReactionComponentLiteSerializer(many=True, read_only=True)
    reactants = APIrcSerializer.ReactionComponentLiteSerializer(many=True, read_only=True)

    class Meta:
        model = APImodels.Reaction
        fields = ('id', 'is_reversible', 'modifiers', 'products', 'reactants')


class HmrInteractionPartnerSerializer(serializers.ModelSerializer):
    modifiers = APIrcSerializer.HmrEnzymeReactionComponentInteractionPartnerSerializer(many=True, read_only=True)
    products = APIrcSerializer.HmrMetaboliteReactionComponentInteractionPartnerSerializer(many=True, read_only=True)
    reactants = APIrcSerializer.HmrMetaboliteReactionComponentInteractionPartnerSerializer(many=True, read_only=True)
    subsystem = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='name',
     )

    class Meta:
        model = APImodels.Reaction
        fields = ('id', 'is_reversible', 'modifiers', 'products', 'reactants', 'subsystem')


# =========================================================================================

class MetaboliteReactionSerializer(serializers.Serializer):
    # TODO remove or fix
    reaction_id = serializers.CharField()
    enzyme_role = serializers.CharField()
    subsystem = serializers.SerializerMethodField('get_subsystems')
    reactants = APIrcSerializer.ReactionComponentSerializer(many=True, read_only=True)
    products = APIrcSerializer.ReactionComponentSerializer(many=True, read_only=True)
    modifiers = APIrcSerializer.ReactionComponentSerializer(many=True, read_only=True)

    def get_subsystems(self, model):
        ss_ids = SubsystemReaction.objects.using(self.context.get('model')).filter(reaction=model.reaction_id).values_list('subsystem')
        return Subsystem.objects.using(self.context.get('model')).filter(id__in=ss_ids).values_list('name')


class ConnectedMetabolitesSerializer(serializers.Serializer):
    enzyme = APIrcSerializer.ReactionComponentSerializer(read_only=True)
    compartment = serializers.CharField()
    reactions = MetaboliteReactionSerializer(many=True)


class CompartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = APImodels.Compartment
        fields = ('name', 'name_id', 'letter_code', 'metabolite_count', 'enzyme_count', 'reaction_count', 'subsystem_count')


class GemBrowserTileCompartmentSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField('fetch_id')
    subsystems = serializers.SerializerMethodField('fetch_subsystems')
    class Meta:
        model = APImodels.Compartment
        fields = ('name', 'id', 'metabolite_count', 'enzyme_count', 'reaction_count', 'subsystem_count', 'subsystems')

    def fetch_subsystems(self, model):
        return model.subsystem.order_by('-reaction_count').values_list('name', flat=True)[:15]

    def fetch_id(self, model):
        return model.name_id


class CompartmentSvgSerializer(serializers.ModelSerializer):
    compartment = serializers.SlugRelatedField(slug_field='name_id', queryset=APImodels.Compartment.objects.all())
    subsystem = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='name',
     )
    class Meta:
        model = APImodels.CompartmentSvg
        fields = ('name', 'name_id', 'compartment', 'filename', 'letter_code', 'subsystem', 'metabolite_count',
         'unique_metabolite_count', 'enzyme_count', 'reaction_count', 'subsystem_count', 'sha')


class SubsystemLiteSerializer(serializers.ModelSerializer):
    compartment = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='name',
     )
    class Meta:
        model = APImodels.Subsystem
        fields = ('name', 'name_id', 'compartment')


class SubsystemSearchSerializer(serializers.ModelSerializer):
    compartment = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='name',
     )
    class Meta:
        model = APImodels.Subsystem
        fields = ('name', 'name_id', 'compartment', 'reaction_count', 'metabolite_count', 'enzyme_count')


class SubsystemSerializer(serializers.ModelSerializer):
    class Meta:
        model = APImodels.Subsystem
        fields = SubsystemLiteSerializer.Meta.fields + \
            ('system', 'external_id', 'external_link', 'metabolite_count', 'unique_metabolite_count', 'enzyme_count', 'reaction_count', 'compartment_count')


class GemBrowserTileSubsystemSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField('fetch_id')
    class Meta:
        model = APImodels.Subsystem
        fields = ('id', 'name', 'metabolite_count', 'enzyme_count', 'reaction_count', 'compartment_count')

    def fetch_id(self, model):
        return model.name_id


class HmrSubsystemSerializer(serializers.ModelSerializer):
    class Meta:
        model = APImodels.Subsystem
        fields = SubsystemLiteSerializer.Meta.fields + \
            ('system', 'external_id', 'external_link', 'metabolite_count', 'unique_metabolite_count', 'enzyme_count', 'reaction_count', 'compartment_count')


class SubsystemSvgSerializer(serializers.ModelSerializer):
    subsystem = serializers.SlugRelatedField(slug_field='name_id', queryset=APImodels.Compartment.objects.all())
    class Meta:
        model = APImodels.SubsystemSvg
        fields = ('name', 'name_id', 'subsystem', 'filename', 'metabolite_count', 'unique_metabolite_count', 'enzyme_count',
            'reaction_count', 'compartment_count', 'sha')


class GemBrowserTileSerializer(serializers.Serializer):
    compartments = GemBrowserTileCompartmentSerializer(many=True)
    subsystems = GemBrowserTileSubsystemSerializer(many=True)
    reactions = APIrcSerializer.GemBrowserTileReactionSerializer(many=True)
    metabolites = APIrcSerializer.GemBrowserTileMetaboliteSerializer(many=True)
    enzymes = APIrcSerializer.GemBrowserTileEnzymeSerializer(many=True)


# =======================================================================================
# models database


class GEModelFileSerializer(serializers.ModelSerializer):
    path = serializers.SerializerMethodField('get_file_path')
    class Meta:
        model = APImodels.GEModelFile
        fields = ('path', 'format')

    def get_file_path(self, model):
        if '/FTP' in model.path:
            return "%s%s" % ('http://ftp.icsb.chalmers.se/models', model.path.split('/FTP')[1])
        else:
            return model.path

class GEModelReferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = APImodels.GEModelReference
        fields = ('title', 'link', 'pubmed', 'year')

class GEModelSetSerializer(serializers.ModelSerializer):
    reference = GEModelReferenceSerializer(many=True, read_only=True)

    class Meta:
        model = APImodels.GEModelSet
        fields = ('name', 'description', 'reference')

class GEModelSampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = APImodels.GEModelSample
        fields = ('organism', 'organ_system', 'tissue', 'cell_type', 'cell_line')


class GEModelSerializer(serializers.ModelSerializer):
    gemodelset = GEModelSetSerializer(read_only=True)
    sample = GEModelSampleSerializer(read_only=True)
    files = GEModelFileSerializer(many=True, read_only=True)
    ref = GEModelReferenceSerializer(many=True, read_only=True)

    class Meta:
        model = APImodels.GEModel
        fields = ('id', 'gemodelset', 'sample', 'label', 'description', 'condition', 'reaction_count', 'metabolite_count', 'enzyme_count', 'files', 'ref', 'maintained', 'repo_name', 'last_update')


class GEModelListSerializer(serializers.ModelSerializer):
    set_name = serializers.SerializerMethodField('get_model_set_name')
    sample = GEModelSampleSerializer(read_only=True)
    year = serializers.SerializerMethodField('get_model_year')

    def get_model_set_name(self, model):
        return model.gemodelset.name

    def get_model_year(self, model):
        refs = model.ref
        if refs.all():
            return max([r.year for r in refs.all()])
        else:
            refs = model.gemodelset.reference
            if refs.all():
                return max([r.year for r in refs.all()])

    class Meta:
        model = APImodels.GEModel
        fields = ('id', 'set_name', 'sample', 'label', 'condition', 'reaction_count', 'metabolite_count', 'enzyme_count', 'maintained', 'year', 'last_update')


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = APImodels.Author
        fields = ('given_name', 'family_name', 'email', 'organization')

############################################################################################################


class GEMListSerializer(serializers.ModelSerializer):
    authors = AuthorSerializer(many=True)
    metabolite_count = serializers.SerializerMethodField('get_meta_count')
    enzyme_count = serializers.SerializerMethodField('get_enz_count')
    reaction_count = serializers.SerializerMethodField('get_react_count')
    details = serializers.SerializerMethodField('get_model_details')

    def get_model_details(self, model):
        return GEModelListSerializer(model.model).data

    class Meta:
        model = APImodels.GEM
        fields = ('short_name', 'name', 'database_name', 'authors', 'metabolite_count', 'enzyme_count', 'reaction_count', 'details')

    def get_meta_count(self, model):
        return model.model.metabolite_count

    def get_enz_count(self, model):
        return model.model.enzyme_count

    def get_react_count(self, model):
        return model.model.reaction_count


class GEMSerializer(serializers.ModelSerializer):
    authors = AuthorSerializer(many=True)
    model = GEModelSerializer(read_only=True)

    class Meta:
        model = APImodels.GEM
        fields = ('id', 'short_name', 'name', 'database_name', 'authors', 'model')
