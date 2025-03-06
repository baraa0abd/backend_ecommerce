from django.db import models

class Products(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    brand = models.CharField(max_length=100)
    image = models.ImageField()

class Orders(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    quantity = models.IntegerField()

class Cart(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    quantity = models.IntegerField()

class Register(models.Model):
    username = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    password = models.CharField(max_length=100)

class Login(models.Model):
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)



class Review(models.Model):
    id = models.AutoField(primary_key=True)
    product_id = models.IntegerField()
    rating = models.IntegerField()
    comment = models.TextField(blank=True)

    def __str__(self):
        return f"Review for Product {self.product_id}"

class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name
