from django.urls import path, re_path
from Buyer.views import *

urlpatterns = [
    path("index/", index),
    path("register/", register),
    path("login/", login),
    path("logout/", logout),
    path("register_email/", register_email),
    path("sendEmail/", sendMessage),
    re_path("goods_details/(\d+)/", goods_details),
    re_path("carJump/(\d+)/", carJump),
    path("buyCar/", buyCar),
    re_path("delete_goods/(\d+)/",delete_goods),
    path("delete_all/", delete_all),
    path("add_address/", add_address),
    re_path("change_address/(\d+)/", change_address),
    re_path("address_del/(\d+)/", address_del),
    path("add_order/", add_order),
    path("buyer/", buyer),
    path("nameValid/", nameValid),
    path("buyer_change/", buyer_change),
    path("openshop/", openshop),
    path("orderList/", orderList),
    re_path("pay/(\d+)/",pay),
    re_path("order_delete/(\d+)/", order_delete),
]
