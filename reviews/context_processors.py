from .views import COUPONS

def coupons_processor(request):
    return {'COUPONS_LIST': COUPONS}
