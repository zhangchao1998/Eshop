from django.urls import path, re_path
from Seller.views import *

urlpatterns = [
    re_path('^$', index),
    path('index/', index),
    re_path('goods_list/(\d+)/', goods_list),
    path('goods_add/', goods_add),
    path('login/', login),
    path('logout/', logout, name="logout"),
    re_path('goods/(\d+)/', goods),
    re_path('goods_change/(\d+)/', goods_change),
    re_path('goods_del/(\d+)/', goods_del),
]
