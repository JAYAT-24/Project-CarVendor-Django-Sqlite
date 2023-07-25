# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Car(models.Model):
    car_id = models.AutoField(primary_key=True, blank=True, null=True)
    manufacturer = models.CharField()
    model = models.CharField()
    year = models.IntegerField()

    class Meta:
        db_table = 'Car'

    def addCar(manufacturer, model, year):
        car = Car(manufacturer = manufacturer, model = model, year = year)
        car.save()

    def deleteCar(self):
        self.delete()



class Carattributes(models.Model):
    car = models.ForeignKey(Car, models.DO_NOTHING, blank=True, null=True)
    mileage = models.FloatField()  # This field type is a guess.
    engine = models.CharField()
    transmission = models.CharField()
    drivetrain = models.CharField()
    fuel_type = models.CharField()
    mpg = models.CharField()
    exterior_color = models.CharField()
    interior_color = models.CharField()

    class Meta:
        db_table = 'CarAttributes'


class Carhistory(models.Model):
    car = models.ForeignKey(Car, models.DO_NOTHING, blank=True, null=True)
    accidents_or_damage = models.BooleanField()
    one_owner = models.BooleanField()
    personal_use_only = models.BooleanField()

    class Meta:
        db_table = 'CarHistory'


class Dealer(models.Model):
    car = models.ForeignKey(Car, models.DO_NOTHING, blank=True, null=True)
    seller_name = models.CharField()
    seller_rating = models.FloatField()  # This field type is a guess.
    driver_rating = models.FloatField()  # This field type is a guess.
    driver_reviews_num = models.FloatField()  # This field type is a guess.

    class Meta:
        db_table = 'Dealer'


class Price(models.Model):
    car = models.ForeignKey(Car, models.DO_NOTHING, blank=True, null=True)
    price_drop = models.FloatField()  # This field type is a guess.
    price = models.FloatField()  # This field type is a guess.

    class Meta:
        db_table = 'Price'
