from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Categoria(models.Model):

    usuario = models.ForeignKey(User,on_delete=models.CASCADE,blank=True,null=True)
    nombre = models.CharField(max_length=200)
    descripcion = models.CharField(max_length=500 ,blank=True,null=True)

    TIPO_CHOICES = (
        ('ingreso', 'Ingreso'),
        ('gasto', 'Gasto'),
    )


    tipo = models.CharField(max_length=10,choices=TIPO_CHOICES)
    creado = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
      nombre = self.nombre if self.nombre else "Sin nombre"
      tipo = self.get_tipo_display() if self.tipo else "Sin tipo"
      return f"{nombre} ({tipo})"

class Gasto(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True)
    cantidadGasto = models.DecimalField(max_digits=36,decimal_places=2)
    creado = models.DateTimeField()

    def __str__(self):
        return f"{self.cantidadGasto} en {self.categoria}"
    

class Ingreso(models.Model):
    usuario = models.ForeignKey(User,on_delete=models.CASCADE)
    
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True)
    cantidadIngresos = models.DecimalField(max_digits=36,decimal_places=2)
    creado = models.DateTimeField()
    
    def __str__(self):
       return f"{self.cantidadIngresos} en {self.categoria}"

