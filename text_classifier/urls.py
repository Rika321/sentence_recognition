from django.urls import path

from . import views

app_name = 'text_classifier'


urlpatterns = [
    path('', views.index, name='index'),
    path('train_mode/', views.train_mode, name='train_mode'),
    path('eval_mode/', views.eval_mode, name='eval_mode'),
    path('simple_upload/', views.simple_upload, name='simple_upload'),
    path('simple_add/', views.simple_add, name = 'simple_add'),
    path('simple_train/', views.simple_train, name = 'simple_train'),
    path('simple_eval/', views.simple_eval, name = 'simple_eval'),
    path('results/', views.results, name='results'),
    path('explain', views.explain, name='explain'),
    path('plot', views.plot, name='plot'),
    path('update', views.update, name='update'),
    path('apply_model', views.apply_model, name='apply_model'),
    #path('random', views.random, name='random'),

]
