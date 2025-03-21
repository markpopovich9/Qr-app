from django.shortcuts import render
from user.models import Profile
from django.shortcuts import redirect
from django.core.handlers.wsgi import WSGIRequest
from  QR_cods.models import QR_CODE

# Перевіряе кількість QR-codes яких може створити користувач
ok = {
    'standart':10,
    'pro':100,
    'free':1
}

# Створюемо функцію view_subscriptions
def view_subscriptions(request:WSGIRequest):
    global ok
    subscription = 'none'
    if request.method == 'POST':
        if request.user.username:
            profile = Profile.objects.get(user=request.user)
            sub = request.POST.get('subscription')
            if not ';' in sub:
                profile.subcription = sub
                count = ok[sub]
                # Перебераемо всі QR-codes
                for qr in QR_CODE.objects.filter(profile = request.user,desktop = False):
                    if count > 0:
                        count -= 1
                        if qr.blocked:
                            # Розблоковуемо QR-code
                            qr.blocked = False
                            qr.save()
                    else:
                        # Блокуємо QR-code
                        qr.blocked = True
                        qr.save()
            else:
                # desktop_QR
                profile.desktop_QR += int(sub.split(';')[1])
            # Зберігаемо CVV та Номер карти  в базі данимх
            profile.card_number = request.POST.get('card')
            profile.CVV = request.POST.get('CVV')
            profile.save()
            
        else:
            return redirect('auth')
    if request.user.username:
        subscription = Profile.objects.get(user=request.user).subcription
    return render(request,template_name= "subscriptions/index.html", context={'subscription':subscription})

def redirection(request:WSGIRequest, qr_id):
    qr = QR_CODE.objects.get(id = qr_id)
    # В залежності яка в користувача підписка перевіряе чи потрібно блокувати QR-code
    if qr.blocked:
        return render(request, template_name='subscriptions/block.html')
    else:
        try:
            return redirect(qr.url)
        except:
            return render(request,'subscriptions/copy.html', {'url':qr.url})