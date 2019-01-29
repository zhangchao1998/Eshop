from django import forms
from Seller.models import Types, Seller


class GoodsForm(forms.Form):
    goods_id = forms.CharField(max_length=32)
    goods_name = forms.CharField(max_length=32)
    goods_price = forms.FloatField()  # 原价
    goods_now_price = forms.FloatField()  # 当前价格
    goods_num = forms.IntegerField()  # 库存
    goods_description = forms.TextInput()  # 描述
    goods_content = forms.TextInput()  # 详情
    goods_show_time = forms.DateField()  # 发布时间
    types = forms.CharField()  # 一个分类有多个商品
    seller = forms.CharField()  # 一家店铺有多个商品
