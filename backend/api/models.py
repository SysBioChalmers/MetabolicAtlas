from django.db import models

class MetabolicModel(models.Model):
    short_name = models.CharField(max_length=255, blank=False)
    name = models.CharField(max_length=255, blank=False)
    #reactions = models.ManyToManyField(Reaction, through='ModelReaction')

    class Meta:
        db_table = "metabolic_model"

class Author(models.Model):
    given_name = models.CharField(max_length=255, blank=False)
    family_name = models.CharField(max_length=255, blank=False)
    email = models.CharField(max_length=255, blank=False)
    organization = models.CharField(max_length=255, blank=False)
    models = models.ManyToManyField(MetabolicModel, through='ModelAuthor')

    class Meta:
        db_table = "author"

class ModelAuthor(models.Model):
    model = models.ForeignKey(MetabolicModel, on_delete=models.CASCADE)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)

    class Meta:
        db_table = "model_authors"

class Reaction(models.Model):
    pass

class ReactionComponent(models.Model):
    pass

class ReactionComponentAnnotation(models.Model):
    pass

class Compartment(models.Model):
    pass

class ExpressionData(models.Model):
    pass

class Metabolite(models.Model):
    pass

class Enzyme(models.Model):
    pass

