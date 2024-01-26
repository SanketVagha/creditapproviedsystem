from django.urls import path
# from django.urls import path, include
# from rest_framework import routers
from creditapi import views
# from creditapi.views import register


# router = routers.DefaultRouter()

# router.register(r'register', register)

urlpatterns = [
    path('register', views.register),
    path('check-eligibility', views.checkeligibility)
    # path('', include(router.urls))

]
