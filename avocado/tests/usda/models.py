from django.db import models

class FoodGroup(models.Model):
    code = models.CharField(primary_key=True, max_length=4)
    name = models.CharField('Name of Food Group', max_length=60)


class FoodDescription(models.Model):
    ndb_no = models.CharField('Nutrient Database Number', max_length=5, primary_key=True)
    food_group_code = models.ForeignKey(FoodGroup)
    long_desc = models.CharField('Long Description', max_length=200)
    short_desc = models.CharField('Short Description', max_length=60)
    common = models.CharField('Common Name', max_length=100, blank=True)
    manufacturer = models.CharField('Manufacturer', max_length=65, blank=True)
    survey = models.BooleanField('Participated in FNDDS', null=False)
    refuse_desc = models.CharField('Inedible Description', max_length=135, blank=True)
    refuse = models.IntegerField('Percent Refuse', blank=True)
    sci_name = models.CharField('Scientific Name', max_length=65, blank=True)
    n_factor = models.DecimalField('Nitrogen Converting Factor', max_digits=6, decimal_places=2, blank=True)
    pro_factor = models.DecimalField('Calories from protein factor', max_digits=6, decimal_places=2, blank=True)
    fat_factor = models.DecimalField('Calories from fat factor', max_digits=6, decimal_places=2, blank=True)
    cho_factor = models.DecimalField('Calories from carbs factor', max_digits=6, decimal_places=2, blank=True)


class NutrientField(models.Model):
    nutr_no = models.CharField('Nutrient Identifier', max_length=3, primary_key=True)
    units = models.CharField(max_length=7)
    tagname = models.CharField(max_length=20, blank=True)
    nutr_desc = models.CharField('Nutrient Name', max_length=60)
    num_dec = models.IntegerField('number of decimal places')
    sr_order = models.IntegerField()


class NutrientData(models.Model):
    ndb_no = models.ForeignKey(FoodDescription)
    nutr_no = models.ForeignKey(NutrientField)
    nutr_val = models.DecimalField('Amount in 100 grams', max_digits=13, decimal_places=3)
    num_data_pts = models.IntegerField()
    std_error = models.DecimalField(max_digits=11, decimal_places=3, null=True)
    source_code = models.CharField(max_length=2)
    deriv_code = models.CharField(max_length=4, blank=True)
    ref_ndb_no = models.CharField(max_length=5, blank=True)
    add_nutr_mark = models.NullBooleanField('Vitamin added for enrichment', blank=True)
    num_studies = models.IntegerField(blank=True)
    min_val = models.DecimalField(max_digits=13, decimal_places=3, blank=True)
    max_val = models.DecimalField(max_digits=13, decimal_places=3, blank=True)
    df = models.IntegerField('Degrees of freedom', blank=True)
    low_eb = models.DecimalField('Lower 95% \error bound', max_digits=13, decimal_places=3, blank=True)
    up_eb = models.DecimalField('Upper 95% \error bound', max_digits=13, decimal_places=3, blank=True)
    stat_comment = models.CommaSeparatedIntegerField(max_length=10, blank=True)

    class Meta(object):
        unique_together = ('ndb_no', 'nutr_no')


# Other Models that can be implemented later

# class Weight(models.Model):
#     ndb_no = models.ForeignKey(FoodDescription)
#     seq = models.CharField('Sequence Number', max_length=2)
#     amount = models.DecimalField('Unit Modifier', max_digits=8, decimal_places=3)
#     description = models.CharField(max_length=80)
#     gram_weight = models.DecimalField(max_digits=8, decimal_places=1)
#     num_data_pts = models.IntegerField(blank=True)
#     std_dev = models.DecimalField(max_digits=10, decimal_places=3, blank=True)
#
#     class Meta(object):
#         unique_together = ('ndb_no', 'seq')
#
# class Source(models.Model):
#     code = models.CharField(max_length=2, primary_key=True)
#     description = models.CharField(max_length=60)
#
#
# class DataSource(models.Model):
#     data_id = models.CharField(max_length=6, primary_key=True)
#     authors = models.CharField(max_length=255, blank=True)
#     title = models.CharField(max_length=255)
#     year = models.DateField(blank=True)
#     journal = models.CharField(max_length=135, blank=True)
#     vol_city = models.CharField(max_length=16, blank=True)
#     issue_state = models.CharField(max_length=5, blank=True)
#     start_page = models.CharField(max_length=5, blank=True)
#     end_page = models.CharField(max_length=5, blank=True)
#
#
# class SourceLink(models.Model):
#     unique_together = ('ndb_no', 'nutr_no', 'data_id')
#     ndb_no = models.ForeignKey(FoodDescription)
#     nutr_no = models.ForeignKey(NutrientData)
#     data_id = models.ForeignKey(DataSource)
#
#
# class Derivation(models.Model):
#     code = models.CharField(max_length=4, primary_key=True)
#     description = models.CharField(max_length=120)
#
#
# class Footnote(models.Model):
#     ndb_no = models.ForeignKey(FoodDescription)
#     seq_num = models.CharField(max_length=4)
#     f_type = models.CharField(max_length=1)
#     nutr_no = models.ForeignKey(NutrientField, null=True, blank=True, default=None)
#     text = models.CharField(max_length=200)
