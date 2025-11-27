import base64
import calendar
import io
from django.db.models import Value, DecimalField
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate,login
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Gasto, Ingreso,Categoria
from .mongo_models import Calificaciones
from django.db.models import Sum, Count,Q

from django.db.models.functions import Coalesce

from datetime import datetime, timedelta,date
import matplotlib.pyplot as plt
from django.utils import timezone

# Create your views here.

def inicio_sesion(request):
    if request.method == 'POST':
        usuario = request.POST.get('usuario')
        clave = request.POST.get('password')


        user = authenticate(username=usuario, password=clave)
        print(usuario,clave)
        if user:
             login(request,user)
             return redirect('finanzas')
        else:
            messages.error(request, "El Usuario o la contraseña son incorrectos")
            return render(request,"inicioSesion.html")
    return render(request, "inicioSesion.html" )

    


def registrar_usuario(request):
    if request.method == 'POST':
        usuario = request.POST.get('usuario')
        clave = request.POST.get('password')
        repetirClave = request.POST.get('repetPassword')
        nombres = request.POST.get('nombres')
        apellidos = request.POST.get('apellidos')
        
        storage = messages.get_messages(request)
        storage.used = True

        print(usuario,clave,repetirClave)

        if not usuario or not clave or not repetirClave or not nombres or not apellidos:
            messages.error(request, "Todos los campos son obligatorios")
            return render(request, "registrar.html")

        if clave != repetirClave:
            messages.error(request, "Las contraseñas no coinciden")
            return render(request,"registrar.html")
        
        if User.objects.filter(username=usuario).exists():
            messages.error(request, "El Usuario ya existe")
            return render(request,"registrar.html")
        
        User.objects.create_user(username=usuario,password=clave,first_name=nombres, last_name=apellidos)
        
    
        print(usuario, clave,repetirClave)
        return redirect("inicio_sesion")

    return render(request, "registrar.html")
     



@login_required
def finanzas(request):
    user = request.user

    # ----------------------------
    # 1️⃣ ÚLTIMOS 6 MESES (INGRESOS Y GASTOS)
    # ----------------------------
    today = timezone.localdate()
    month_labels = []
    series_ing = []
    series_gas = []

    for i in range(5, -1, -1):
        year = today.year
        month = today.month - i

        # Ajustar año si baja de enero
        while month <= 0:
            month += 12
            year -= 1

        start = date(year, month, 1)
        end = date(year, month, calendar.monthrange(year, month)[1])

        month_labels.append(start.strftime("%b %Y"))

        total_ing = Ingreso.objects.filter(
            usuario=user,
            creado__date__gte=start,
            creado__date__lte=end
        ).aggregate(
            total=Coalesce(Sum('cantidadIngresos'), Value(0), output_field=DecimalField())
        )["total"]

        total_gas = Gasto.objects.filter(
            usuario=user,
            creado__date__gte=start,
            creado__date__lte=end
        ).aggregate(
            total=Coalesce(Sum('cantidadGasto'), Value(0), output_field=DecimalField())
        )["total"]

        series_ing.append(float(total_ing))
        series_gas.append(float(total_gas))

    # ----------------------------
    # 2️⃣ GRÁFICO DE BARRAS
    # ----------------------------
    bar_chart_uri = None
    if any(series_ing) or any(series_gas):
        fig, ax = plt.subplots(figsize=(8, 4))
        x = range(len(month_labels))
        width = 0.35

        ax.bar([i - width/2 for i in x], series_ing, width, label="Ingresos")
        ax.bar([i + width/2 for i in x], series_gas, width, label="Gastos")

        ax.set_xticks(x)
        ax.set_xticklabels(month_labels, rotation=45)
        ax.set_ylabel("Montos")
        ax.legend()
        plt.tight_layout()

        buffer = io.BytesIO()
        fig.savefig(buffer, format='png')
        buffer.seek(0)
        bar_chart_uri = "data:image/png;base64," + base64.b64encode(buffer.read()).decode()

    # ----------------------------
    # 3️⃣ PIE: GASTOS POR CATEGORÍA
    # ----------------------------
    gastos_categoria = (
        Gasto.objects.filter(usuario=user)
        .values("categoria__nombre")
        .annotate(
            total=Coalesce(Sum("cantidadGasto"), Value(0), output_field=DecimalField())
        )
        .order_by("-total")
    )

    labels = [c["categoria__nombre"] or "Sin categoría" for c in gastos_categoria]
    values = [float(c["total"]) for c in gastos_categoria]

    pie_chart_uri = None
    if values:
        fig2, ax2 = plt.subplots(figsize=(5, 5))
        ax2.pie(values, labels=labels, autopct="%1.1f%%", startangle=90)
        ax2.axis("equal")
        plt.tight_layout()

        buf2 = io.BytesIO()
        fig2.savefig(buf2, format='png')
        buf2.seek(0)
        pie_chart_uri = "data:image/png;base64," + base64.b64encode(buf2.read()).decode()

    # ----------------------------
    # 4️⃣ TOTALES GENERALES
    # ----------------------------
    total_ingresos = Ingreso.objects.filter(usuario=user).aggregate(
        total=Coalesce(Sum('cantidadIngresos'), Value(0), output_field=DecimalField())
    )['total']

    total_gastos = Gasto.objects.filter(usuario=user).aggregate(
        total=Coalesce(Sum('cantidadGasto'), Value(0), output_field=DecimalField())
    )['total']

    balance = float(total_ingresos) - float(total_gastos)

    # ----------------------------
    # 5️⃣ CONTEXTO
    # ----------------------------
    context = {
        "pie_chart_uri": pie_chart_uri,
        "bar_chart_uri": bar_chart_uri,
        "total_ingresos": float(total_ingresos),
        "total_gastos": float(total_gastos),
        "balance": balance,
        "top_categorias": gastos_categoria[:5]
    }

    return render(request, "finanzas.html", context)


@login_required
def registrarIngreso(request):
    usuario = request.user


    categoria = Categoria.objects.filter(
        (Q(usuario=usuario) & Q(tipo='ingreso')) |
        (Q(usuario__isnull=True) & Q(tipo='ingreso'))
    ).order_by('-creado')

    if request.method == "POST":
        categoriaSeleccionada = request.POST.get('categoria')
        valor = request.POST.get('cantidadIngresos')
        categoria_obj = Categoria.objects.get(id=categoriaSeleccionada)
        accion = request.POST.get('Agregar')
        fecha = request.POST.get('fecha')
        print(fecha)
        if fecha:
            fecha= datetime.fromisoformat(fecha)
        else:
            fecha = timezone.now()

        if accion == 'guardar':

         Ingreso.objects.create(usuario=usuario,categoria=categoria_obj,cantidadIngresos=valor,creado=fecha)
         return redirect('finanzas')
        
        if accion == 'guardarMas':

            Ingreso.objects.create(usuario=usuario,categoria=categoria_obj,cantidadIngresos=valor,creado=fecha)
            return render(request,'agregarIngresos.html',{'categoria': categoria})
        if accion == 'cancelar':
            return redirect('finanzas')
        


    
    
    return render(request, 'agregarIngresos.html',{'categoria': categoria})

@login_required
def registrarGastos(request):
    usuario = request.user

    categoria = Categoria.objects.filter(
        Q(usuario=usuario) |
        (Q(usuario__isnull=True) & Q(tipo='gasto'))
    ).order_by('-creado')
    if request.method == "POST":
        categoriaSeleccionada = request.POST.get('categoria')
        valor = request.POST.get('cantidadGasto')
        categoria_obj = Categoria.objects.get(id=categoriaSeleccionada)
        accion = request.POST.get('Agregar')
        fecha = request.POST.get('fecha')
        


        if fecha:
            fecha= datetime.fromisoformat(fecha)
        else:
            fecha = timezone.now()

        if accion == 'guardar':

         Gasto.objects.create(usuario=usuario,categoria=categoria_obj,cantidadGasto=valor,creado=fecha)
         return redirect('finanzas')
        
        if accion == 'guardarMas':

            Gasto.objects.create(usuario=usuario,categoria=categoria_obj,cantidadGasto=valor,creado=fecha)
            return render(request,'agregarGastos.html')
        if accion == 'cancelar':
            return redirect('finanzas')

    
    
    return render(request, 'agregarGastos.html',{'categoria': categoria})

@login_required
def calificacion(request):
    usuario = request.user
    listValores= [1,2,3,4,5]

    if request.method == "POST":
        descripcion = request.POST.get('descripcion')
        calificacion = request.POST.get('calificacion')
        accion = request.POST.get('accion')

        if accion == 'cancelar':
            return redirect('finanzas')
        if not usuario or not descripcion or not calificacion:
            messages.error(request, "Todos los campos son obligatorios")
            return render(request, "registrarCalificacion.html")
        
        if accion=='agregar':

            u = Calificaciones(usuarioId=usuario.id,usuarioName=usuario.username, descripcion=descripcion,calificacion=calificacion)
            u.save()
            return redirect('finanzas')
    return render(request, 'registrarCalificacion.html',{'calificacion':listValores})


# views.py


class VerCalificacion(LoginRequiredMixin,ListView):
    template_name = "mostrarCalificaciones.html"
    context_object_name = "calificaciones"

    def get_queryset(self):
        return Calificaciones.objects.all()

    def post(self, request, *args, **kwargs):
        accion = request.POST.get('accion')
        if accion == 'regresar':
            return redirect('finanzas')
        return self.get(request, *args, **kwargs)

@login_required
def categoriaNueva(request):
    usuario = request.user

    listTipo=['ingreso','gasto']

    if request.method == "POST":
        nombreCat = request.POST.get('nuevaCat')
        descripcion = request.POST.get('descripcion')
        tipo = request.POST.get('tipo')

        accion = request.POST.get('Agregar')

        if accion == 'cancelar':
            return redirect('finanzas')
        if not nombreCat:
            messages.error(request, "El campo Nombre Categoria es obligatorio")

        if accion =='guardar':

            Categoria.objects.create(usuario=usuario,nombre=nombreCat,descripcion=descripcion,tipo=tipo)
            return redirect('finanzas')
        if accion == 'guardarMas':
            return render(request, 'agregarCategoria.html')

    return render(request, 'agregarCategoria.html',{'listTipo':listTipo})




