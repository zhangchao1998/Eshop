from django.db import models

# Create your models here.
class Buyer(models.Model):
    username = models.CharField(max_length=32)
    password = models.CharField(max_length=64)
    email =models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=32, blank=True, null=True)
    photo = models.ImageField(upload_to="buyer/images", blank=True, null=True)
    vip = models.CharField(max_length=32, blank=True, null=True)


class Address(models.Model):
    address = models.TextField()
    phone = models.CharField(max_length=32)
    consignee = models.CharField(max_length=32)
    buyer = models.ForeignKey(Buyer, on_delete=True)


class EmailValid(models.Model):
    value = models.CharField(max_length=32)
    email_address = models.EmailField()
    times = models.DateTimeField()


class BuyCar(models.Model):
    goods_id = models.CharField(max_length=32)
    goods_name = models.CharField(max_length=32)
    goods_img = models.ImageField()
    goods_price = models.FloatField()
    goods_num = models.IntegerField()
    goods_user = models.ForeignKey(Buyer, on_delete=True)


class Order(models.Model):
    order_num = models.CharField(max_length=64)
    order_time = models.DateTimeField(auto_now=True)
    order_statue = models.CharField(max_length=32)
    total = models.FloatField()
    user = models.ForeignKey(Buyer, on_delete=True)
    order_address = models.ForeignKey(Address, on_delete=True)


class OrderGoods(models.Model):
    goods_id = models.IntegerField()
    goods_name = models.CharField(max_length=32)
    goods_price = models.FloatField()
    goods_num = models.IntegerField()
    goods_img = models.ImageField()
    order = models.ForeignKey(Order, on_delete=True)

