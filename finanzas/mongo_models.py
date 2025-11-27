from mongoengine import Document, StringField, DateTimeField, FloatField,IntField



class Calificaciones(Document):
    usuarioId = IntField(requiered=True)
    usuarioName = StringField(requiered=True)
    descripcion = StringField(requiered=True)
    calificacion = StringField(requiered=True)
    creado = DateTimeField()