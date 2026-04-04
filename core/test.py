from django.db.models import Count
from backend.models import HoKhau

ho_list = (HoKhau.objects
           .annotate(so_nk=Count('nhan_khaus'))
           .order_by('-so_nk')[:50])

