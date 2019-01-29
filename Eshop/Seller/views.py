from django.shortcuts import render, render_to_response
from django.http import HttpResponseRedirect
from Seller.models import *
from Eshop.settings import MEDIA_ROOT
import datetime
import hashlib
import os


def setPassword(password):
    md5 = hashlib.md5()
    md5.update(password.encode())
    result = md5.hexdigest()
    return result


def cookieValid(fun):
    def inner(request, *args, **kwargs):
        cookie = request.COOKIES
        user = Seller.objects.filter(email=cookie.get("email"))
        session = request.session.get("nickname")
        if user and session == user.first().nickname:
            return fun(request, *args, **kwargs)
        else:
            return HttpResponseRedirect("/seller/login/")
    return inner


@cookieValid
def index(request):
    return render(request, "seller/index.html")


@cookieValid
def goods_list(request, page):
    id = request.COOKIES.get("id")
    page = int(page)
    start_num = (page - 1) * 10
    end_num = page * 10
    goodsList = Goods.objects.filter(seller = Seller.objects.get(id = int(id)))
    goods_count = goodsList.count()
    pageEnd = goods_count / 10
    if pageEnd != int(pageEnd):
        pageEnd += 1
    pageEnd = int(pageEnd)
    if page <= 3:
        page_range = range(1, pageEnd+1)
    elif page >= pageEnd - 2:
        if pageEnd-4 < 0:
            page_range = range(1, pageEnd+1)
        else:
            page_range = range(pageEnd - 4, pageEnd + 1)
    else:
        page_range = range(page - 2, page + 3)
    goodsList = goodsList[start_num:end_num]
    if not goodsList:
        goodsList = goodsList[0:10]
    return render(request, "seller/goods_list.html", locals())
    # return render(request, "seller/goods_list.html")


@cookieValid
def goods_add(request):
    all_type = Types.objects.all()
    if request.method == "POST" and request.POST:
        goods_id = request.POST.get("goods_num")
        goods_name = request.POST.get("goods_name")
        goods_oprice = request.POST.get("goods_oprice")
        goods_xprice = request.POST.get("goods_xprice")
        goods_count = request.POST.get("goods_count")
        goods_description = request.POST.get("goods_description")
        goods_content = request.POST.get("goods_content")
        goods_types = request.POST.get("goods_type")
        goods_time = datetime.datetime.now()
        img_file = request.FILES.getlist("goods_photo")

        g = Goods()
        g.goods_id = goods_id
        g.goods_name = goods_name
        g.goods_price = goods_oprice
        g.goods_now_price = goods_xprice
        g.goods_num = goods_count
        g.goods_description = goods_description
        g.goods_content = goods_content
        g.goods_show_time = goods_time
        g.types = Types.objects.get(id=int(goods_types))
        id = request.COOKIES.get("id")
        if id:
            g.seller = Seller.objects.get(id = int(id))
        else:
            return HttpResponseRedirect("/seller/login/")
        g.save()


        n = 1
        for one_img in img_file:
            i = Image()
            i.img_address = "seller/images/{0}_{1}.{2}".format(goods_name, str(n), one_img.name.rsplit(".",1)[1])
            i.img_label = "{}_{}".format(goods_name, str(n))
            i.img_description = "就是图片描述"
            i.goods = g
            path = os.path.join(MEDIA_ROOT,"seller/images/{0}_{1}.{2}".format(goods_name, str(n), one_img.name.rsplit(".",1)[1]) )
            with open(path, "wb") as f:
                for j in one_img.chunks(chunk_size=1024):
                    f.write(j)
            i.save()
            n += 1
    return render(request, "seller/goods_add.html", locals())


def login(request):
    result = {"error": ""}
    if request.method == "POST" and request.POST:
        login_valid = request.POST.get("login_valid")
        cookie_one = request.COOKIES.get("cookie_one")
        if login_valid == "login_valid" and cookie_one == "just is a cookie":
            username = request.POST.get("username")
            user = Seller.objects.filter(username = username).first()
            if user:
                if user.password == setPassword(request.POST.get("password")):
                    response = HttpResponseRedirect("/seller/")
                    response.set_cookie("email", user.email)
                    response.set_cookie("id", user.id)
                    request.session["nickname"] = user.nickname
                    return response
                else:
                    result["error"] = "密码错误"
            else:
                result["error"] = "用户不存在"
        else:
            result["error"] = "请使用正确的接口登录"
    response = render(request, "seller/login.html", {"result": result})
    response.set_cookie("cookie_one", "just is a cookie")
    return response


def logout(request):
    email = request.COOKIES.get("email")
    if email:
        response = HttpResponseRedirect("/seller/login/")
        response.delete_cookie("email")
        del request.session["nickname"]
        return response
    else:
        return HttpResponseRedirect("/seller/login/")


@cookieValid
def goods(request, number):
    number = int(number)
    one_goods = Goods.objects.get(id=number)
    photos = Image.objects.filter(goods_id=one_goods.id)
    return render(request, "seller/goods.html", locals())


@cookieValid
def goods_change(request,id):
    key = "修改"
    goods = Goods.objects.get(id = int(id))
    goodsType = goods.types.label
    if request.method == "POST" and request.POST:
        goods_id = request.POST.get("goods_num")
        goods_name = request.POST.get("goods_name")
        goods_oprice = request.POST.get("goods_oprice")
        goods_xprice = request.POST.get("goods_xprice")
        goods_count = request.POST.get("goods_count")
        goods_description = request.POST.get("goods_description")
        goods_content = request.POST.get("goods_content")
        goods_types = request.POST.get("goods_type")
        goods_time = datetime.datetime.now()
        img_file = request.FILES.getlist("goods_photo")

        g = goods
        g.goods_id = goods_id
        g.goods_name = goods_name
        g.goods_price = goods_oprice
        g.goods_now_price = goods_xprice
        g.goods_num = goods_count
        g.goods_description = goods_description
        g.goods_content = goods_content
        g.goods_show_time = goods_time
        g.types = Types.objects.get(label=goods_types)
        id = request.COOKIES.get("id")
        if id:
            g.seller = Seller.objects.get(id=int(id))
        else:
            return HttpResponseRedirect("/seller/login/")
        g.save()


        imgs = goods.image_set.all()
        imgs.delete()
        n = 1
        for one_img in img_file:
            i = Image()
            i.img_address = "seller/images/{0}_{1}.{2}".format(goods_name, str(n), one_img.name.rsplit(".", 1)[1])
            i.img_label = "{}_{}".format(goods_name, str(n))
            i.img_description = "就是图片描述"
            i.goods = g
            path = os.path.join(MEDIA_ROOT, "seller/images/{0}_{1}.{2}".format(goods_name, str(n), one_img.name.rsplit(".", 1)[1]))
            with open(path, "wb") as f:
                for j in one_img.chunks(chunk_size=1024):
                    f.write(j)
            i.save()
            n += 1
        return HttpResponseRedirect("/seller/goods_list/1/")
    return render(request, "seller/goods_add.html", locals())


def goods_del(request, id):
    goods = Goods.objects.get(id = int(id))
    images = goods.image_set.all()
    for image in images:
        os.remove(os.path.join(MEDIA_ROOT, str(image.img_address)))
    images.delete()
    goods.delete()
    return HttpResponseRedirect("/seller/goods_list/1/")


