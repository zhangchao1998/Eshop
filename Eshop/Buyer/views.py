from django.shortcuts import render, HttpResponseRedirect
from Buyer.models import *
from Seller.models import *
from Seller.views import setPassword
from django.core.mail import EmailMultiAlternatives
from django.http import JsonResponse
from Eshop.settings import MEDIA_ROOT
from alipay import AliPay
import random
import datetime
import time
import os


def cookieValid(fun):
    def inner(request, *args, **kwargs):
        cookie = request.COOKIES
        user = Buyer.objects.filter(username=cookie.get("username"))
        session = request.session.get("username")
        if user and session == user.first().username:
            return fun(request, *args, **kwargs)
        else:
            return HttpResponseRedirect("/buyer/login/")
    return inner


@cookieValid
def index(request):
    data = []
    goods = Goods.objects.all()
    for one_goods in goods:
        data.append(
            {"img": one_goods.image_set.first().img_address, "name": one_goods.goods_name, "price": one_goods.goods_now_price, "id": one_goods.id}
        )
    return render(request, "buyer/index.html", {"data": data})


def register(request):
    if request.method == "POST" and request.POST:
        username = request.POST.get("username")
        password = setPassword(request.POST.get("userpass"))
        buyer = Buyer()
        buyer.username = username
        buyer.password = password
        buyer.save()
        return HttpResponseRedirect("/buyer/login/")
    return render(request, "buyer/register.html")


def login(request):
    data = {"data": ""}
    if request.method == "POST" and request.POST:
        username = request.POST.get("username")
        user = Buyer.objects.filter(username = username).first()
        if user:
            password = setPassword(request.POST.get("userpass"))
            db_password = user.password
            if password == db_password:
                response = HttpResponseRedirect("/buyer/index/")
                response.set_cookie("username", user.username)
                response.set_cookie("userid", user.id)
                request.session["username"] = user.username
                return response
            else:
                data["data"] = "密码错误"
        else:
            data["data"] = "用户不存在"
    return render(request, "buyer/login.html", {"data": data})


def logout(request):
    response = HttpResponseRedirect("/buyer/login/")
    response.delete_cookie("username")
    response.delete_cookie("userid")
    del request.session["username"]
    return response


def getRandom():
    result = str(random.randint(100000, 999999))
    return result


def sendMessage(request):
    result = {"staue": "error","data": ""}
    if request.method == "GET" and request.GET:
        recver = request.GET.get("email")
        try:
            subject = "验证码"
            text_content = "商城验证码"
            value = getRandom()
            html_content = "<p>您的验证码是：{}</p>".format(value)
            message = EmailMultiAlternatives(subject,text_content,"zhang_my163email@163.com", [recver])
            message.attach_alternative(html_content,"text/html")
            message.send()
        except Exception as e:
            result["data"] = str(e)
        else:
            result["staue"] = "success"
            result["data"] = "success"
            email = EmailValid()
            email.value = value
            email.email_address = recver
            email.times = datetime.datetime.now()
            email.save()
        finally:
            return JsonResponse(result)


def register_email(request):
    result = {"statu": "error", "data": ""}
    if request.method == "POST" and request.POST:
        username = request.POST.get("email")
        code = request.POST.get("code")
        userpass = request.POST.get("userpass")
        email = EmailValid.objects.filter(email_address=username).first()
        if email:
            if code == email.value:
                now = time.mktime(datetime.datetime.now().timetuple())
                db_now = time.mktime(email.times.timetuple())
                if now - db_now >= 86400:
                    result["data"] = "验证码过期"
                    email.delete()
                else:
                    buyer = Buyer()
                    buyer.username = username
                    buyer.email = username
                    buyer.password = setPassword(userpass)
                    buyer.save()
                    result["statu"] = "success"
                    result["data"] = "注册成功"
                    email.delete()
                    return HttpResponseRedirect("/buyer/login/")
            else:
                result["data"] = "验证码错误"
        else:
            result["data"] = "请重新获取验证码"
    return render(request, "buyer/register_email.html", locals())


@cookieValid
def goods_details(request, id):
    goods = Goods.objects.get(id=int(id))
    img_address = str(goods.image_set.first().img_address)
    all_img = []
    for i in goods.image_set.all():
        all_img.append(str(i.img_address))
    address = goods.seller.address
    all_goods = goods.seller.goods_set.all()
    goods_list = []
    for one_goods in all_goods:
        if one_goods.id != int(id):
            goods_list.append({"a_goods": one_goods, "img": str(one_goods.image_set.all().first().img_address)})
    return render(request, "buyer/goods_details.html", locals())


@cookieValid
def carJump(request, id):
    goods = Goods.objects.get(id = int(id))
    img_address = str(goods.image_set.first().img_address)
    if request.method == "POST" and request.POST:
        number = int(request.POST.get("count"))
        money = goods.goods_now_price*number
        buycar = BuyCar.objects.filter(goods_user=Buyer.objects.get(id = int(request.COOKIES.get("userid"))),goods_id=goods.id).first()
        if not buycar:
            buycar = BuyCar()
            buycar.goods_id = goods.id
            buycar.goods_name = goods.goods_name
            buycar.goods_price = goods.goods_now_price
            buycar.goods_num = number
            buycar.goods_img = goods.image_set.first().img_address
            buycar.goods_user = Buyer.objects.get(id = request.COOKIES.get("userid"))
        else:
            buycar.goods_num += number
        buycar.save()
    return render(request, "buyer/carJump.html", locals())


@cookieValid
def buyCar(request):
    goods_list = Buyer.objects.get(id = int(request.COOKIES.get("userid"))).buycar_set.all()
    address_list = Buyer.objects.get(id = int(request.COOKIES.get("userid"))).address_set.all()
    goodsList = []
    all_money = 0
    for goods in goods_list:
        goodsList.append({"money": int(goods.goods_num)*float(goods.goods_price), "goods": goods, "img": str(goods.goods_img)})
        all_money += int(goods.goods_num)*float(goods.goods_price)
    return render(request, "buyer/buyCar.html", locals())


@cookieValid
def delete_goods(request, goods_id):
    id = request.COOKIES.get("userid")
    goods = BuyCar.objects.filter(goods_user = Buyer.objects.get(id = int(id)),goods_id=int(goods_id))
    goods.delete()
    return HttpResponseRedirect("/buyer/buyCar/")


@cookieValid
def delete_all(request):
    id = request.COOKIES.get("userid")
    goods = Buyer.objects.get(id = int(id)).buycar_set.all()
    goods.delete()
    return HttpResponseRedirect("/buyer/buyCar/")


@cookieValid
def add_address(request):
    if request.method == "POST" and request.POST:
        buyer_id = request.COOKIES.get("userid")
        addr = Address()
        addr.consignee = request.POST.get("name")
        addr.phone = request.POST.get("phone")
        addr.address = request.POST.get("address")
        addr.buyer = Buyer.objects.get(id = int(buyer_id))
        addr.save()
        return HttpResponseRedirect("/buyer/buyer/")
    return render(request, "buyer/add_address.html")


@cookieValid
def change_address(request,id):
    address = Address.objects.get(id = int(id))
    if request.method == "POST" and request.POST:
        buyer_id = request.COOKIES.get("userid")
        address.consignee = request.POST.get("name")
        address.phone = request.POST.get("phone")
        address.address = request.POST.get("address")
        address.buyer = Buyer.objects.get(id=int(buyer_id))
        address.save()
        return HttpResponseRedirect("/buyer/buyer/")
    return render(request, "buyer/add_address.html", locals())


@cookieValid
def address_del(request, id):
    address = Address.objects.get(id = int(id))
    address.delete()
    return HttpResponseRedirect("/buyer/buyer/")


@cookieValid
def add_order(request):
    buyer_id = request.COOKIES.get("userid")
    goods_list = []
    if request.method == "POST" and request.POST:
        requestData = request.POST
        addr = requestData.get("address")
        pay_method = requestData.get("pay_Method")
        all_money = 0
        for key, value in requestData.items():
            if key.startswith("on"):
                one_goods = BuyCar.objects.get(id = int(value))
                money = float(one_goods.goods_num)*float(one_goods.goods_price)
                all_money += money
                goods_list.append({"money": money, "one_goods": one_goods, "img": str(one_goods.goods_img)})
        Addr = Address.objects.get(id = int(addr))
        order = Order()
        order.order_num = str(int(time.time())) + str(random.randint(10000, 99999)) + str(buyer_id)
        order.order_time = datetime.datetime.now()
        order.order_statue = 1
        order.total = all_money
        order.user = Buyer.objects.get(id = int(buyer_id))
        order.order_address = Addr
        order.save()
        for goods in goods_list:
            g = goods.get("one_goods")
            g_o = OrderGoods()
            g_o.goods_id = g.id
            g_o.goods_name = g.goods_name
            g_o.goods_price = g.goods_price
            g_o.goods_num = g.goods_num
            g_o.goods_img = g.goods_img
            g_o.order = order
            g_o.save()
        return render(request, "buyer/enterOrder.html", locals())
    else:
        return HttpResponseRedirect("/buyer/buyCar/")


@cookieValid
def buyer(request):
    buyer_id = request.COOKIES.get("userid")
    buyer = Buyer.objects.get(id = int(buyer_id))
    img = str(buyer.photo)
    addressList = Buyer.objects.get(id=int(buyer_id)).address_set.all()
    return render(request, "buyer/buyer.html", locals())



def nameValid(request):
    if request.method == "GET" and request.GET:
        oldname = Buyer.objects.get(id = int(request.COOKIES.get("userid"))).username
        username = request.GET.get("username")
        user = Buyer.objects.filter(username=username)
        if user:
            if username == oldname:
                return JsonResponse({"result": "T"})
            else:
                return JsonResponse({"result": "F"})
        else:
            return JsonResponse({"result": "T"})


@cookieValid
def buyer_change(request):
    buyer_id = request.COOKIES.get("userid")
    buyer = Buyer.objects.get(id = int(buyer_id))
    if request.method == "POST" and request.POST:
        buyer.username = request.POST.get("username")
        buyer.phone = request.POST.get("phone")
        buyer.photo = "buyer/images/{0}.{1}".format(request.POST.get("username"), request.FILES.get("photo").name.rsplit(".",1)[1])
        path = os.path.join(MEDIA_ROOT, "buyer/images/{0}.{1}".format(request.POST.get("username"), request.FILES.get("photo").name.rsplit(".",1)[1]))
        with open(path, "wb") as f:
            for j in request.FILES.get("photo").chunks(chunk_size=1024):
                f.write(j)
        buyer.save()
        return HttpResponseRedirect("/buyer/buyer/")
    return render(request, "buyer/buyer_change.html", locals())


@cookieValid
def openshop(request):
    result = {"statu": "error", "data": ""}
    if request.method == "POST" and request.POST:
        email = EmailValid.objects.filter(email_address=request.POST.get("email")).first()
        code = request.POST.get("code")
        if email:
            if code == email.value:
                now = time.mktime(datetime.datetime.now().timetuple())
                db_now = time.mktime(email.times.timetuple())
                if now - db_now >= 86400:
                    result["data"] = "验证码过期"
                    email.delete()
                else:
                    seller = Seller()
                    seller.username = request.POST.get("username")
                    seller.password = setPassword(request.POST.get("password"))
                    seller.nickname = request.POST.get("nickname")
                    seller.phone = request.POST.get("phone")
                    seller.address = request.POST.get("address")
                    seller.email = request.POST.get("email")
                    seller.id_number = request.POST.get("id_number")
                    seller.photo = "seller/images/{0}.{1}".format(request.POST.get("email"), request.FILES.get("photo").name.rsplit(".", 1)[1])
                    path = os.path.join(MEDIA_ROOT, "seller/images/{0}.{1}".format(request.POST.get("email"), request.FILES.get("photo").name.rsplit(".", 1)[1]))
                    with open(path, "wb") as f:
                        for j in request.FILES.get("photo").chunks(chunk_size=1024):
                            f.write(j)
                    seller.save()
                    result["statu"] = "success"
                    result["data"] = "注册成功"
                    email.delete()
                    return HttpResponseRedirect("/seller/login/")
            else:
                result["data"] = "验证码错误"
        else:
            result["data"] = "请重新获取验证码"
    return render(request, "buyer/free.html", locals())


def pay(request,id):
    order = Order.objects.get(id = int(id))
    number = order.order_num
    money = order.total
    alipay_public_key_string = '''-----BEGIN PUBLIC KEY-----
        MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEApHXnbFSfgcPQayYQBRvvIrjaFdlqOck/s7N6ffA/Y7RFYNGW9pwwqEYn2qfl4sqZA59mJ4mxC7xKmqaG4gv6PUpcylcpFm6jaVHMXNRLorwK4Hx9d/1i1SWOP26+RwEgBvSce9OsUBpNo5KkAfwQA92+LQjnwNRsVLdgq0gyQrdA+U1QyGCEzlgZbJ3Z476JOhp0EFvY5xW/sI0hIstenhtrtIoBChI6GrRMy1/nT4jHpuz1e1xYj3FMOONYbGG8lKKx3MIMjFAXOjdYwU15rSqwk2o16H6ATQVLaIwmSA7UWAPOPKr62PkN/oWDRdnW4nyPu9HJsbVgZY4OOb2dkwIDAQAB
    -----END PUBLIC KEY-----'''

    app_private_key_string = '''-----BEGIN RSA PRIVATE KEY-----
        MIIEpQIBAAKCAQEApHXnbFSfgcPQayYQBRvvIrjaFdlqOck/s7N6ffA/Y7RFYNGW9pwwqEYn2qfl4sqZA59mJ4mxC7xKmqaG4gv6PUpcylcpFm6jaVHMXNRLorwK4Hx9d/1i1SWOP26+RwEgBvSce9OsUBpNo5KkAfwQA92+LQjnwNRsVLdgq0gyQrdA+U1QyGCEzlgZbJ3Z476JOhp0EFvY5xW/sI0hIstenhtrtIoBChI6GrRMy1/nT4jHpuz1e1xYj3FMOONYbGG8lKKx3MIMjFAXOjdYwU15rSqwk2o16H6ATQVLaIwmSA7UWAPOPKr62PkN/oWDRdnW4nyPu9HJsbVgZY4OOb2dkwIDAQABAoIBAQCBHNtJrgnnu04VwLUU/cA41zzHqH9/zGJJdx80Xfe2E+Hfx8un4ilFAobpX6TX7sxADtUJN00adIFxdkkwj8yub4H3jIQCS2vZFFHHkxeqM8yqPrHWEMSVp71MSWnynoyBSWrMv/pojK3lPAusTzJXhq919abUOTCvNaQb9DsZKjiMxA5CcbTvpEHsFZFO62MkUqzkufcdCBS4HwdGiilIHKqZcYHijOAN4T6FtRCydqYAkCib3KJAN3v5Q2YlPCEK+jywghmTrpYOl+ko/sPwteOYAH2SWxXN2exgtzUWjBXBQOkL4OyYyyzJhEUQKxBzmM11BVgk1+Mhylr8J11RAoGBANl09HXUm4BSBrYnOGrAIUSLR3thN21FrooAHyBzrJucJGMSRu4LJSpOEeELtVu5Bq5otElu0GcJr2+pLJNUp8r0xWls/9ZNBDEhNgvJfVc39YT76oMtN0vFAQzhwZxZM4+ExwnMv7Otsn8WnLy5k0YavbsMqqC1ibmcDtDz47UZAoGBAMGcQcDfYTW8x+s7m1U70nolsn/hHjOj1dQkMYWt4lBg1cxQYgQQT96KxBBfNMVHB/XFWR9DmwOVrjeIG/8hRzR3XI5Ba/6AaprGqfXGo7PnBowdOQvx6XqX2a6HfWSaLkaBVecRhuXRVSsvsSzdOmg0szUfTyNmxxl9y7NchLGLAoGBAKOdSen2Q+Hy1bXsIJjBYsaN/QSqCugey8pteP4TysVyYDZipBerLxV7lBw9kQEoYAyOH0g5JnjAYs2i/jUENxOPw5ElQAFgBU1p7Z5Exhf/tK2QVczJEpfh7H5ixif7Pb44awHGml54zJquytN81YCj0imQyDkPHkcXUlaJisTRAoGBAMDzm0w+00Cc7ZjwBLSDNBZrr2Nm1ZSdeSM9FuWlD+EPQMOocKagIxkkrpWqbIsXaUV08ocH91sxNzk8urofTjlpo6JabOhsztGFoCjDWK6YVZwaG5pd81QsNdOMUFmMlwXJK/VnMEulvf2WQDr4F5d2vgr5MwOTEGXFStdsIwpVAoGAWJSczDvZxtLf/XX+ptNTphUcZ+UJpebxFuFnbu9qfaRojZy55i5wkMyzQH3ZaZIVHjg7vbCvqZWhZPXWSGnK1+wLVW2h5ZY57Li0u5n+YobtLu8Y+hl8QYsrYgHA3s1Lyv8rDNYLJeCJnbYdAgsmmFCbPtYm7eH4zzl+kS3A9DY=
    -----END RSA PRIVATE KEY-----'''

    alipay = AliPay(
        appid="2016092400586029",  # 支付宝app的id
        app_notify_url=None,  # 会掉视图
        app_private_key_string=app_private_key_string,  # 私钥字符
        alipay_public_key_string=alipay_public_key_string,  # 公钥字符
        sign_type="RSA2",  # 加密方法
    )

    order_string = alipay.api_alipay_trade_page_pay(
        out_trade_no=str(number),
        total_amount=str(money),  # 将Decimal类型转换为字符串交给支付宝
        subject="商贸商城",
        return_url="http://127.0.0.1:8000/buyer/orderList/",
        notify_url=None  # 可选, 不填则使用默认notify url
    )
    return HttpResponseRedirect("https://openapi.alipaydev.com/gateway.do?" + order_string)



def orderList(request):
    buyer_id = request.COOKIES.get("userid")
    buyer = Buyer.objects.get(id = int(buyer_id))
    order = buyer.order_set.all()
    all_order = []
    for one_order in order:
        all_goods = one_order.ordergoods_set.all()
        one = {"order": one_order, "id": int(one_order.id)}
        three = []
        for one_goods in all_goods:
            img = str(one_goods.goods_img)
            two = {"goods": one_goods, "img": img}
            three.append(two)
        one["goods"] = three
        all_order.append(one)
    return render(request, "buyer/orderList.html", locals())


def order_delete(request,id):
    order = Order.objects.get(id = int(id))
    ordergoods = order.ordergoods_set.all()
    ordergoods.delete()
    order.delete()
    return HttpResponseRedirect("/buyer/orderList/")

